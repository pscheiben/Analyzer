import tkinter as tk
from gui import AnalyzerApp

if __name__ == "__main__":
    root = tk.Tk()
    
    # Optional: Set initial window size
    root.geometry("1000x700")
    
    app = AnalyzerApp(root)
    root.mainloop()