# Mathematical Derivation: Local Polynomial Fitting for Spectral Derivatives

This document outlines the rigorous mathematical foundation for why we evaluate spectral derivatives using local polynomial fits, and demonstrates exactly how it translates to the ultra-fast **Savitzky-Golay** method used in our benchmarking scripts.

---

## 1. The Problem: Noise Amplification in Finite Differences

In raw hyperspectral or spectroscopic data, the measured intensity $y_i$ at wavelength $x_i$ always contains physical truth $f(x_i)$ plus random noise $\epsilon_i$:

$$ y_i = f(x_i) + \epsilon_i $$

If we try to compute the derivative using a standard finite difference, e.g., the central difference:

$$ y'_i \approx \frac{y_{i+1} - y_{i-1}}{2h} = \frac{f(x_{i+1}) - f(x_{i-1})}{2h} + \frac{\epsilon_{i+1} - \epsilon_{i-1}}{2h} $$

Because the spacing $h = x_{i+1} - x_i$ is typically very small, dividing by $2h$ massively amplifies the high-frequency random noise $\epsilon$. The resulting derivative spectrum will be dominated by noise, obscuring the physical signal. 

**The Solution:** We must smooth the data concurrently with taking the derivative. Fitting a smooth polynomial to a local window of points accomplishes exactly this.

---

## 2. Setting Up the Local Polynomial Fit

Consider a sliding window of $N = 2m + 1$ equally spaced data points centered around an index of interest. 
Let's translate our coordinate system locally so the center point is at $x = 0$. 
The input coordinates for our window are $x_i$ where $i \in \{-m, \dots, -1, 0, 1, \dots, m\}$.

We want to approximate the data inside this window using a polynomial of degree $n$ (where $n < N$):

$$ p_n(x) = c_0 + c_1 x + c_2 x^2 + \dots + c_n x^n = \sum_{k=0}^{n} c_k x^k $$

---

## 3. Ordinary Least Squares (OLS) Derivation

To find the best fitting polynomial, we minimize the sum of the squared residuals ($E$) between our polynomial $p_n(x)$ and the observed data $y_i$:

$$ E(c_0, \dots, c_n) = \sum_{i=-m}^{m} \left( p_n(x_i) - y_i \right)^2 = \sum_{i=-m}^{m} \left( \sum_{k=0}^{n} c_k x_i^k - y_i \right)^2 $$

We can write this elegantly in matrix notation. 
Let $\mathbf{y}$ be the column vector of length $N$ containing our data points, and $\mathbf{c}$ be the vector of polynomial coefficients:

$$ \mathbf{y} = \begin{bmatrix} y_{-m} \\ \vdots \\ y_0 \\ \vdots \\ y_m \end{bmatrix}, \quad \mathbf{c} = \begin{bmatrix} c_0 \\ c_1 \\ \vdots \\ c_n \end{bmatrix} $$

Let $\mathbf{X}$ be the **Design Matrix** (or Vandermonde matrix) of shape $N \times (n+1)$, where each element $X_{i,k} = x_i^k$:

$$ \mathbf{X} = \begin{bmatrix} 
1 & x_{-m} & x_{-m}^2 & \dots & x_{-m}^n \\
\vdots & \vdots & \vdots & & \vdots \\
1 & x_0 & x_0^2 & \dots & x_0^n \\
\vdots & \vdots & \vdots & & \vdots \\
1 & x_m & x_m^2 & \dots & x_m^n
\end{bmatrix} $$

The objective is to minimize the squared $L_2$ norm: $E(\mathbf{c}) = ||\mathbf{Xc} - \mathbf{y}||^2$.

To find the minimum, we take the gradient with respect to $\mathbf{c}$ and set it to zero, leading to the **Normal Equations**:

$$ (\mathbf{X}^T \mathbf{X}) \mathbf{c} = \mathbf{X}^T \mathbf{y} $$

If the points are distinct (which they are), $\mathbf{X}^T \mathbf{X}$ is a non-singular, invertible square matrix. The exact mathematical solution for the optimal polynomial coefficients is:

$$ \mathbf{c} = (\mathbf{X}^T \mathbf{X})^{-1} \mathbf{X}^T \mathbf{y} $$

---

## 4. Extracting the Derivative

Remember our local polynomial:

$$ p_n(x) = c_0 + c_1 x + c_2 x^2 + c_3 x^3 + \dots $$

Taking the first analytical derivative yields:

$$ \frac{d}{dx} p_n(x) = c_1 + 2 c_2 x + 3 c_3 x^2 + \dots $$

Because we cleverly shifted our local coordinate system heavily so the point of interest (the center of the window) sits exactly at $x = 0$, evaluating the derivative at the center point makes all terms involving $x$ vanish!

$$ \left. \frac{d}{dx} p_n(x) \right|_{x=0} = c_1 + 2 c_2(0) + \dots = c_1 $$

Similarly, if we wanted the smoothed data value, it's just $c_0$. The second derivative is exactly $2c_2$.

**Conclusion:** The first derivative at the center of the sliding window is *exactly* the $c_1$ coefficient of our least-squares polynomial.

---

## 5. The Savitzky-Golay "Trick" (Why it's so fast)

If we implement the above naively using `np.polyfit` in a sliding loop, the algorithm has to construct the matrix $\mathbf{X}$, calculate $\mathbf{X}^T \mathbf{X}$, invert it, and multiply it by $\mathbf{X}^T \mathbf{y}$ for **every single wavelength pixel** in the spectrum. This requires solving an $(n+1) \times (n+1)$ matrix system hundreds or thousands of times per array!

However, mathematical pioneers Abraham Savitzky and Marcel J. E. Golay (1964) realized a massive shortcut.

Look at the matrix term that maps our data vector $\mathbf{y}$ to our coefficient vector $\mathbf{c}$:

$$ \mathbf{H} = (\mathbf{X}^T \mathbf{X})^{-1} \mathbf{X}^T $$

This "Hat Matrix" $\mathbf{H}$ depends *exclusively* on the grid spacing ($x_i$), window size ($N$), and polynomial order ($n$). **It does not depend on the actual spectral data $\mathbf{y}$ at all.** 

Because spectroscopic data arrays usually have a constant pixel spacing (e.g., $1\text{ nm}$ or $0.5\text{ cm}^{-1}$), the local coordinates $\{-m, \dots, 0, \dots, m\}$ are perfectly identical for every single window position. 
Therefore, the matrix $\mathbf{H}$ is **a constant for the entire spectrum**.

Since we only care about the first derivative (the $c_1$ coefficient), we only need the second row of the $\mathbf{H}$ matrix. Let's call this row vector $\mathbf{w}$ (for weights).

$$ c_1 = \mathbf{w} \cdot \mathbf{y} = \sum_{i=-m}^{m} w_i y_i $$

### The Paradigm Shift
Instead of doing a massive matrix inversion solving $E = ||\mathbf{Xc} - \mathbf{y}||^2$ repetitively, `scipy.signal.savgol_filter` simply pre-calculates the array of constants $\mathbf{w}$ once. It then slides across the spectrum performing a simple $O(N)$ **linear convolution** (a dot product). 

This mathematical realization is exactly why the Savitzky-Golay filter achieves the same output as `np.polyfit` but executes 10 to 50 times faster.

---

## 6. How Noise Behaves: Finite Distances vs. Polynomial Fits

To understand exactly *why* finite differences fail on physical spectra and why the polynomial (Savitzky-Golay) approach succeeds, we must mathematically evaluate the variance of the noise.

Assume the random noise $e_i$ at each pixel is independent and identically distributed (i.i.d.) with a variance of $\sigma^2$.

### Scenario A: Noise in Finite Differences
Using the central difference method, the derivative is calculated from two adjacent points separated by a grid spacing of $h$:
$$ y'_i \approx \frac{y_{i+1} - y_{i-1}}{2h} $$

The variance of this derivative is calculated using the property $Var(aX + bY) = a^2 Var(X) + b^2 Var(Y)$:
$$ \text{Var}(y'_i) = \text{Var}\left( \frac{y_{i+1}}{2h} - \frac{y_{i-1}}{2h} \right) = \frac{\text{Var}(y_{i+1}) + \text{Var}(y_{i-1})}{(2h)^2} = \frac{\sigma^2 + \sigma^2}{4h^2} = \frac{\sigma^2}{2h^2} $$

**The consequence:** Because the pixel spacing $h$ in spectroscopy is very small (often $h \ll 1$), $h^2$ is microscopic. Dividing variance $\sigma^2$ by this microscopic number causes the noise variance to **explode globally**. The higher the resolution of your spectrometer (the smaller $h$ gets), the worse the noise becomes in finite differences!

### Scenario B: Noise in a Polynomial Fit (Savitzky-Golay)
In the Savitzky-Golay method, the center point's first derivative $c_1$ is calculated via a linear combination of all $N$ window points using the pre-computed weights $w_j$:
$$ y'_i = c_1 = \sum_{j=-m}^{m} w_j y_{i+j} $$

The variance of a linear combination of independent variables translates to the sum of the squared coefficients:
$$ \text{Var}(y'_i) = \text{Var}\left( \sum_{j=-m}^{m} w_j y_{i+j} \right) = \sum_{j=-m}^{m} w_j^2 \text{Var}(y_{i+j}) = \sigma^2 \sum_{j=-m}^{m} w_j^2 $$

**The consequence:** By extending the evaluation window across $N$ points, the variance is scaled by the sum of the squared convolution weights $\sum w_j^2$. Through the analytical properties of the hat matrix $\mathbf{H} = (\mathbf{X}^T \mathbf{X})^{-1} \mathbf{X}^T$, it can be proven that the sum of squared weights for the first derivative roughly scales proportionally to $\frac{1}{N^3}$. 

Therefore, as you increase the polynomial window size $N$, **the noise variance drops dramatically according to $O(1/N^3)$.** The polynomial fit actively averages out the random fluctuations across the entire window rather than amplifying the raw difference between just two adjacent noisy pixels. This allows you to construct virtually noiseless, ultra-reliable derivatives of highly sensitive physical spectra.