import numpy as np
from scipy.fft import fft
from scipy.signal import find_peaks, detrend  # <--- Make sure detrend is imported

def get_fft_data(data_array, sample_rate, remove_dc=False):
    """
    Calculates the FFT.
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
    # Even after detrending, tiny residuals can remain. This kills them.
    if remove_dc:
        magnitude[0] = 0  
        # Optional: Kill the first few bins too if leakage is bad (e.g., magnitude[0:5] = 0)
    
    return freq_axis, magnitude

def get_top_peaks(freqs, magnitude, top_n=5, min_dist_hz=500, freq_range=None):
    """
    Finds peaks, optionally restricted to a specific frequency range (zoomed view).
    """
    # --- NEW: Filter data to the zoomed range ---
    if freq_range:
        min_f, max_f = freq_range
        # Create a boolean mask (True/False list) for the valid range
        mask = (freqs >= min_f) & (freqs <= max_f)
        
        # Apply the mask
        search_freqs = freqs[mask]
        search_mags = magnitude[mask]
        
        # If we zoomed too far and have no data, return empty
        if len(search_freqs) == 0:
            return []
    else:
        search_freqs = freqs
        search_mags = magnitude
    # --------------------------------------------

    # 1. Convert min_distance from Hz to array indices
    if len(search_freqs) > 1:
        hz_per_bin = search_freqs[1] - search_freqs[0]
        distance_indices = int(min_dist_hz / hz_per_bin)
        # Ensure distance is at least 1
        distance_indices = max(1, distance_indices)
    else:
        distance_indices = 1
    
    # 2. Find peaks in the FILTERED data
    peaks, properties = find_peaks(search_mags, distance=distance_indices, height=0)
    
    # 3. Sort by height
    sorted_indices = np.argsort(properties['peak_heights'])[::-1]
    top_peak_indices = peaks[sorted_indices][:top_n]
    
    # 4. Return results (Mapped back to real frequency/magnitude)
    results = []
    for idx in top_peak_indices:
        results.append((search_freqs[idx], search_mags[idx]))
        
    return results