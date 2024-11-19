import numpy as np
from scipy.fft import fft
import pandas as pd
import matplotlib.pyplot as plt

NUM_SAMPLES = 524288
SAMPLE_FREQ = 250000

def create_histogram(data, column):

    fig = plt.figure()
    # Create the histogram
    ax = data[column].hist()
    # Add labels and title (optional)
    ax.set_xlabel(column)
    ax.set_ylabel('Amplitude Value')
    ax.set_title(f'Histogram of {column}')
        
    # Show the plot
    plt.show()
    return fig

def calculate_fft(data, column):
    # Compute the FFT of the column
    fft_values = np.fft.fft(data[column].values, n=NUM_SAMPLES)
    fft_magnitude = np.abs(fft_values)
    
    # Calculate the frequency bins
    freqs = np.fft.fftfreq(NUM_SAMPLES, 1 / SAMPLE_FREQ)

    # Exclude the zero frequency and Nyquist frequency components
    valid_indices = np.where((freqs > 0) & (freqs < SAMPLE_FREQ / 2))
    valid_freqs = freqs[valid_indices]
    valid_magnitude = fft_magnitude[valid_indices]

    # Create a new figure
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)

    # Plot the FFT magnitude
    ax.plot(valid_freqs, valid_magnitude)

    # Add labels and title (optional)
    ax.set_xlabel('Frequency')
    ax.set_ylabel('Amplitude')
    ax.set_title(f'FFT spectrum of {column}')
    # Show the plot
    plt.show()
    return fig

def calculate_power_spectrum(data, column):
    freq = np.fft.fftfreq(len(data[column]))
    ps = np.abs(np.fft.fft(data[column]))**2
    return freq, ps

def calculate_psd(data, column):
    freq, ps = calculate_power_spectrum(data, column)
    return freq, ps / len(freq)

def show_S(data, column):
    return None

def time_domain_gating(data, column):
    return None

def frequency_domain_back(data, column):
    return None