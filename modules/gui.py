import tkinter as tk    # Import the tkinter module as tk
import pandas as pd     # Import the pandas module as pd
from tkinter import filedialog, messagebox  # Import the filedialog and messagebox modules from tkinter
from modules.analysis import create_histogram, calculate_fft, calculate_power_spectrum, calculate_psd # Import the create_histogram, calculate_fft, calculate_power_spectrum, and calculate_psd functions from the modules.analysis module
from modules.column_selector import SelectColumnsWindow

NUM_SAMPLES = 524288
SAMPLE_FREQ = 250000

class AnalyzerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Analyzer")
        self.create_widgets()
        self.selected_columns = []

    def create_widgets(self):
        button_width = 14  # Width in text units
        button_height = 2  # Height in text units
        padxvalue = 5
        padyvalue = 5
        self.load_button = tk.Button(
            self.root, text="Load Data", command=self.load_csv, width=button_width, height=button_height
        )
        self.load_button.grid(row=0, column=0, padx=padyvalue, pady=padxvalue)

        self.select_column_button = tk.Button(
            self.root, text="Select Columns", command=self.select_column, state="disabled",
            width=button_width, height=button_height
        )
        self.select_column_button.grid(row=1, column=0, padx=padyvalue, pady=padxvalue)

        self.histogram_button = tk.Button(
            self.root, text="Histogram", command=self.histogram, state="disabled",
            width=button_width, height=button_height
        )
        self.histogram_button.grid(row=2, column=0, padx=padyvalue, pady=padxvalue)

        self.fft_button = tk.Button(
            self.root, text="FFT Spectrum", command=self.fft, state="disabled",
            width=button_width, height=button_height
        )
        self.fft_button.grid(row=3, column=0, padx=padyvalue, pady=padxvalue)

        self.s_button = tk.Button(
            self.root, text="S-Parameters", command=self.S_param, state="disabled",
            width=button_width, height=button_height
        )
        self.s_button.grid(row=1, column=1, padx=padyvalue, pady=padxvalue)

        self.Time_Domain_button = tk.Button(
            self.root, text="Time Domain", command=self.time_domain, state="disabled",
            width=button_width, height=button_height
        )
        self.Time_Domain_button.grid(row=2, column=1, padx=padyvalue, pady=padxvalue)

        self.Frequency_Domain_button = tk.Button(
            self.root, text="Frequency Domain", command=self.frequency_domain, state="disabled",
            width=button_width, height=button_height
        )

        self.Frequency_Domain_button.grid(row=3, column=1, padx=padyvalue, pady=padxvalue)

        self.exit_button = tk.Button(
            self.root, text="Exit", command=self.root.quit, width=button_width, height=button_height
        )
        self.exit_button.grid(row=4, column=4, padx=padyvalue, pady=padxvalue)

    def load_csv(self):
        self.file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if self.file_path:
            self.data = pd.read_csv(self.file_path, nrows=NUM_SAMPLES)
            print(f"Loaded file: {self.file_path}, with first {NUM_SAMPLES} rows")
            self.select_column_button.config(state="normal")  # Enable "Select Columns" button

    def select_column(self):
        if self.data is None or not hasattr(self.data, 'columns'):
            messagebox.showerror("No Data", "No CSV file loaded")
            return

        columns = list(self.data.columns)
        selector = SelectColumnsWindow(self.root, columns)
        self.root.wait_window(selector)

        self.selected_columns = selector.selected_columns
        print("Selected columns:", self.selected_columns)

        if self.selected_columns:
            self.histogram_button.config(state="normal")  # Enable "Histogram" button
            self.fft_button.config(state="normal")  # Enable "FFT Spectrum" button

    def save_plot(self, fig, filename):
        fig.savefig(filename)
        print("Plot Saved", f"Plot saved to {filename}")

    def histogram(self):
        if not hasattr(self, 'data'):
            messagebox.showerror("No Data", "No CSV file loaded")
            return

        if not self.selected_columns:
            messagebox.showerror("No Columns", "No columns selected for analysis")
            return

        for column in self.selected_columns:
            hist = create_histogram(self.data, column)
            self.save_plot(hist, f"{column}_histogram.png")

    def fft(self):
        if not hasattr(self, 'data'):
            messagebox.showerror("No Data", "No CSV file loaded")
            return

        if not self.selected_columns:
            messagebox.showerror("No Columns", "No columns selected for analysis")
            return

        for column in self.selected_columns:
            fft_plot = calculate_fft(self.data, column)
            self.save_plot(fft_plot, f"{column}_fft.png")

    def S_param(self):
        if not hasattr(self, 'data'):
            messagebox.showerror("No Data", "No CSV file loaded")
            return

        if not self.selected_columns:
            messagebox.showerror("No Columns", "No columns selected for analysis")
            return

        for column in self.selected_columns:
            show_S(self.data, column)

    def time_domain(self):
        if not hasattr(self, 'data'):
            messagebox.showerror("No Data", "No CSV file loaded")
            return

        if not self.selected_columns:
            messagebox.showerror("No Columns", "No columns selected for analysis")
            return

        for column in self.selected_columns:
            time_domain_gating(self.data, column)

    def frequency_domain(self):
        if not hasattr(self, 'data'):
            messagebox.showerror("No Data", "No CSV file loaded")
            return

        if not self.selected_columns:
            messagebox.showerror("No Columns", "No columns selected for analysis")
            return

        for column in self.selected_columns:
            frequency_domain_back(self.data, column)        
        