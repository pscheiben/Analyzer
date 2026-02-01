import tkinter as tk
from tkinter import ttk

class ColumnMapperDialog(tk.Toplevel):
    def __init__(self, parent, columns, filename):
        super().__init__(parent)
        self.title(f"Import Settings")
        self.geometry("350x250")
        self.columns = columns
        self.result = None
        
        # UI Layout
        ttk.Label(self, text=f"File: {filename}", font=("Arial", 10, "bold")).pack(pady=10)
        ttk.Label(self, text="Map your CSV columns:").pack(pady=5)
        
        # X-Axis Selection (e.g., Time or Frequency)
        frame_x = ttk.Frame(self)
        frame_x.pack(pady=5, fill=tk.X, padx=20)
        ttk.Label(frame_x, text="X-Axis Data:").pack(side=tk.LEFT)
        self.x_var = tk.StringVar()
        self.x_combo = ttk.Combobox(frame_x, textvariable=self.x_var, values=columns, state="readonly")
        self.x_combo.pack(side=tk.RIGHT)
        if columns: self.x_combo.current(0)
        
        # Y-Axis Selection (e.g., Voltage or dBm)
        frame_y = ttk.Frame(self)
        frame_y.pack(pady=5, fill=tk.X, padx=20)
        ttk.Label(frame_y, text="Y-Axis Data:").pack(side=tk.LEFT)
        self.y_var = tk.StringVar()
        self.y_combo = ttk.Combobox(frame_y, textvariable=self.y_var, values=columns, state="readonly")
        self.y_combo.pack(side=tk.RIGHT)
        if len(columns) > 1: self.y_combo.current(1)
        
        # Domain Type Selection
        self.type_var = tk.StringVar(value="time")
        frame_type = ttk.LabelFrame(self, text="Data Type")
        frame_type.pack(pady=10, fill=tk.X, padx=20)
        
        ttk.Radiobutton(frame_type, text="Time Domain (PicoScope)\n-> Will Perform FFT", 
                        variable=self.type_var, value="time").pack(anchor=tk.W, padx=5, pady=2)
        
        ttk.Radiobutton(frame_type, text="Frequency Domain (Spectrum Analyzer)\n-> No FFT needed", 
                        variable=self.type_var, value="freq").pack(anchor=tk.W, padx=5, pady=2)

        # Confirm Button
        ttk.Button(self, text="Import Trace", command=self.on_confirm).pack(pady=10)

    def on_confirm(self):
        self.result = {
            'x_col': self.x_var.get(),
            'y_col': self.y_var.get(),
            'domain': self.type_var.get()
        }
        self.destroy()