import tkinter as tk    # Import the tkinter module as tk
from tkinter import filedialog, messagebox  # Import the filedialog and messagebox modules from tkinter
from modules.file_operations import read_csv, save_plot # Import the read_csv and save_plot functions from the modules.file_operations module
from modules.analysis import create_histogram, calculate_fft, calculate_power_spectrum, calculate_psd # Import the create_histogram, calculate_fft, calculate_power_spectrum, and calculate_psd functions from the modules.analysis module
from modules.visualization import plot_histogram, plot_fft, plot_power_spectrum, plot_psd # Import the plot_histogram, plot_fft, plot_power_spectrum, and plot_psd functions from the modules.visualization module

class CSVAnalyzerApp: # Define a new class named CSVAnalyzerApp
    def __init__(self, root): # Define the __init__ method with the self and root parameters
        self.root = root  # Set the root attribute to the value of the root parameter
        self.root.title("CSV Analyzer") # Set the title of the root window to "CSV Analyzer"
        self.create_widgets() # Call the create_widgets method to create the widgets

    def create_widgets(self): # Define the create_widgets method with the self parameter
        self.load_button = tk.Button(self.root, text="Load CSV", command=self.load_csv) # Create a new Button widget with the text "Load CSV" and the command self.load_csv
        self.load_button.pack() # Pack the load_button widget into the root window

        self.analyze_button = tk.Button(self.root, text="Analyze", command=self.analyze) # Create a new Button widget with the text "Analyze" and the command self.analyze
        self.analyze_button.pack() # Pack the analyze_button widget into the root window

        self.compare_button = tk.Button(self.root, text="Compare", command=self.compare) # Create a new Button widget with the text "Compare" and the command self.compare
        self.compare_button.pack() # Pack the compare_button widget into the root window

    def load_csv(self): # Define the load_csv method with the self parameter
        self.file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")]) # Open a file dialog to select a CSV file and store the file path in the file_path attribute
        if self.file_path: # If a file path was selected
            self.data = read_csv(self.file_path) # Read the CSV file using the read_csv function and store the data in the data attribute
            messagebox.showinfo("File Loaded", f"Loaded {self.file_path}") # Show an info message box with the file path

    def analyze(self): # Define the analyze method with the self parameter
        if not hasattr(self, 'data'): # If the data attribute does not exist
            messagebox.showerror("No Data", "No CSV file loaded") # Show an error message box
            return # Exit the method

        column = self.ask_column() # Call the ask_column method and store the result in the column variable
        if column: # If a column was selected
            hist = create_histogram(self.data, column)  # Create a histogram using the create_histogram function
            fig = plot_histogram(hist) # Plot the histogram using the plot_histogram function
            save_plot(fig, "histogram.png") # Save the histogram plot as "histogram.png"
            messagebox.showinfo("Analysis Complete", "Histogram saved as histogram.png") # Show an info message box

    def ask_column(self): # Define the ask_column method with the self parameter
        # Simple prompt to ask for column name
        column = tk.simpledialog.askstring("Input", "Enter column name:") # Prompt the user to enter a column name
        if column and column in self.data.columns: # If a column name was entered and it exists in the CSV data
            return column   # Return the column name
        messagebox.showerror("Invalid Column", "Column not found in CSV") # Show an error message box
        return None
