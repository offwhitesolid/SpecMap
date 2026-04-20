# Hierarchical State Compression Strategy (Format v3)

## 1. Overview and Objective
For exceedingly large configurations of `XYMap`, relying on a single global `gzip` compression (Format v2) encounters scaling inefficiencies, specifically when encountering vast domains of unmapped pixels (`np.nan`). Standard binary representations of `np.nan` under IEEE 754 don't yield optimal repeating bit-patterns for the DEFLATE compression algorithm.

This document outlines **Format v3**: a hierarchical compression implementation that segregates distinct large memory blocks, structurally normalizes `np.nan` into an optimal constant, compresses each object individually, and finally compresses the entire state dictionary.

Crucially, **backward compatibility** must be retained for `format_version=1` (uncompressed legacy) and `format_version=2` (single-layer unchunked/chunked GZIP).

## 2. Core Theoretical Optimizations

### A. Element-Wise NaN Replacement
`ROImask`, `HSI`, and the Derivative Data Cubes (`x * y * lambda`) often contain vast unused territories mapped entirely by `np.nan`.
*   **Theory**: Swapping spatial `np.nan` references to a dedicated repeating valid number (e.g., `-99999.0`) creates extremely long, unbroken streams of identical bytes. Binary compression engines (like GZIP) hyper-compress continuous identical values via Run-Length Encoding.
*   **Action**: Before serialization, iterate through large spatial sub-objects (`PMdict`, `roihandler.roilist`, data cubes) and map `np.isnan(array) -> -99999.0`. Store this mapping key.
*   **Implementation Details**:
    *   `_prepare_roilist_for_pickle(roilist)`: Iterate through all masks, convert to `np.ndarray`, identify all `np.nan`, replace with a dynamic `UNIQUE_NUM` calculated outside the bounds of existing valid array data (e.g., `min_val - 1000`). Record `{roi_name: UNIQUE_NUM}`.
    *   `_prepare_pmdict_for_pickle(pmdict)`: Deep copy `PMdict`. For each `PixelMatrix`, swap `np.nan` to a `UNIQUE_NUM` and record mapping.
*   **Benefit**: Compression engines map empty space to virtually zero file size. 

### B. Nested Sub-Object Compression (Hierarchical Zipping)
*   **Theory**: Rather than asking `gzip` to figure out the binary dictionary for everything at once, each large discrete object processes better against its own compression tree.
*   **Targeted Objects**:
    1.  `ROImask` (`roilist`)
    2.  `HSI Images` (`PMdict` and `PMclass` structures)
    3.  `Derivatives Cube Data`
    4.  `Averaged Spectra` (`disspecs`)
*   **Action**:
    *   Extract each element.
    *   Swap NaNs.
    *   Serialize and compress the item individually in memory: `compressed_obj = gzip.compress(pickle.dumps(obj))`
*   **Implementation Details**:
    *   Replace sequential file-writes with memory-based binary dumps: `gzip.compress(pickle.dumps(pmdict_prepared, protocol=pickle.HIGHEST_PROTOCOL))`.
    *   Do this for `pmdict_bytes`, `roilist_bytes`, `specs_bytes`, and `SpecDataMatrix_bytes`.
    *   Wrap these individual bytes objects inside the master `state` dictionary, and perform a final `gzip.open(filename, 'wb')` dump to disk.
*   **Benefit**: Drastically isolates object parsing. A failure or corruption in one array byte block won't break the extraction of native configurations. Loads balance into multi-threaded unzipping later if necessary.

---

## 3. Step-by-Step Implementation Flow

### Phase 1: Serialization Intercept (Save Logic)
1. **Initialize `save_state_v3`**:
    *   Define the global NaN replacement key (e.g., `NAN_KEY = -999999.0`).
2. **Sub-Component Processing**:
    *   **Derivatives / HSI Matrices**: For each item in `PMdict`, scan matrices, swap `np.nan` for `NAN_KEY`. Apply `gzip.compress` to the component yielding a byte stream (`pmdict_bytes`).
    *   **ROI Masks**: Iterate `roilist`, apply the same `NaN -> NAN_KEY` swap, output `roilist_bytes`.
    *   **Averaged Spectra**: Output `disspecs_bytes`.
3. **Global Assembly**:
    *   Construct the primary `state` dictionary consisting of GUI variables, parameters (`WL`, configurations), and the new `_bytes` sub-objects.
    *   Set `state['format_version'] = 3` and `state['nan_key'] = NAN_KEY`.
4. **Final Global Zipping**:
    *   Use `gzip.open(filename, 'wb')` to pickle and compress the global container to disk.

### Phase 2: Compatibility Pipeline (Load Logic)
1. **Header Sniffing**: 
    *   Check the first 2 bytes of the saved file for `\x1f\x8b` (GZIP signature).
    *   Open using `gzip.open` if positive, else use standard `open`.
2. **Format Routing**:
    *   `pickle.load(f)` the primary dictionary. Look up `state.get('format_version', 1)`.
    *   **Fallback (v1)**: Process as an uncompressed legacy file.
    *   **Fallback (v2)**: Process standard internal chunking.
3. **Reconstruction (v3)**:
    *   Extract the `NAN_KEY` from the loaded state.
    *   *Decompress the sub-elements*: `roilist = pickle.loads(gzip.decompress(state['roilist_bytes']))`.
    *   *Scan and Restore NaNs*: Iterate arrays and re-apply `np.nan` wherever the `NAN_KEY` is matched (`array[array == NAN_KEY] = np.nan`).
4. **Re-link Object Pointers**: Restore dynamic `WL` and global matrix pointer arrays across `XYMap` ensuring active RAM state matches perfectly.

---

## 4. Implementation Summary

### Task: Implement Hierarchical State Compression (Format v3)

#### For Save Logic (`save_state`)
1. **Import Requirements**: Require `import gzip` and `import io` at the top of the file.
2. **Nan Preparations**: 
   * Call `_prepare_pmdict_for_pickle(self.PMdict)` and `_prepare_roilist_for_pickle(roilist)` to convert all `np.nan` values inside matrices into fallback numeric values (`_nan_replacements`).
3. **Sub-Object Zipping**:
   * Instead of iteratively dumping `specs`, `SpecDataMatrix`, `PMdict`, and `roilist` via `_save_*_chunked`, convert these elements individually into compressed in-memory binary payloads:
     * `state['specs_bytes'] = gzip.compress(pickle.dumps(self.specs, protocol=pickle.HIGHEST_PROTOCOL))`
     * `state['matrix_bytes'] = gzip.compress(pickle.dumps(self.SpecDataMatrix, protocol=pickle.HIGHEST_PROTOCOL))`
     * `state['pmdict_bytes'] = gzip.compress(pickle.dumps(pmdict_prepared, protocol=pickle.HIGHEST_PROTOCOL))`
     * `state['roilist_bytes'] = gzip.compress(pickle.dumps(roilist_prepared, protocol=pickle.HIGHEST_PROTOCOL))`
4. **Primary State Construction**:
   * Wrap those binary fields alongside all other UI state strings, constants, floating parameters, and pointers (`WL`).
   * Explicitly set `state['format_version'] = 3` and inject `_nan_replacements`.
5. **Disk Write**:
   * Create output directories if needed. 
   * Execute a final `with gzip.open(filename, 'wb') as f:` and dump the entire master dictionary: `pickle.dump(state, f, protocol=pickle.HIGHEST_PROTOCOL)`.

#### For Load Logic (`load_state`)
1. **Magic Header Detection**: 
   * `read(2)` from `filename`. If it equals `\x1f\x8b`, utilize `gzip.open()`. Otherwise use standard `open()`.
2. **Master Dictionary Extraction**:
   * Standard `pickle.load` to unpack the primary loaded shell. Check `format_version`.
3. **Sub-Object Extraction (Version 3 Routing)**:
   * Perform sequential in-memory extractions:
     * `self.specs = pickle.loads(gzip.decompress(state['specs_bytes']))`
     * `self.SpecDataMatrix = pickle.loads(gzip.decompress(state['matrix_bytes']))`
     * `pmdict_loaded = pickle.loads(gzip.decompress(state['pmdict_bytes']))`
     * `roilist_loaded = pickle.loads(gzip.decompress(state['roilist_bytes']))`
   * Proceed to garbage collect (`gc.collect()`).
4. **Pointer Re-Mapping**:
   * Reassigned parsed `WL` arrays sequentially to internal components of `self.specs` and `self.SpecDataMatrix`.
5. **Nan Restoration**:
   * Check for `_nan_replacements_roilist` and `_nan_replacements` mapping. Read valid numbers back into standard `np.nan` blocks for `self.PMdict` and `self.roilist`.
6. **State Rebuild**:
   * Fallback on older versions (Format V2 chunked reads vs. Format V1 standard flat dictionaries). Sync all TK variable GUI variables accordingly.