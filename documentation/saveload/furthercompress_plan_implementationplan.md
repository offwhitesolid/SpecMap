# Exact Implementation Plan: Hierarchical State Compression (Format v3)

This document provides the exact code modifications required in `lib9.py` to implement the Format v3 compression strategy outlined in `furthercompress_plan.md`.

## 1. Imports
**Where:** Top of `lib9.py`
**Code to Validate/Add:**
```python
import gzip
import io
import gc
import pickle
```

## 2. Modifications to `save_state(self, filename)`
**Where:** inside class `XYMap` under `lib9.py`

**Current Code to Replace:**
```python
        # Create a dictionary with all important state (excluding large arrays)
        state = {
            # ...
            # NOTE: Large arrays (specs, SpecDataMatrix, PMdict) saved separately
            'format_version': 2,  # Version 2 = chunked format, Version 1 (implicit) = legacy format
            # ...
        }
        
        # Save to file with error handling and chunking
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(filename), exist_ok=True) if os.path.dirname(filename) else None
            
            with open(filename, 'wb') as f:
                # Save main state dictionary first
                pickle.dump(state, f, protocol=pickle.HIGHEST_PROTOCOL)
                
                # 1. Save specs list in chunks
                self._save_specs_chunked(f, self.specs)
                
                # 2. Save SpecDataMatrix in chunks
                self._save_matrix_chunked(f, self.SpecDataMatrix)
                
                # 3. Save PMdict in chunks
                self._save_pmdict_chunked(f, pmdict_prepared)
                
                # 4. Save ROI list
                pickle.dump(roilist_prepared, f, protocol=pickle.HIGHEST_PROTOCOL)
```

**New Code to Inject:**
```python
        # Create a dictionary with all important state
        state = {
            # ... keep existing core data ...
            'format_version': 3,  # Updated to Version 3
            # ... keep existing metadata ...
        }
        
        try:
            os.makedirs(os.path.dirname(filename), exist_ok=True) if os.path.dirname(filename) else None
            
            mem_tracker.log_memory("Starting gzip compression of sub-objects", context="save_state")
            
            # Compress large objects into memory bytes directly inside the state dictionary
            state['specs_bytes'] = gzip.compress(pickle.dumps(self.specs, protocol=pickle.HIGHEST_PROTOCOL))
            gc.collect()
            
            state['matrix_bytes'] = gzip.compress(pickle.dumps(self.SpecDataMatrix, protocol=pickle.HIGHEST_PROTOCOL))
            gc.collect()
            
            state['pmdict_bytes'] = gzip.compress(pickle.dumps(pmdict_prepared, protocol=pickle.HIGHEST_PROTOCOL))
            gc.collect()
            
            state['roilist_bytes'] = gzip.compress(pickle.dumps(roilist_prepared, protocol=pickle.HIGHEST_PROTOCOL))
            gc.collect()
            
            # Write the entire master state object out using a global gzip wrapper
            with gzip.open(filename, 'wb') as f:
                pickle.dump(state, f, protocol=pickle.HIGHEST_PROTOCOL)
```

## 3. Modifications to `load_state(self, filename)`
**Where:** inside class `XYMap` under `lib9.py`

**Current Code to Replace:**
```python
        try:
            with open(filename, 'rb') as f:
                # Load main state dictionary
                state = pickle.load(f)
                
                # Check format version (version 2 = chunked, version 1 or missing = legacy)
                format_version = state.get('format_version', 1)
                
                if format_version >= 2:
                    # Load large data structures in chunks (version 2+)
                    self.specs = self._load_specs_chunked(f)
                    self.SpecDataMatrix = self._load_matrix_chunked(f)
                    pmdict_loaded = self._load_pmdict_chunked(f)
                    roilist_loaded = pickle.load(f)
                else:
                    # Legacy format (version 1) - load from state dictionary
                    self.specs = state['specs']
                    self.SpecDataMatrix = state['SpecDataMatrix']
                    pmdict_loaded = state['PMdict']
                    roilist_loaded = state.get('roilist', {})
```

**New Code to Inject:**
```python
        try:
            # 1. Magic Byte Sniffing to determine if the outer shell is natively gzipped
            is_gzipped = False
            with open(filename, 'rb') as f_check:
                magic = f_check.read(2)
                if len(magic) >= 2 and magic[0] == 0x1f and magic[1] == 0x8b:
                    is_gzipped = True
                    
            open_func = gzip.open if is_gzipped else open
            
            # 2. Extract master state dictionary
            with open_func(filename, 'rb') as f:
                state = pickle.load(f)
                mem_tracker.log_memory("After loading main state", context="load_state")
                
                format_version = state.get('format_version', 1)
                
                # 3. Route extraction behavior based on Version target
                if format_version == 3:
                    # Version 3: Extract nested bytes payloads through gzip inversion
                    print("  - Loading format (version 3)")
                    self.specs = pickle.loads(gzip.decompress(state['specs_bytes']))
                    gc.collect()
                    
                    self.SpecDataMatrix = pickle.loads(gzip.decompress(state['matrix_bytes']))
                    gc.collect()
                    
                    pmdict_loaded = pickle.loads(gzip.decompress(state['pmdict_bytes']))
                    gc.collect()
                    
                    roilist_loaded = pickle.loads(gzip.decompress(state['roilist_bytes']))
                    gc.collect()
                    
                    # Explicitly remove binary nodes inside dict to free payload RAM
                    del state['specs_bytes'], state['matrix_bytes'], state['pmdict_bytes'], state['roilist_bytes']
                    gc.collect()
                    
                elif format_version == 2:
                    # Version 2: Standard uncompressed file chunked loading logic
                    print("  - Loading format (version 2)")
                    self.specs = self._load_specs_chunked(f)
                    gc.collect()
                    
                    self.SpecDataMatrix = self._load_matrix_chunked(f)
                    gc.collect()
                    
                    pmdict_loaded = self._load_pmdict_chunked(f)
                    gc.collect()
                    
                    roilist_loaded = pickle.load(f)
                    gc.collect()
                    
                else:
                    # Version 1 (Fallback): Load out of static flat dict
                    print("  - Loading legacy format (version 1)")
                    self.specs = state['specs']
                    self.SpecDataMatrix = state['SpecDataMatrix']
                    pmdict_loaded = state['PMdict']
                    roilist_loaded = state.get('roilist', {})
```

## 4. Why This Works
The subsequent processes corresponding to pointers handling inside `load_state`:
```python
# Restore WL arrays FIRST...
self.WL = state['WL']
# ... NaN replacement restoration
self.PMdict = self._restore_nan_in_pmdict(pmdict_loaded, nan_replacements)
```
...remain **100% physically identical**, as the output instances resolved inside the format version pathways yield the identical structural typing needed for trailing state reconstruction. No extra code editing is required past extracting the actual formats array variables!