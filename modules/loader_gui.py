import tkinter as tk
from tkinter import ttk

class ColumnMapperDialog(tk.Toplevel):
    def __init__(self, parent, columns, filename):
        super().__init__(parent)
        self.title(f"Import Settings")
        
        # --- FIXED: Increased size from 350x250 to 450x450 ---
        self.geometry("450x450")
        self.minsize(400, 300) # Prevent it from getting too small
        # -----------------------------------------------------
        
        self.columns = columns
        self.result = None
        
        # UI Layout
        # Using a main frame with padding ensures content doesn't touch the window edges
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text=f"File: {filename}", font=("Arial", 10, "bold")).pack(pady=(0, 10))
        ttk.Label(main_frame, text="Map your CSV columns:").pack(pady=(0, 5))
        
        # X-Axis Selection
        frame_x = ttk.Frame(main_frame)
        frame_x.pack(pady=5, fill=tk.X)
        ttk.Label(frame_x, text="X-Axis Data:").pack(side=tk.LEFT)
        self.x_var = tk.StringVar()
        self.x_combo = ttk.Combobox(frame_x, textvariable=self.x_var, values=columns, state="readonly", width=25)
        self.x_combo.pack(side=tk.RIGHT)
        if columns: self.x_combo.current(0)
        
        # Y-Axis Selection
        frame_y = ttk.Frame(main_frame)
        frame_y.pack(pady=5, fill=tk.X)
        ttk.Label(frame_y, text="Y-Axis Data:").pack(side=tk.LEFT)
        self.y_var = tk.StringVar()
        self.y_combo = ttk.Combobox(frame_y, textvariable=self.y_var, values=columns, state="readonly", width=25)
        self.y_combo.pack(side=tk.RIGHT)
        if len(columns) > 1: self.y_combo.current(1)
        
        # Domain Type Selection
        self.type_var = tk.StringVar(value="time")
        frame_type = ttk.LabelFrame(main_frame, text="Data Type", padding=10)
        frame_type.pack(pady=15, fill=tk.X)
        
        ttk.Radiobutton(frame_type, text="Time Domain (PicoScope)\n-> Will Perform FFT", 
                        variable=self.type_var, value="time").pack(anchor=tk.W, pady=2)
        
        ttk.Radiobutton(frame_type, text="Frequency Domain (Spectrum Analyzer)\n-> No FFT needed", 
                        variable=self.type_var, value="freq").pack(anchor=tk.W, pady=2)

        # Confirm Button
        ttk.Button(main_frame, text="Import Trace", command=self.on_confirm).pack(side=tk.BOTTOM, pady=10)

    def on_confirm(self):
        self.result = {
            'x_col': self.x_var.get(),
            'y_col': self.y_var.get(),
            'domain': self.type_var.get()
        }
        self.destroy()