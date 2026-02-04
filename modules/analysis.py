import numpy as np
from scipy.fft import fft
from scipy.signal import find_peaks, detrend

def get_fft_data(data_array, sample_rate, remove_dc=False, to_db=True):
    """
    Calculates the FFT, normalizes the peak to 0 dB, and returns freq/mag.
    """
    N = len(data_array)
    
    # 1. Remove DC / Linear Trend
    if remove_dc:
        # 'linear' subtracts a best-fit line (removes both offset AND drift)
        work_data = detrend(data_array, type='linear')
    else:
        work_data = data_array
    
    # 2. Compute FFT
    fft_values = fft(work_data)
    magnitude = np.abs(fft_values)[:N//2] * 2 / N
    freq_axis = np.fft.fftfreq(N, 1 / sample_rate)[:N//2]
    
    # 3. The "Sledgehammer": Force 0 Hz to Absolute Zero
    if remove_dc:
        magnitude[0] = 0  
    
    # 4. Normalization (Scale peak to 1.0)
    max_val = np.max(magnitude)
    if max_val > 0:
        magnitude = magnitude / max_val
    
    # 5. Convert to Decibels (dB)
    if to_db:
        # 1e-12 floor prevents log(0) errors
        magnitude = 20 * np.log10(magnitude + 1e-12)
    
    return freq_axis, magnitude

def get_noise_floor(magnitude_data):
    """
    Returns the approximate noise floor using the median.
    """
    # We use median because it ignores the high peaks (signals)
    return np.median(magnitude_data)

def get_top_peaks(freqs, magnitude, top_n=5, min_dist_hz=500, freq_range=None):
    """
    Finds peaks, optionally restricted to a specific frequency range.
    """
    if freq_range:
        min_f, max_f = freq_range
        mask = (freqs >= min_f) & (freqs <= max_f)
        search_freqs = freqs[mask]
        search_mags = magnitude[mask]
        
        if len(search_freqs) == 0:
            return []
    else:
        search_freqs = freqs
        search_mags = magnitude

    if len(search_freqs) > 1:
        hz_per_bin = search_freqs[1] - search_freqs[0]
        distance_indices = int(min_dist_hz / hz_per_bin)
        distance_indices = max(1, distance_indices)
    else:
        distance_indices = 1
    
    peaks, properties = find_peaks(search_mags, distance=distance_indices, height=-140 if any(search_mags < 0) else 0)
    
    sorted_indices = np.argsort(properties['peak_heights'])[::-1]
    top_peak_indices = peaks[sorted_indices][:top_n]
    
    results = []
    for idx in top_peak_indices:
        results.append((search_freqs[idx], search_mags[idx]))
        
    return results