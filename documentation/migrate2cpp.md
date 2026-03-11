# SpecMap → C++ Migration Plan

## Overview

This document outlines a step-by-step migration of the SpecMap Python application to C++.
The goal is a thread-safe, memory-safe implementation with **FLTK** as the GUI frontend.

The Python source analyzed is `main9.py` and all libraries it imports directly or transitively.

---

## 1. Python Library → C++ Concept Mapping

### 1.1 `tkinter` / `tkinter.ttk` → **FLTK**

| Python (tkinter)              | C++ (FLTK)                                  |
|-------------------------------|---------------------------------------------|
| `tk.Tk()` root window         | `Fl_Window` (or `Fl_Double_Window`)         |
| `ttk.Notebook`                | `Fl_Tabs` + `Fl_Group` per tab              |
| `tk.Frame`                    | `Fl_Group`                                  |
| `tk.Canvas` + scrollbars      | `Fl_Scroll` containing an `Fl_Group`        |
| `tk.Label`                    | `Fl_Box` (with label)                       |
| `tk.Button`                   | `Fl_Button`                                 |
| `tk.Entry`                    | `Fl_Input`                                  |
| `ttk.Combobox`                | `Fl_Choice`                                 |
| `tk.Checkbutton`              | `Fl_Check_Button`                           |
| `filedialog.askopenfilename`  | `fl_file_chooser()` / `Fl_Native_File_Chooser` |
| `messagebox.showerror`        | `fl_alert()` / `fl_message()`              |
| `tk.Menu` / `tk.Menu.add_*`   | `Fl_Menu_Bar` + `Fl_Menu_Item[]`            |
| `widget.pack()` / `.grid()`   | `widget->position(x, y)` + `widget->size(w, h)` or `Fl_Pack` / `Fl_Grid` |
| `root.after(ms, callback)`    | `Fl::add_timeout(sec, cb, data)`            |
| `threading` callbacks to GUI  | `Fl::awake(cb, data)` from worker threads   |

**Key design rule:** FLTK is single-threaded for its event loop. All GUI updates from worker
threads must go through `Fl::awake()` or `Fl::lock()` / `Fl::unlock()`.

---

### 1.2 `matplotlib` → **ImGui + ImPlot** (or **Matplot++ / gnuplot-cpp**)

| Python (matplotlib)               | C++ Recommendation                                      |
|-----------------------------------|---------------------------------------------------------|
| `Figure`, `Axes`                  | `ImPlot::BeginPlot()` context                           |
| `plt.plot()` / `ax.plot()`        | `ImPlot::PlotLine()`                                    |
| `imshow()` (for HSI colormap)     | `ImPlot::PlotHeatmap()` or custom `Fl_RGB_Image`        |
| `FigureCanvasTkAgg`               | Embed ImGui/ImPlot inside an `Fl_Gl_Window`             |
| `NavigationToolbar2Tk`            | Custom FLTK toolbar with zoom/pan buttons               |
| `matplotlib.patches.Rectangle`   | `ImPlot::PlotRectX()` or custom draw call               |
| `matplotlib.widgets.Cursor`       | Custom mouse-move handler on the plot widget            |
| `matplotlib.widgets.Button`       | `Fl_Button` overlaying the plot area                    |
| `matplotlib.ticker.AutoLocator`   | ImPlot handles tick placement automatically             |
| `matplotlib.colors` / colormaps   | ImPlot built-in colormaps, or custom LUT arrays         |

**Alternative for static/export plots:** link `matplotlib-cpp` (header-only Python C API bridge)
as a transitional step until the ImGui/ImPlot layer is complete.

---

### 1.3 `numpy` → **Eigen** (linear algebra) + **xtensor** or raw `std::vector`

| Python (numpy)                        | C++ Recommendation                              |
|---------------------------------------|-------------------------------------------------|
| `np.array([...], dtype=float64)`      | `Eigen::MatrixXd` / `std::vector<double>`       |
| `np.zeros((m, n))` / `np.ones(...)`   | `Eigen::MatrixXd::Zero(m, n)`                   |
| 3-D HSI cube `[y, x, wl]`            | `xtensor` rank-3 tensor or flat `std::vector` with index helper |
| `np.mean()`, `np.std()`              | Eigen `.mean()` / custom reduction              |
| Array slicing `a[i, :, :]`           | Eigen block operations / xtensor views          |
| `np.exp()`, `np.sqrt()` element-wise | Eigen `array()` expressions / `<cmath>` loops  |
| `np.isnan()` / `np.isinf()`          | `std::isnan()` / `std::isinf()` with loops      |
| Broadcasting                          | Eigen broadcasting or explicit loops            |

---

### 1.4 `scipy` → **Eigen** + custom implementations + **Ceres / GSL**

| Python (scipy)                            | C++ Recommendation                                           |
|-------------------------------------------|--------------------------------------------------------------|
| `scipy.optimize.curve_fit`               | **Ceres Solver** (non-linear least squares) or **GSL** `gsl_multifit_nlinear` |
| `scipy.optimize.fminbound`               | Ceres / custom Brent method (`boost::math::tools::brent_find_minima`) |
| `scipy.optimize.minimize`                | Ceres or **NLopt**                                           |
| `scipy.special.wofz` (Faddeeva/Voigt)   | **libcerf** or the MIT Faddeeva package (header-only C)       |
| `scipy.special.jv` (Bessel functions)   | `boost::math::cyl_bessel_j()` or GSL `gsl_sf_bessel_Jn`     |
| `scipy.ndimage.median_filter`            | Custom O(n log n) sliding-window median or OpenCV `medianBlur` |
| `scipy.ndimage.gaussian_filter1d`        | OpenCV `GaussianBlur` (1-D projection) or custom kernel      |
| `scipy.signal.find_peaks`               | Custom peak-finding algorithm (compare neighbors + threshold) |
| `scipy.signal.savgol_filter`             | Custom Savitzky–Golay filter (solve Vandermonde system once) |
| `scipy.signal.hilbert`                   | FFTW-based Hilbert transform via `fftwf_plan_dft_r2c`        |
| `scipy.interpolate.UnivariateSpline`     | **GSL** cubic spline or **Eigen** polynomial interpolation   |

---

### 1.5 `PIL` (Pillow) → **stb_image** + **stb_image_write** (or libpng/libjpeg)

| Python (PIL)                  | C++ Recommendation                                      |
|-------------------------------|---------------------------------------------------------|
| `Image.open(path)`            | `stbi_load()` → `unsigned char*` buffer                |
| `Image.fromarray(nparray)`    | Copy Eigen matrix → raw buffer → `Fl_RGB_Image`        |
| `ImageTk.PhotoImage`          | `Fl_RGB_Image` displayed in `Fl_Box`                   |
| `image.save(path)`            | `stbi_write_png()` / `stbi_write_jpg()`                |
| `image.resize()`              | `stbir_resize_uint8()` (stb_image_resize)              |

---

### 1.6 `pickle` → **cereal** (header-only C++ serialization)

| Python (pickle)               | C++ Recommendation                                     |
|-------------------------------|--------------------------------------------------------|
| `pickle.dump(obj, f)`         | `cereal::BinaryOutputArchive` to `std::ofstream`       |
| `pickle.load(f)`              | `cereal::BinaryInputArchive` from `std::ifstream`      |
| Arbitrary object graph        | Define `serialize()` method on each class for cereal   |
| Versioned data                | Add a `version` field and handle migration in load     |

**Alternative:** Protobuf or MessagePack if cross-language compatibility is needed.

---

### 1.7 `threading` / `concurrent.futures` → **`std::thread`** + **`std::mutex`** + **`std::atomic`**

| Python                                    | C++                                                          |
|-------------------------------------------|--------------------------------------------------------------|
| `threading.Thread(target=f)`              | `std::thread t(f);`                                          |
| `threading.Event` (stop flag)             | `std::atomic<bool> stop_flag{false};`                        |
| `thread.join(timeout=0.5)`                | `t.join()` with a `std::future` + `wait_for(500ms)`         |
| `ThreadPoolExecutor(max_workers=n)`       | Custom thread pool or **BS::thread_pool** (header-only)      |
| `as_completed(futures)`                   | `std::future::get()` in a results loop                       |
| `threading.enumerate()`                   | Track all `std::thread` objects in a `std::vector<std::thread>` |
| GUI callback from worker thread           | `Fl::awake(callback, data)` (FLTK thread-safe callback)      |

**Thread-safety rules:**
- All HSI data arrays must be protected by `std::shared_mutex` (readers–writer lock).
- GUI updates must only occur on the FLTK main thread via `Fl::awake()`.
- Use `std::atomic<bool>` cancellation tokens instead of Python `Event`.

---

### 1.8 `os` / `sys` / `shutil` / `gc` → **`<filesystem>`** (C++17)

| Python                            | C++                                              |
|-----------------------------------|--------------------------------------------------|
| `os.path.join(a, b)`              | `std::filesystem::path(a) / b`                   |
| `os.path.exists(p)`               | `std::filesystem::exists(p)`                     |
| `os.walk(folder)`                 | `std::filesystem::recursive_directory_iterator`  |
| `os.listdir(dir)`                 | `std::filesystem::directory_iterator`            |
| `shutil.copy(src, dst)`           | `std::filesystem::copy(src, dst)`                |
| `gc.collect()`                    | Deterministic RAII; use `std::unique_ptr` / RAII |
| `sys.exit()`                      | `std::exit()` or graceful shutdown via flag      |

---

### 1.9 `pandas` → **Custom data structures** or **Arrow C++ / CSV parser**

| Python (pandas)                   | C++ Recommendation                                     |
|-----------------------------------|--------------------------------------------------------|
| `pd.DataFrame`                    | Custom struct/class + `std::vector<std::vector<T>>`   |
| `df.to_csv()`                     | Custom CSV writer or **fast-cpp-csv-parser**           |
| `pd.read_csv()`                   | **fast-cpp-csv-parser** (header-only) or libcsv        |
| Column-wise operations            | Eigen column vectors; or Arrow C++ chunked arrays      |

---

### 1.10 `json` → **nlohmann/json** (header-only)

| Python (json)                 | C++ (nlohmann/json)                             |
|-------------------------------|-------------------------------------------------|
| `json.dump(obj, f)`           | `nlohmann::json j = obj; f << j;`              |
| `json.load(f)`                | `nlohmann::json j; f >> j; auto v = j["key"];` |

---

### 1.11 `logging` → **spdlog** (header-only, fast, thread-safe)

| Python (logging)                        | C++ (spdlog)                                     |
|-----------------------------------------|--------------------------------------------------|
| `logging.getLogger(name)`               | `spdlog::get(name)` / `spdlog::logger`           |
| `RotatingFileHandler`                   | `spdlog::rotating_logger_mt()`                   |
| `logger.info/warning/error(msg)`        | `spdlog::info/warn/error(msg)`                   |

---

## 2. C++ Project Architecture

```
specmap-cpp/
├── CMakeLists.txt
├── include/
│   ├── core/
│   │   ├── SpectrumData.hpp        # equivalent of lib9 SpectrumData
│   │   ├── XYMap.hpp               # equivalent of lib9 XYMap
│   │   ├── PMClass.hpp             # equivalent of PMclasslib1 PMclass / Spectra
│   │   ├── MathLib.hpp             # equivalent of mathlib3
│   │   ├── Normalization.hpp       # equivalent of hsi_normalization
│   │   ├── CosmicRemoval.hpp       # cosmic ray removal algorithms
│   │   └── ErrorHandler.hpp        # equivalent of error_handler
│   ├── io/
│   │   ├── FileLoader.hpp          # spectrum file loaders
│   │   ├── Serializer.hpp          # cereal-based save/load
│   │   ├── NewtonLoader.hpp        # equivalent of newtonspeclib1
│   │   ├── TCSPCLoader.hpp         # equivalent of TCSPClib
│   │   └── DefaultsManager.hpp     # equivalent of deflib1 defaults
│   └── gui/
│       ├── MainWindow.hpp          # top-level FLTK window + menu
│       ├── TabManager.hpp          # Fl_Tabs management
│       ├── tabs/
│       │   ├── LoadDataTab.hpp     # "Load Data" tab
│       │   ├── HyperspectraTab.hpp # "Hyperspectra" tab
│       │   ├── ClaraImageTab.hpp   # "Clara Image" tab
│       │   ├── HSIPlotTab.hpp      # "HSI Plot" tab
│       │   ├── NewtonSpecTab.hpp   # "Newton Spectrum" tab
│       │   ├── TCSPCTab.hpp        # "TCSPC" tab
│       │   ├── FileSorterTab.hpp   # "HSI File Sorter" tab
│       │   └── SettingsTab.hpp     # "Settings" tab
│       ├── widgets/
│       │   ├── ColormapWidget.hpp  # FLTK widget for HSI colormap display
│       │   ├── SpectrumPlot.hpp    # ImPlot-based spectrum viewer
│       │   └── ScrollableGroup.hpp # Fl_Scroll + Fl_Group helper
│       └── PlotWindow.hpp          # Detached plot window (ImGui/ImPlot)
├── src/
│   ├── core/   (*.cpp implementations)
│   ├── io/
│   └── gui/
├── third_party/
│   ├── fltk/         (FLTK 1.4)
│   ├── eigen/        (Eigen 3)
│   ├── spdlog/       (spdlog)
│   ├── cereal/       (cereal serialization)
│   ├── nlohmann/     (nlohmann/json)
│   ├── stb/          (stb_image, stb_image_write, stb_image_resize)
│   ├── imgui/        (Dear ImGui)
│   ├── implot/       (ImPlot)
│   └── BS_thread_pool/ (thread pool)
└── main.cpp
```

---

## 3. Thread-Safety & Memory-Safety Design

### 3.1 Data ownership model

```cpp
// HSI data is owned by a shared_ptr so multiple GUI components can observe it
// without copying, but writes are protected by a shared_mutex.
struct HSIData {
    std::vector<std::vector<float>> spectra;   // [pixel_index][wavelength]
    std::vector<float>              wavelengths;
    std::vector<float>              x_positions;
    std::vector<float>              y_positions;
    std::unordered_map<std::string, std::string> metadata;
};

class XYMap {
    std::shared_ptr<HSIData>   data_;        // shared ownership
    mutable std::shared_mutex  data_mutex_;  // readers–writer lock
public:
    // Multiple GUI threads can read simultaneously
    auto readData() const {
        std::shared_lock lock(data_mutex_);
        return data_;
    }
    // Only one writer at a time
    void setData(std::shared_ptr<HSIData> d) {
        std::unique_lock lock(data_mutex_);
        data_ = std::move(d);
    }
};
```

### 3.2 Background processing pattern

```cpp
// Worker thread submits a GUI-safe callback via Fl::awake
void XYMap::loadFilesAsync(std::vector<std::string> paths) {
    stop_flag_.store(false);
    worker_ = std::thread([this, paths = std::move(paths)]() {
        auto result = std::make_shared<HSIData>();
        for (const auto& p : paths) {
            if (stop_flag_.load()) return;  // cancellation check
            loadSingleFile(p, *result);
        }
        // Pass result to GUI thread safely
        Fl::awake([](void* data) {
            auto* self = static_cast<XYMap*>(data);
            self->onLoadComplete();
        }, this);
    });
}

void XYMap::cancel() {
    stop_flag_.store(true);
    if (worker_.joinable()) worker_.join();
}
```

### 3.3 RAII resource management

- No raw `new` / `delete`. Use `std::unique_ptr` for FLTK widgets constructed dynamically.
- FLTK itself manages widget lifetime when a parent is destroyed, so only root-level or
  dynamically added widgets need explicit pointer management.
- File handles wrapped in RAII classes (e.g., use `std::ifstream` which closes automatically).

---

## 4. Incremental Build Tasks

Each task is designed to be independently buildable and testable. Complete them in order;
each one leaves the application in a running state.

---

### Task 1 — Project Scaffold & CMake Setup

**Goal:** A "Hello World" FLTK window that compiles and runs.

**Steps:**
1. Create `CMakeLists.txt` with targets:
   - `find_package(FLTK REQUIRED)` or `add_subdirectory(third_party/fltk)`
   - Add `Eigen3`, `spdlog`, `nlohmann_json` via `FetchContent` or git submodules.
2. Create `main.cpp` with a minimal `Fl_Window` that opens and closes cleanly.
3. Create `include/core/ErrorHandler.hpp` backed by **spdlog** rotating logger.
4. Add a basic unit test target (`ctest`) for the logger.

**Deliverable:** `cmake --build . && ./specmap` shows an empty FLTK window.

---

### Task 2 — Defaults Manager & Settings Tab

**Goal:** Load/save `defaults.txt` and display a Settings tab (mirrors `deflib1.py`).

**Steps:**
1. Implement `DefaultsManager` with typed `get<T>(key)` / `set(key, val)` and file I/O.
2. Create `MainWindow` with `Fl_Menu_Bar` and `Fl_Tabs` (8 tabs, all empty `Fl_Group`).
3. Implement `SettingsTab` with `Fl_Input` widgets for all default keys.
4. Wire Save/Load buttons to `DefaultsManager`.

**Deliverable:** Tabbed window with a functional Settings tab that persists defaults.

---

### Task 3 — Core Data Model (SpectrumData, XYMap, PMClass)

**Goal:** Pure C++ port of `lib9.py` and `PMclasslib1.py` data structures (no GUI).

**Steps:**
1. `SpectrumData`: wavelength array, intensity array, metadata map, background subtraction,
   cosmic removal (median filter), linear background.
2. `PMClass` / `Spectra`: pixel matrix, x/y axes, metadata, grid step computation.
3. `XYMap`: holds a 2-D array of `SpectrumData`, computes pixel intensity map.
4. `MathLib`: Voigt/Gaussian/Lorentzian fits via Ceres, Savitzky–Golay filter, peak finder,
   Hilbert transform via FFTW.
5. Unit tests for all math functions comparing output to known values.

**Deliverable:** All data structures pass unit tests; no GUI dependency.

---

### Task 4 — File I/O Layer

**Goal:** Read the same spectrum files that the Python version reads.

**Steps:**
1. `FileLoader`: scan a directory, filter by filename pattern, parse each file into
   `SpectrumData` (text/CSV spectrum format used by the current app).
2. `NewtonLoader`: read Newton spectrometer files (mirrors `newtonspeclib1.py`).
3. `TCSPCLoader`: read TCSPC CSV files (mirrors `TCSPClib.py`).
4. `Serializer`: cereal-based binary save/load for `XYMap` (replaces `pickle`).
5. Integration test: load the same test dataset that `main9.py` uses and compare results.

**Deliverable:** Can load all supported file formats from the command line.

---

### Task 5 — Load Data Tab

**Goal:** Functional "Load Data" tab (mirrors `createbuttons()` in `main9.py`).

**Steps:**
1. `LoadDataTab`: folder entry, filename entry, file extension entry, Browse buttons.
2. Background options: Multiple BG checkbox, Linear BG checkbox, Power Correction checkbox.
3. Cosmic removal: checkbox, method dropdown (`Fl_Choice`), threshold entry, width entry.
4. Derivative options: First/Second derivative checkboxes, polynomial order, N fit points.
5. Multiple-HSIs batch processing sub-frame.
6. Save/Load current HSI object sub-frame (backed by `Serializer`).
7. Newton, TCSPC file entries.
8. "Load HSI Data" button triggers background thread; progress indicator shown in status bar.

**Deliverable:** Users can select files and trigger a load; data populates `XYMap`.

---

### Task 6 — Colormap Widget & Hyperspectra Tab

**Goal:** Display the 2-D HSI intensity colormap and allow pixel selection.

**Steps:**
1. `ColormapWidget` (custom `Fl_Widget` subclass):
   - Renders pixel intensity matrix as an `Fl_RGB_Image` using a chosen colormap LUT.
   - Mouse click → emits selected `(x, y)` pixel coordinate signal.
   - Mouse drag → region-of-interest (ROI) selection.
2. `SpectrumPlot` (ImPlot inside `Fl_Gl_Window`):
   - Draws the spectrum for the currently selected pixel.
   - Supports overlaying fit results.
3. `HyperspectraTab`: `Fl_Scroll` containing `ColormapWidget` on top, `SpectrumPlot` below.
4. Wire pixel click → update `SpectrumPlot`.
5. Colormap selector (`Fl_Choice`) and intensity range inputs.

**Deliverable:** Interactive HSI colormap with live spectrum preview on click.

---

### Task 7 — Spectrum Fitting & Analysis Controls

**Goal:** Expose the spectral fitting functionality in the Hyperspectra tab.

**Steps:**
1. Port fitting routines from `mathlib3.py` using Ceres Solver:
   - Gaussian, Lorentzian, Voigt, double variants.
   - Peak finder.
2. Add fit-control sub-panel in `HyperspectraTab`: fit range, initial parameters, fit button.
3. Overlay fit curve on `SpectrumPlot`.
4. Export fit parameters to CSV.
5. Port `hsi_normalization.py` normalization modes and expose as dropdown.

**Deliverable:** Single-pixel spectrum can be fitted and results displayed.

---

### Task 8 — HSI Plot Tab (Export / Fancy Image)

**Goal:** Mirrors `export2.py` / `array_plotclass1.py` — create an exportable false-color image.

**Steps:**
1. `HSIPlotTab` with `PlotHSI` ImPlot widget.
2. Parameter inputs: colormap, wavelength range for integration, scale bar, title.
3. Render button: compute integrated intensity image, display in widget.
4. Export button: save as PNG/TIFF via `stb_image_write`.
5. Drag-and-drop annotations (rectangles, text) drawn with ImPlot draw list.

**Deliverable:** HSI false-color image can be rendered and saved.

---

### Task 9 — Clara Image Tab

**Goal:** Port `claralib1.py` — load and display a confocal/CL image with 2-D Gaussian fit.

**Steps:**
1. `ClaraImageTab`: file entry + Browse, scaling factor dropdown (20×/50×/100×).
2. Image display in a `ColormapWidget` (reuse Task 6).
3. 2-D Gaussian fit via Ceres (port `fit_gaussian_2d`).
4. Overlay fit contour on image.
5. Display fit results (center x/y, width x/y, amplitude).

**Deliverable:** CL/confocal image loads, displays, and can be fitted.

---

### Task 10 — Newton Spectrum Tab

**Goal:** Port `newtonspeclib1.py` — view single Newton spectrometer files.

**Steps:**
1. `NewtonSpecTab`: file entry + Browse, Load button.
2. Display spectrum in `SpectrumPlot` (reuse Task 6).
3. Basic controls: x-range, y-range, title.
4. Export to CSV.

**Deliverable:** Newton spectrum files can be loaded and viewed.

---

### Task 11 — TCSPC Tab

**Goal:** Port `TCSPClib.py` — load and visualize time-correlated single photon counting data.

**Steps:**
1. `TCSPCTab`: directory entry + Browse, save directory entry, Load button.
2. Load TCSPC data into a 2-D time × wavelength matrix.
3. Display time-resolved emission map using `ColormapWidget`.
4. Time-slice and wavelength-slice spectrum plots.
5. Exponential decay fitting (via Ceres).
6. Export processed results.

**Deliverable:** TCSPC data can be loaded, visualized, and fitted.

---

### Task 12 — HSI File Sorter Tab

**Goal:** Port `specfilesorter` class in `main9.py`.

**Steps:**
1. `FileSorterTab`: main directory, filename pattern, file extension, save directory, process directory.
2. Scan main directory, list matching files.
3. Sort/move files to process or save directory based on rules.
4. Progress indicator.

**Deliverable:** File sorting works from the GUI.

---

### Task 13 — Menu Bar & Application Wiring

**Goal:** Complete `MainWindow` with all menu actions and cross-tab communication.

**Steps:**
1. `File` menu: New, Open (load defaults), Save Defaults, Exit.
2. `View` menu: toggle tab visibility.
3. `Help` menu: About dialog.
4. Global status bar showing last operation and thread state.
5. Connect "Load Data" tab actions to update Hyperspectra, HSI Plot, etc.
6. Application shutdown: join all worker threads, flush logger.

**Deliverable:** Fully wired application; all tabs work together.

---

### Task 14 — Packaging & CI

**Goal:** Produce a self-contained binary for Linux, Windows, macOS.

**Steps:**
1. CPack configuration for `.AppImage` (Linux), `.msi`/NSIS (Windows), `.dmg` (macOS).
2. GitHub Actions workflow: build + test matrix for all three platforms.
3. Static-link FLTK and third-party libs to minimize runtime dependencies.
4. Sign macOS/Windows binaries if certificates are available.

---

## 5. Third-Party Dependency Summary

| Library               | Version   | Purpose                           | License        |
|-----------------------|-----------|-----------------------------------|----------------|
| FLTK                  | 1.4.x     | GUI frontend                      | LGPL           |
| Eigen                 | 3.4+      | Linear algebra / array math       | MPL2           |
| Ceres Solver          | 2.2+      | Non-linear least squares fitting  | BSD            |
| spdlog                | 1.13+     | Thread-safe logging               | MIT            |
| nlohmann/json         | 3.11+     | JSON config / metadata            | MIT            |
| cereal                | 1.3+      | Binary serialization              | BSD            |
| stb_image / stb_image_write / stb_image_resize | latest | Image I/O     | MIT/Public domain |
| Dear ImGui            | 1.90+     | Immediate-mode overlay UI         | MIT            |
| ImPlot                | 0.17+     | ImGui-based plotting              | MIT            |
| BS::thread_pool       | 4.1+      | Thread pool                       | MIT            |
| libcerf / Faddeeva    | latest    | Voigt (Faddeeva) function         | MIT            |
| fast-cpp-csv-parser   | latest    | CSV reading                       | BSD            |
| FFTW3                 | 3.3+      | Hilbert transform / FFT           | GPL (or MKL)   |

> **GPL note:** FFTW3 is GPL; use Intel MKL (free) or kiss_fft (BSD) if a permissive
> license is required.

---

## 6. Key Design Decisions

1. **FLTK + ImGui hybrid:** FLTK provides the main window, tabs, and form-style inputs.
   ImGui/ImPlot runs inside a `Fl_Gl_Window` for interactive scientific plotting. This
   avoids reinventing the plot widget while keeping the familiar FLTK widget hierarchy.

2. **Shared ownership of HSI data:** `std::shared_ptr<HSIData>` is passed to the GUI
   widgets. A `std::shared_mutex` guards writes. Readers (plot widgets) hold shared locks;
   the loader thread holds a unique lock only during data replacement, then atomically
   swaps the pointer.

3. **Cancellation tokens:** Every background task receives an `std::atomic<bool>&`
   cancellation flag. Tasks check the flag at regular intervals (e.g., after each file).

4. **Exception handling across thread boundaries:** Worker threads should catch all
   exceptions internally and communicate errors to the GUI thread via `Fl::awake()` to
   avoid unhandled exceptions terminating the program. If rethrowing is needed,
   use `std::exception_ptr` with `std::promise` / `std::future` to safely transfer
   exception state across thread boundaries.

5. **Incremental tab delivery:** Each tab (Tasks 5–12) is built as a self-contained class
   with a minimal interface (`Fl_Group* widget()`). The `TabManager` inserts them into
   `Fl_Tabs` without knowing their internals. This allows building and testing each tab
   independently before integration.
