"""
FastestUp – Lightweight Hyperspectral Image (HSI) Creator
==========================================================
A minimal tkinter GUI for generating a Hyperspectral Image (HSI)
from raw spectrometer data files very quickly.

Processing pipeline
-------------------
1. Load spectra files from a folder (filename pattern + extension filter).
2. Read the shared Wavelength (WL) axis and Background (BG) from the first
   valid file; optionally flatten the BG to its mean (Linear BG mode).
3. Compute PLB = PL − BG for every pixel.
4. Optionally remove cosmic rays using the combined
   "Linear Interpolation + Nearest-Neighbour Average" algorithm.
5. Integrate (sum) PLB over the chosen wavelength window [wl_start, wl_end].
6. Arrange the integrated values into a 2-D pixel matrix and display the
   resulting HSI with matplotlib (use the toolbar's Save button to export).

No derivative calculation, no spectrum averaging, and no pickle saving are
performed – this is intentionally kept as simple and fast as possible.
"""

import sys
import os

# ── resolve SpecMap root so we can import deflib1 ──────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SPECMAP_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..'))
if SPECMAP_DIR not in sys.path:
    sys.path.insert(0, SPECMAP_DIR)

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import numpy as np
import matplotlib.pyplot as plt

try:
    import deflib1 as deflib
    _DEFLIB_AVAILABLE = True
except ImportError:
    _DEFLIB_AVAILABLE = False

# ── defaults ────────────────────────────────────────────────────────────────
DEFAULTS_FILE = os.path.join(SCRIPT_DIR, 'defaults.txt')

DEFAULTS = {
    'data_folder':      '',
    'filename':         'spectrum',
    'file_extension':   '.txt',
    'linear_bg':        True,
    'remove_cosmics':   True,
    'cosmic_method':    'Linear + Neighbor (Combined)',
    'cosmic_threshold': 100,
    'cosmic_width':     10,
    'wl_start':         500.0,
    'wl_end':           700.0,
    'count_threshold':  0,
    'colormap':         'hot',
}

_DEFAULTTYPES = {
    'data_folder':      str,
    'filename':         str,
    'file_extension':   str,
    'linear_bg':        bool,
    'remove_cosmics':   bool,
    'cosmic_method':    str,
    'cosmic_threshold': int,
    'cosmic_width':     int,
    'wl_start':         float,
    'wl_end':           float,
    'count_threshold':  float,
    'colormap':         str,
}


def load_defaults():
    """Load default values from defaults.txt."""
    variables = {}
    if os.path.exists(DEFAULTS_FILE):
        with open(DEFAULTS_FILE, 'r') as file:
            for line in file:
                if '=' in line:
                    name, value = line.split('=', 1)
                    name = name.strip()
                    value = value.strip()
                    if value.isdigit():
                        value = int(value)
                    elif value.replace('.', '', 1).isdigit():
                        value = float(value)
                    elif value.lower() in ('true', 'false'):
                        value = value.lower() == 'true'
                    variables[name] = value
    return variables


def save_defaults(variables):
    """Save default values to defaults.txt."""
    with open(DEFAULTS_FILE, 'w') as file:
        for name, value in variables.items():
            file.write(f'{name} = {value}\n')


def initdefaults():
    """Load defaults from file, falling back to hardcoded values."""
    loadeddefaults = load_defaults()
    reqdefaults = DEFAULTS.copy()
    for i in loadeddefaults.keys():
        if i not in _DEFAULTTYPES:
            continue
        try:
            reqdefaults[i] = _DEFAULTTYPES[i](loadeddefaults[i])
        except Exception as error:
            if loadeddefaults[i] == 'None':
                pass
            else:
                print(f'[FastestUp] Error: {error} while loading entry '
                      f'{i!r}. Using default: {reqdefaults[i]}')
    return reqdefaults


DEFAULTS = initdefaults()

# Metadata keys whose values should be converted to float
_FLOAT_KEYS = {
    'x-position', 'y-position', 'z-position',
    'Delta Wavelength (nm)',
    'Exposure Time (s)',
    'Central Wavelength (nm)',
}

# Whitelist of cosmic-removal methods supplied by deflib1
# Falls back to a simple linear-only implementation when deflib is absent.
_COSMIC_METHODS = ['Linear + Neighbor (Combined)', 'Linear Interpolation',
                   'Nearest Neighbor average']

# ── pure-python fallback cosmic removal (used when deflib1 is unavailable) ──
def _remove_cosmics_linear_fallback(data, thresh, width):
    """Simple linear-interpolation cosmic removal (no scipy dependency)."""
    data = np.asarray(data, dtype=np.float32)
    diff = np.diff(data)
    corrected = data.copy()
    for start in np.where(np.abs(diff) > thresh)[0]:
        end_range = min(int(start) + int(width), len(data) - 1)
        for end in range(int(start) + 1, end_range + 1):
            if np.abs(data[end] - data[start]) < thresh:
                corrected[start:end + 1] = np.linspace(
                    data[start], data[end], end - start + 1)
                break
    return corrected


def _apply_cosmic_removal(plb, method, threshold, width):
    """Apply the chosen cosmic-removal algorithm to a 1-D PLB array."""
    if _DEFLIB_AVAILABLE and method in deflib.cosmicfuncts:
        try:
            return np.asarray(
                deflib.cosmicfuncts[method](plb, threshold, width),
                dtype=np.float32)
        except Exception as exc:
            print(f'[FastestUp] Cosmic removal ({method}) failed: {exc}')
    # fallback
    return _remove_cosmics_linear_fallback(plb, threshold, width)


# ── lightweight file reader ──────────────────────────────────────────────────
_READ_KEYS = {'BG', 'PL'}

def _read_wl_bg(filepath):
    """
    Read the shared Wavelength (WL) axis and the Background (BG) column from
    *filepath*.  Returns (wl_list, bg_list) on success, (None, None) on error.
    """
    wl, bg = [], []
    reading = False
    try:
        with open(filepath, 'r', errors='replace') as fh:
            for line in fh:
                if '\t' in line:
                    parts = line.split()
                    if not reading:
                        if len(parts) >= 2 and any(k in parts for k in _READ_KEYS):
                            reading = True
                    else:
                        try:
                            wl.append(float(parts[0]))
                            bg.append(float(parts[1]))
                        except (IndexError, ValueError):
                            pass
    except OSError as exc:
        print(f'[FastestUp] Cannot open {filepath}: {exc}')
        return None, None
    return (wl, bg) if wl else (None, None)


def _read_spectrum(filepath, WL_len):
    """
    Read one spectrum file.  Returns a dict with keys
    ``'x'``, ``'y'`` and ``'PL'`` (numpy float32 array of length WL_len),
    or *None* on failure.
    """
    data_meta = {}
    pl = []
    reading = False
    try:
        with open(filepath, 'r', errors='replace') as fh:
            for line in fh:
                if ':' in line and '\t' not in line:
                    key, _, value = line.partition(':')
                    key   = key.strip()
                    value = value.strip()
                    if key in _FLOAT_KEYS:
                        try:
                            data_meta[key] = float(value)
                        except ValueError:
                            data_meta[key] = value
                    else:
                        data_meta[key] = value
                elif '\t' in line:
                    parts = line.split()
                    if not reading:
                        if len(parts) >= 2 and any(k in parts for k in _READ_KEYS):
                            reading = True
                    else:
                        try:
                            pl.append(float(parts[2]))
                        except (IndexError, ValueError):
                            pass
    except OSError as exc:
        print(f'[FastestUp] Cannot read {filepath}: {exc}')
        return None

    if len(pl) != WL_len:
        return None  # mismatched length – skip

    return {
        'x':  float(data_meta.get('x-position', 0.0)),
        'y':  float(data_meta.get('y-position', 0.0)),
        'PL': np.array(pl, dtype=np.float32),
    }


# ── core processing ──────────────────────────────────────────────────────────

def build_hsi(files, linear_bg, remove_cosmics, cosmic_method,
              cosmic_threshold, cosmic_width, wl_start, wl_end,
              count_threshold, status_cb=None):
    """
    Build a 2-D HSI pixel matrix from *files*.

    Parameters
    ----------
    files            : list[str] – sorted list of spectrum file paths
    linear_bg        : bool  – if True, flatten BG to its mean before subtraction
    remove_cosmics   : bool  – apply cosmic-ray removal to each PLB spectrum
    cosmic_method    : str   – key into deflib.cosmicfuncts
    cosmic_threshold : float – threshold for cosmic detection
    cosmic_width     : int   – window width for cosmic removal
    wl_start         : float – integration start wavelength (nm)
    wl_end           : float – integration end wavelength (nm)
    count_threshold  : float – pixels whose integrated intensity is below this
                               value are set to NaN
    status_cb        : callable(str) | None – optional progress callback

    Returns
    -------
    pixel_matrix : 2-D numpy array  (rows = Y, cols = X)
    wl           : 1-D numpy array  wavelength axis
    x_axis       : 1-D numpy array  unique sorted X positions
    y_axis       : 1-D numpy array  unique sorted Y positions
    wl_start_used: float
    wl_end_used  : float
    """
    if not files:
        raise ValueError('No files provided.')

    def _status(msg):
        print(f'[FastestUp] {msg}')
        if status_cb:
            status_cb(msg)

    # ── 1. read WL + BG once ────────────────────────────────────────────────
    _status('Reading WL / BG axis …')
    wl_list, bg_list = None, None
    for f in files:
        wl_list, bg_list = _read_wl_bg(f)
        if wl_list:
            break
    if not wl_list:
        raise RuntimeError('Could not read WL axis from any file.')

    WL = np.array(wl_list, dtype=np.float32)
    BG = np.array(bg_list, dtype=np.float32)

    if linear_bg:
        BG[:] = np.mean(BG)          # flatten to mean → "linear" background

    # ── 2. determine integration pixel window ───────────────────────────────
    aq_start = int(np.searchsorted(WL, wl_start, side='left'))
    aq_end   = int(np.searchsorted(WL, wl_end,   side='right'))
    aq_start = max(0, min(aq_start, len(WL) - 1))
    aq_end   = max(aq_start + 1, min(aq_end, len(WL)))

    wl_start_used = float(WL[aq_start])
    wl_end_used   = float(WL[aq_end - 1])

    # ── 3. read & process every spectrum ────────────────────────────────────
    _status(f'Loading {len(files)} spectra …')
    pixel_data = []          # list of (x, y, intensity)

    for idx, fpath in enumerate(files):
        rec = _read_spectrum(fpath, len(WL))
        if rec is None:
            continue

        PLB = rec['PL'] - BG

        if remove_cosmics:
            PLB = _apply_cosmic_removal(
                PLB, cosmic_method, cosmic_threshold, cosmic_width)

        intensity = float(np.sum(PLB[aq_start:aq_end]))
        pixel_data.append((rec['x'], rec['y'], intensity))

        if (idx + 1) % max(1, len(files) // 10) == 0:
            _status(f'  processed {idx + 1}/{len(files)} spectra …')

    if not pixel_data:
        raise RuntimeError('No valid spectra found in the selected folder.')

    # ── 4. arrange into 2-D matrix ──────────────────────────────────────────
    _status('Building pixel matrix …')
    xs = sorted(set(p[0] for p in pixel_data))
    ys = sorted(set(p[1] for p in pixel_data))

    x_idx = {v: i for i, v in enumerate(xs)}
    y_idx = {v: i for i, v in enumerate(ys)}

    pixel_matrix = np.full((len(ys), len(xs)), np.nan, dtype=np.float64)
    for x, y, val in pixel_data:
        pixel_matrix[y_idx[y], x_idx[x]] = val

    # apply count threshold
    if count_threshold > 0:
        pixel_matrix[pixel_matrix < count_threshold] = np.nan

    _status('Done.')
    return (pixel_matrix,
            WL,
            np.array(xs, dtype=np.float64),
            np.array(ys, dtype=np.float64),
            wl_start_used,
            wl_end_used)


# ── GUI ──────────────────────────────────────────────────────────────────────

class FastestUpApp:
    """Lightweight tkinter application for fast HSI generation."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title('FastestUp – Lightweight HSI Creator')
        self.root.resizable(True, True)

        self._build_gui()

    # ── GUI construction ────────────────────────────────────────────────────

    def _build_gui(self):
        # ---------- top-level layout ----------------------------------------
        main = tk.Frame(self.root, padx=8, pady=8)
        main.pack(fill=tk.BOTH, expand=True)

        # ---------- File input frame ----------------------------------------
        file_frame = tk.LabelFrame(main, text='Data Input', padx=6, pady=6)
        file_frame.pack(fill=tk.X, pady=(0, 6))

        tk.Label(file_frame, text='Data Folder:').grid(
            row=0, column=0, sticky='w')
        self._folder_var = tk.StringVar(value=DEFAULTS['data_folder'])
        tk.Entry(file_frame, textvariable=self._folder_var, width=60).grid(
            row=0, column=1, sticky='ew', padx=(4, 4))
        tk.Button(file_frame, text='Browse …',
                  command=self._browse_folder).grid(row=0, column=2)

        tk.Label(file_frame, text='Filename pattern:').grid(
            row=1, column=0, sticky='w')
        self._fname_var = tk.StringVar(value=DEFAULTS['filename'])
        tk.Entry(file_frame, textvariable=self._fname_var, width=30).grid(
            row=1, column=1, sticky='w', padx=(4, 4))

        tk.Label(file_frame, text='File extension:').grid(
            row=2, column=0, sticky='w')
        self._fext_var = tk.StringVar(value=DEFAULTS['file_extension'])
        tk.Entry(file_frame, textvariable=self._fext_var, width=15).grid(
            row=2, column=1, sticky='w', padx=(4, 4))

        file_frame.columnconfigure(1, weight=1)

        # ---------- Processing options frame --------------------------------
        proc_frame = tk.LabelFrame(main, text='Processing Options',
                                   padx=6, pady=6)
        proc_frame.pack(fill=tk.X, pady=(0, 6))

        # BG correction
        bg_sub = tk.LabelFrame(proc_frame, text='Background Correction',
                               padx=4, pady=4)
        bg_sub.grid(row=0, column=0, sticky='nsew', padx=(0, 8))

        self._linear_bg_var = tk.BooleanVar(value=DEFAULTS['linear_bg'])
        tk.Checkbutton(bg_sub, text='Linear Background\n(average BG)',
                       variable=self._linear_bg_var).pack(anchor='w')

        # Cosmic removal
        cos_sub = tk.LabelFrame(proc_frame, text='Cosmic Ray Removal',
                                padx=4, pady=4)
        cos_sub.grid(row=0, column=1, sticky='nsew')

        self._rem_cos_var = tk.BooleanVar(value=DEFAULTS['remove_cosmics'])
        tk.Checkbutton(cos_sub, text='Remove Cosmic Rays',
                       variable=self._rem_cos_var).grid(
            row=0, column=0, columnspan=2, sticky='w')

        tk.Label(cos_sub, text='Method:').grid(row=1, column=0, sticky='w')
        self._cos_method_var = tk.StringVar(value=DEFAULTS['cosmic_method'])
        method_combo = ttk.Combobox(cos_sub, textvariable=self._cos_method_var,
                                    values=_COSMIC_METHODS, width=30,
                                    state='readonly')
        method_combo.grid(row=1, column=1, sticky='w', padx=(4, 0))

        tk.Label(cos_sub, text='Threshold:').grid(row=2, column=0, sticky='w')
        self._cos_thresh_var = tk.StringVar(
            value=str(DEFAULTS['cosmic_threshold']))
        tk.Entry(cos_sub, textvariable=self._cos_thresh_var,
                 width=10).grid(row=2, column=1, sticky='w', padx=(4, 0))

        tk.Label(cos_sub, text='Width:').grid(row=3, column=0, sticky='w')
        self._cos_width_var = tk.StringVar(
            value=str(DEFAULTS['cosmic_width']))
        tk.Entry(cos_sub, textvariable=self._cos_width_var,
                 width=10).grid(row=3, column=1, sticky='w', padx=(4, 0))

        proc_frame.columnconfigure(0, weight=1)
        proc_frame.columnconfigure(1, weight=1)

        # ---------- Wavelength / display frame ------------------------------
        wl_frame = tk.LabelFrame(main, text='Wavelength Range & Display',
                                 padx=6, pady=6)
        wl_frame.pack(fill=tk.X, pady=(0, 6))

        tk.Label(wl_frame, text='Start wavelength (nm):').grid(
            row=0, column=0, sticky='w')
        self._wl_start_var = tk.StringVar(value=str(DEFAULTS['wl_start']))
        tk.Entry(wl_frame, textvariable=self._wl_start_var,
                 width=12).grid(row=0, column=1, sticky='w', padx=(4, 20))

        tk.Label(wl_frame, text='End wavelength (nm):').grid(
            row=0, column=2, sticky='w')
        self._wl_end_var = tk.StringVar(value=str(DEFAULTS['wl_end']))
        tk.Entry(wl_frame, textvariable=self._wl_end_var,
                 width=12).grid(row=0, column=3, sticky='w', padx=(4, 20))

        tk.Label(wl_frame, text='Count threshold:').grid(
            row=1, column=0, sticky='w')
        self._thresh_var = tk.StringVar(
            value=str(DEFAULTS['count_threshold']))
        tk.Entry(wl_frame, textvariable=self._thresh_var,
                 width=12).grid(row=1, column=1, sticky='w', padx=(4, 20))

        tk.Label(wl_frame, text='Colormap:').grid(
            row=1, column=2, sticky='w')
        self._cmap_var = tk.StringVar(value=DEFAULTS['colormap'])
        cmap_combo = ttk.Combobox(
            wl_frame, textvariable=self._cmap_var,
            values=['hot', 'viridis', 'plasma', 'inferno', 'magma',
                    'cividis', 'gray', 'jet', 'rainbow'],
            width=12, state='readonly')
        cmap_combo.grid(row=1, column=3, sticky='w', padx=(4, 0))

        # ---------- Action buttons ------------------------------------------
        btn_frame = tk.Frame(main)
        btn_frame.pack(fill=tk.X, pady=(0, 4))

        tk.Button(btn_frame, text='Create HSI',
                  font=('Arial', 10, 'bold'),
                  bg='#4CAF50', fg='white',
                  command=self._create_hsi).pack(side=tk.LEFT, padx=(0, 10))

        # ---------- Status bar ----------------------------------------------
        self._status_var = tk.StringVar(value='Ready.')
        tk.Label(main, textvariable=self._status_var,
                 anchor='w', relief='sunken').pack(
            fill=tk.X, side=tk.BOTTOM, pady=(4, 0))

    # ── callbacks ───────────────────────────────────────────────────────────

    def _browse_folder(self):
        folder = filedialog.askdirectory(title='Select data folder')
        if folder:
            self._folder_var.set(folder)

    def _set_status(self, msg: str):
        self._status_var.set(msg)
        self.root.update_idletasks()

    def _collect_files(self):
        """Walk folder, return sorted list of matching files."""
        folder   = self._folder_var.get().strip()
        pattern  = self._fname_var.get().strip()
        ext      = self._fext_var.get().strip()
        if not folder:
            messagebox.showerror('Error', 'Please select a data folder.')
            return []
        files = []
        for root_dir, _, filenames in os.walk(folder):
            for fn in filenames:
                if pattern in fn and fn.endswith(ext):
                    files.append(os.path.join(root_dir, fn))
        files.sort()
        return files

    def _parse_float(self, var: tk.StringVar, name: str, default: float):
        try:
            return float(var.get())
        except ValueError:
            print(
                'Warning',
                f'Invalid value for {name}, using default ({default}).')
            return default

    def _parse_int(self, var: tk.StringVar, name: str, default: int):
        try:
            return int(var.get())
        except ValueError:
            print(
                'Warning',
                f'Invalid value for {name}, using default ({default}).')
            return default

    def _create_hsi(self):
        files = self._collect_files()
        if not files:
            print(
                'No files',
                'No matching files found.\n'
                'Check the folder, filename pattern and extension.')
            return

        self._set_status(f'Found {len(files)} file(s) – processing …')

        # collect parameters
        linear_bg        = self._linear_bg_var.get()
        remove_cosmics   = self._rem_cos_var.get()
        cosmic_method    = self._cos_method_var.get()
        cosmic_threshold = self._parse_float(
            self._cos_thresh_var, 'Cosmic threshold',
            DEFAULTS['cosmic_threshold'])
        cosmic_width     = self._parse_int(
            self._cos_width_var, 'Cosmic width',
            DEFAULTS['cosmic_width'])
        wl_start         = self._parse_float(
            self._wl_start_var, 'Start wavelength', DEFAULTS['wl_start'])
        wl_end           = self._parse_float(
            self._wl_end_var, 'End wavelength', DEFAULTS['wl_end'])
        count_threshold  = self._parse_float(
            self._thresh_var, 'Count threshold', DEFAULTS['count_threshold'])
        colormap         = self._cmap_var.get()

        try:
            (pixel_matrix,
             WL,
             x_axis,
             y_axis,
             wl_start_used,
             wl_end_used) = build_hsi(
                files=files,
                linear_bg=linear_bg,
                remove_cosmics=remove_cosmics,
                cosmic_method=cosmic_method,
                cosmic_threshold=cosmic_threshold,
                cosmic_width=cosmic_width,
                wl_start=wl_start,
                wl_end=wl_end,
                count_threshold=count_threshold,
                status_cb=self._set_status,
            )
        except Exception as exc:
            messagebox.showerror('Processing error', str(exc))
            self._set_status(f'Error: {exc}')
            return

        # ── plot ─────────────────────────────────────────────────────────────
        fig, ax = plt.subplots(figsize=(6, 5))

        im = ax.imshow(
            pixel_matrix,
            cmap=colormap,
            aspect='auto',
            origin='lower',
            extent=[float(x_axis[0]),  float(x_axis[-1]),
                    float(y_axis[0]),  float(y_axis[-1])]
            if len(x_axis) > 1 and len(y_axis) > 1
            else None,
        )

        cbar = fig.colorbar(im, ax=ax)
        cbar.set_label('Integrated counts', fontsize=10)

        ax.set_title(
            f'HSI: {wl_start_used:.1f} – {wl_end_used:.1f} nm'
            f'  ({len(files)} pixels)',
            fontsize=10)
        ax.set_xlabel('X position (µm)', fontsize=9)
        ax.set_ylabel('Y position (µm)', fontsize=9)

        fig.tight_layout()
        plt.show()

        self._set_status(
            f'HSI created: {pixel_matrix.shape[1]}×{pixel_matrix.shape[0]}'
            f' pixels  |  {wl_start_used:.1f}–{wl_end_used:.1f} nm  '
            f'|  use the toolbar to save the image.')


# ── entry point ───────────────────────────────────────────────────────────────

def main():
    root = tk.Tk()
    root.geometry('900x600')
    FastestUpApp(root)
    root.protocol('WM_DELETE_WINDOW', root.destroy)
    root.mainloop()


if __name__ == '__main__':
    main()
