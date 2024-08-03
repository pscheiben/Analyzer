import tkinter as tk    # Import the tkinter module as tk
import pandas as pd     # Import the pandas module as pd
from tkinter import filedialog, simpledialog, messagebox  # Import the filedialog and messagebox modules from tkinter
from modules.analysis import create_histogram, calculate_fft, calculate_power_spectrum, calculate_psd # Import the create_histogram, calculate_fft, calculate_power_spectrum, and calculate_psd functions from the modules.analysis module
from modules.column_selector import SelectColumnsWindow

NUM_SAMPLES = 524288
SAMPLE_FREQ = 250000

class AnalyzerApp: # Define a new class named CSVAnalyzerApp
    def __init__(self, root): # Define the __init__ method with the self and root parameters
        self.root = root  # Set the root attribute to the value of the root parameter
        self.root.title("Analyzer") # Set the title of the root window to "CSV Analyzer"
        self.create_widgets() # Call the create_widgets method to create the widgets
        self.selected_columns = [] # Initialize the selected_columns attribute as an empty list

    def create_widgets(self): # Define the create_widgets method with the self parameter
        self.load_button = tk.Button(self.root, text="Load CSV", command=self.load_csv) # Create a new Button widget with the text "Load CSV" and the command self.load_csv
        self.load_button.grid(row=0, column=0, padx=5, pady=5) # Pack the load_button widget into the root window

        self.select_column_button = tk.Button(self.root, text="Select Columns", command=self.select_column)
        self.select_column_button.grid(row=1, column=0, padx=5, pady=5)
        self.select_column_button.grid_forget()

        self.histogram_button = tk.Button(self.root, text="Histogram", command=self.histogram) # Create a new Button widget with the text "Analyze" and the command self.analyze
        self.histogram_button.grid(row=2, column=0, padx=5, pady=5) # Pack the analyze_button widget into the root window
        self.histogram_button.grid_forget()

        self.fft_button = tk.Button(self.root, text="FFT Spectrum", command=self.fft) # Create a new Button widget with the text "Analyze" and the command self.analyze
        self.fft_button.grid(row=2, column=0, padx=5, pady=5) # Pack the analyze_button widget into the root window
        self.fft_button.grid_forget()

        self.exit_button = tk.Button(self.root, text="Exit", command=self.root.quit) # Create a new Button widget with the text "Exit" and the command self.root.quit
        self.exit_button.grid(row=3, column=1, padx=5, pady=5, ) # Pack the exit_button widget into the root window

    def load_csv(self): # Define the load_csv method with the self parameter
        self.file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")]) # Open a file dialog to select a CSV file and store the file path in the file_path attribute
        if self.file_path: # If a file path was selected
            self.data = pd.read_csv(self.file_path, nrows=NUM_SAMPLES)
            print(f"Loaded file: {self.file_path}, with first {NUM_SAMPLES} rows")
            self.select_column_button.grid(row=1, column=0, padx=5, pady=5)

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
            self.histogram_button.grid(row=2, column=0, padx=5, pady=5)
            self.fft_button.grid(row=2, column=1, padx=5, pady=5)

    def save_plot(self, fig, filename):
        fig.savefig(filename)
        print("Plot Saved", f"Plot saved to {filename}")

    def histogram(self): # Define the analyze method with the self parameter
        if not hasattr(self, 'data'): # If the data attribute does not exist
            messagebox.showerror("No Data", "No CSV file loaded") # Show an error message box
            return # Exit the method

        if not self.selected_columns:
            messagebox.showerror("No Columns", "No columns selected for analysis")
            return

        for column in self.selected_columns:
            hist = create_histogram(self.data, column)
            self.save_plot(hist, f"{column}_histogram.png")

    def fft(self): # Define the analyze method with the self parameter
        if not hasattr(self, 'data'):
            messagebox.showerror("No Data", "No CSV file loaded")
            return
        
        if not self.selected_columns:
            messagebox.showerror("No Columns", "No columns selected for analysis")
            return
        
        for column in self.selected_columns:
            fft_plot = calculate_fft(self.data, column)
            self.save_plot(fft_plot, f"{column}_fft.png")
            
    
