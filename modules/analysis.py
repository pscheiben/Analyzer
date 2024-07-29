import numpy as np
from scipy.fft import fft

def create_histogram(data, column):
    return data[column].hist()

def calculate_fft(data, column):
    return fft(data[column].values)

def calculate_power_spectrum(data, column):
    freq = np.fft.fftfreq(len(data[column]))
    ps = np.abs(np.fft.fft(data[column]))**2
    return freq, ps

def calculate_psd(data, column):
    freq, ps = calculate_power_spectrum(data, column)
    return freq, ps / len(freq)
