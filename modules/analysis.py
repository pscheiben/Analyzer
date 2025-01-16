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

    # Sort by magnitude and enforce at least 500 Hz difference
    sorted_indices = np.argsort(fft_magnitude)[::-1]  # Indices sorted by descending magnitude
    top_5_freqs = []
    
    for freq_index in sorted_indices:
        freq = freqs[freq_index]
        if freq > 0 and all(abs(freq - freqs[idx]) >= 500 for idx in top_5_freqs):
            top_5_freqs.append(freq_index)
        if len(top_5_freqs) == 5:  # Stop after finding 5 peaks
            break

    # Exclude the zero frequency and Nyquist frequency components
    valid_indices = np.where((freqs > 0) & (freqs < SAMPLE_FREQ / 2))
    valid_freqs = freqs[valid_indices] / 1000 # Convert to kHz
    valid_magnitude = fft_magnitude[valid_indices]

    # Create a new figure
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)


    # Adjust y-axis limit to make room for annotations
    max_magnitude = max(valid_magnitude)
    ax.set_ylim(0, max_magnitude * 1.2)  # Extend 20% beyond the maximum magnitude

    # Plot the FFT magnitude
    ax.plot(valid_freqs, valid_magnitude)

    # Add labels and title (optional)
    ax.set_xlabel('Frequency (kHz)')
    ax.set_ylabel('Amplitude')
    ax.set_title(f'FFT spectrum of {column}')

    # Annotate the filtered top 5 frequencies on the plot
    used_positions = []
    for freq_index in top_5_freqs:
        freq_khz = freqs[freq_index] / 1000
        magnitude = fft_magnitude[freq_index]

        # Find a suitable position for the annotation
        annotation_x = freq_khz
        annotation_y = magnitude + max(valid_magnitude) * 0.05  # Initial position above the peak
        for used_x, used_y in used_positions:
            if abs(annotation_x - used_x) < 0.05 and abs(annotation_y - used_y) < max(valid_magnitude) * 0.1:
                annotation_y += max(valid_magnitude) * 0.05  # Adjust to avoid overlap

        # Add the annotation
        ax.annotate(
            f'{freq_khz:.2f} kHz',
            xy=(freq_khz, magnitude),
            xytext=(annotation_x, annotation_y),
            textcoords="data",
            ha='center',
            va='bottom',
            arrowprops=dict(facecolor='red', shrink=0.05, headwidth=6, headlength=8)
        )
        used_positions.append((annotation_x, annotation_y))
    


    # Show the plot
    plt.show()
    return fig

def calculate_pds(data, column):
    # Compute the FFT of the column
    fft_values = np.fft.fft(data[column].values, n=NUM_SAMPLES)
    fft_magnitude = np.abs(fft_values)
    
    # Calculate the power spectral density
    power_density = (fft_magnitude ** 2) / NUM_SAMPLES

    # Calculate the frequency bins
    freqs = np.fft.fftfreq(NUM_SAMPLES, 1 / SAMPLE_FREQ)
    
    # Sort by power density and enforce at least 500 Hz difference
    sorted_indices = np.argsort(power_density)[::-1]
    top_5_freqs = []

    for freq_index in sorted_indices:
        freq = freqs[freq_index]
        if freq > 0 and all(abs(freq - freqs[idx]) >= 500 for idx in top_5_freqs):
            top_5_freqs.append(freq_index)
        if len(top_5_freqs) == 5:
            break

    # Exclude the zero frequency and Nyquist frequency components
    valid_indices = np.where((freqs > 0) & (freqs < SAMPLE_FREQ / 2))
    valid_freqs = freqs[valid_indices] / 1000  # Convert to kHz
    valid_power_density = power_density[valid_indices]

    # Create a new figure
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)

    # Plot the power density
    ax.plot(valid_freqs, valid_power_density)

    # Add labels and title
    ax.set_xlabel('Frequency (kHz)')
    ax.set_ylabel('Power Density')
    ax.set_title(f'Power Spectral Density of {column}')

    # Adjust y-axis limit to make room for annotations
    max_power = max(valid_power_density)
    ax.set_ylim(0, max_power * 1.2)  # Extend 20% beyond the maximum power density

    # Annotate the filtered top 5 frequencies on the plot
    used_positions = []
    for freq_index in top_5_freqs:
        freq_khz = freqs[freq_index] / 1000
        power = power_density[freq_index]

        # Find a suitable position for the annotation
        annotation_x = freq_khz
        annotation_y = power + max_power * 0.05  # Initial position above the peak
        for used_x, used_y in used_positions:
            if abs(annotation_x - used_x) < 0.05 and abs(annotation_y - used_y) < max_power * 0.1:
                annotation_y += max_power * 0.05  # Adjust to avoid overlap

        # Ensure the annotation stays within the adjusted y-axis limits
        if annotation_y > max_power * 1.2:
            annotation_y = max_power * 1.15  # Keep it just below the top limit

        # Add the annotation
        ax.annotate(
            f'{freq_khz:.2f} kHz',
            xy=(freq_khz, power),
            xytext=(annotation_x, annotation_y),
            textcoords="data",
            ha='center',
            va='bottom',
            arrowprops=dict(facecolor='red', shrink=0.05, headwidth=6, headlength=8)
        )
        used_positions.append((annotation_x, annotation_y))

    # Show the plot
    plt.show()
    return fig

def show_S(data, column):
    return None

def time_domain_gating(data, column):
    return None

def frequency_domain_back(data, column):
    return None