from modules.gui import AnalyzerApp  # Import the CSVAnalyzerApp class from the gui module
import tkinter as tk            # Import the tkinter module as tk

if __name__ == "__main__":      # If the script is being run as the main program
    root = tk.Tk()              # Create a new Tkinter root window
    app = AnalyzerApp(root)  # Create a new instance of the CSVAnalyzerApp class
    root.mainloop()             # Start the Tkinter main event loop