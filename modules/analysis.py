import numpy as np
from scipy.fft import fft
from scipy.signal import find_peaks, detrend, windows

def get_fft_data(data_array, sample_rate, remove_dc=False, to_db=True):
    """
    Calculates the FFT using a Hann window and scales to dBV (ref 1V).
    """
    N = len(data_array)
    
    # 1. Remove DC / Linear Trend
    if remove_dc:
        work_data = detrend(data_array, type='linear')
    else:
        work_data = data_array
    
    # 2. Apply Hann Window
    # The Hann window reduces spectral leakage but requires a coherent gain correction
    window = windows.hann(N)
    win_data = work_data * window
    
    # 3. Compute FFT
    fft_values = fft(win_data)
    
    # 4. Magnitude Calculation & Scaling
    # Multiply by 2 for single-sided spectrum (except DC).
    # Divide by sum(window) instead of N to correct for window processing loss.
    magnitude = np.abs(fft_values)[:N//2] * 2 / np.sum(window)
    freq_axis = np.fft.fftfreq(N, 1 / sample_rate)[:N//2]
    
    if remove_dc:
        magnitude[0] = 0  
    
    # 5. Convert to dBV (Reference: 1V)
    if to_db:
        # No more max_val normalization; use absolute 1V reference
        # Floor at -160dB to prevent log(0)
        magnitude = 20 * np.log10(magnitude + 1e-8)
    
    return freq_axis, magnitude

def get_noise_floor(magnitude_data):
    """
    Returns the approximate noise floor using the median.
    With a Hann window and no normalization, this represents the 
    average noise power density across the bins.
    """
    return np.median(magnitude_data)

def get_top_peaks(freqs, magnitude, top_n=5, min_dist_hz=500, freq_range=None):
    # Logic remains the same, but now operates on absolute dBV values
    if freq_range:
        min_f, max_f = freq_range
        mask = (freqs >= min_f) & (freqs <= max_f)
        search_freqs = freqs[mask]
        search_mags = magnitude[mask]
        if len(search_freqs) == 0: return []
    else:
        search_freqs = freqs
        search_mags = magnitude

    if len(search_freqs) > 1:
        hz_per_bin = search_freqs[1] - search_freqs[0]
        distance_indices = int(min_dist_hz / hz_per_bin)
        distance_indices = max(1, distance_indices)
    else:
        distance_indices = 1
    
    # Height set to -150 to catch peaks in absolute dBV scale
    peaks, properties = find_peaks(search_mags, distance=distance_indices, height=-150)
    
    sorted_indices = np.argsort(properties['peak_heights'])[::-1]
    top_peak_indices = peaks[sorted_indices][:top_n]
    
    return [(search_freqs[idx], search_mags[idx]) for idx in top_peak_indices]