import numpy as np
import pandas as pd
import analysis 

class Trace:
    def __init__(self, name, freqs, mags, is_db=False):
        self.name = name
        self.freqs = freqs
        self.mags = mags
        self.is_db = is_db 
        self.visible = True
        self.is_active = False
        self.color = None 

    @classmethod
    def from_time_domain(cls, name, time_data, volt_data, remove_dc=False, manual_sample_rate=None):
        """
        Creates a trace from Time Domain data with normalization and dB scaling.
        """
        volt_clean = pd.to_numeric(volt_data, errors='coerce')
        time_clean = pd.to_numeric(time_data, errors='coerce')
        
        mask = ~np.isnan(volt_clean) & ~np.isnan(time_clean)
        volt_clean = volt_clean[mask]
        time_clean = time_clean[mask]
        
        if len(volt_clean) < 2:
            raise ValueError(f"Not enough valid data in {name}")

        if manual_sample_rate is not None and manual_sample_rate > 0:
            sample_rate = float(manual_sample_rate)
        else:
            dt = time_clean[1] - time_clean[0]
            if dt == 0 and len(time_clean) > 2:
                dt = time_clean[2] - time_clean[0] / 2
            if dt <= 0:
                raise ValueError("Invalid Time steps (dt <= 0).")

            sample_rate_raw = 1.0 / dt
            if sample_rate_raw < 1000: 
                 sample_rate = sample_rate_raw * 1e9 
            else:
                 sample_rate = sample_rate_raw

        # Calculate FFT with dB conversion enabled
        freqs, mags = analysis.get_fft_data(volt_clean, sample_rate, remove_dc=remove_dc, to_db=True)
        return cls(name, freqs, mags, is_db=True)

    @classmethod
    def from_freq_domain(cls, name, freq_data, mag_data):
        freq_clean = pd.to_numeric(freq_data, errors='coerce')
        mag_clean = pd.to_numeric(mag_data, errors='coerce')
        mask = ~np.isnan(freq_clean) & ~np.isnan(mag_clean)
        return cls(name, freq_clean[mask], mag_clean[mask], is_db=True)