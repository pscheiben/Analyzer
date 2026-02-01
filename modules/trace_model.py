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
        self.color = None  # <--- New attribute to store the static color

    @classmethod
    def from_time_domain(cls, name, time_data, volt_data, remove_dc=False):
        """
        Creates a trace from Time Domain data.
        Auto-calculates sample rate from the Time column.
        """
        # 1. Clean Data: Force to numeric, turn errors (strings) into NaN
        volt_clean = pd.to_numeric(volt_data, errors='coerce')
        time_clean = pd.to_numeric(time_data, errors='coerce')
        
        # Drop rows where data is missing/corrupt
        mask = ~np.isnan(volt_clean) & ~np.isnan(time_clean)
        volt_clean = volt_clean[mask]
        time_clean = time_clean[mask]
        
        if len(volt_clean) < 2:
            raise ValueError(f"Not enough valid data in {name}")

        # 2. Auto-Calculate Sample Rate
        # Calculate time step (dt) between first two samples
        dt = time_clean[1] - time_clean[0]
        
        # Safety: If dt is 0 (duplicate times), try the next point
        if dt == 0 and len(time_clean) > 2:
            dt = time_clean[2] - time_clean[0] / 2
            
        if dt <= 0:
            raise ValueError("Invalid Time steps (dt <= 0). Check CSV time column.")

        # GUESS UNITS: If dt is tiny (e.g. 4.0), it's likely Nanoseconds (PicoScope default)
        # If dt is small (0.000004), it's Seconds.
        # Heuristic: If sample rate < 1 Hz, assume it was nanoseconds.
        sample_rate_raw = 1.0 / dt
        
        if sample_rate_raw < 1000: # Less than 1kHz? Likely nS or uS
             # Assume nS (common for PicoScope) -> Convert to Hz (x 1e9)
             # NOTE: You can make this smarter if you read the unit from the header
             sample_rate = sample_rate_raw * 1e9 
             print(f"Auto-detected Sample Rate: {sample_rate/1e6:.2f} MHz (assuming nS inputs)")
        else:
             sample_rate = sample_rate_raw
             print(f"Auto-detected Sample Rate: {sample_rate/1000:.2f} kHz")

        # 3. Calculate FFT
        freqs, mags = analysis.get_fft_data(volt_clean, sample_rate, remove_dc=remove_dc)
        return cls(name, freqs, mags, is_db=False)

    @classmethod
    def from_freq_domain(cls, name, freq_data, mag_data):
        # Clean Data
        freq_clean = pd.to_numeric(freq_data, errors='coerce')
        mag_clean = pd.to_numeric(mag_data, errors='coerce')
        
        mask = ~np.isnan(freq_clean) & ~np.isnan(mag_clean)
        return cls(name, freq_clean[mask], mag_clean[mask], is_db=True)