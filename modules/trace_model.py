import numpy as np
import analysis 

class Trace:
    def __init__(self, name, freqs, mags, is_db=False):
        self.name = name
        self.freqs = freqs
        self.mags = mags
        self.is_db = is_db # True if data is already in dB/dBm
        self.visible = True

    @classmethod
    def from_time_domain(cls, name, time_data, volt_data, sample_rate, remove_dc=False):
        """
        Creates a trace from Time Domain data (Runs FFT).
        """
        # Call your existing analysis module
        freqs, mags = analysis.get_fft_data(volt_data, sample_rate, remove_dc=remove_dc)
        return cls(name, freqs, mags, is_db=False)

    @classmethod
    def from_freq_domain(cls, name, freq_data, mag_data):
        """
        Creates a trace from Frequency Domain data (No FFT).
        """
        return cls(name, freq_data, mag_data, is_db=True)