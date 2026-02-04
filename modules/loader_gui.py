import tkinter as tk
from tkinter import ttk

class ColumnMapperDialog(tk.Toplevel):
    def __init__(self, parent, columns, filename):
        super().__init__(parent)
        self.title(f"Import Settings")
        
        # Geometry
        self.geometry("450x500") # Slightly taller for new option
        self.minsize(400, 300) 
        
        self.columns = columns
        self.result = None
        
        # UI Layout
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text=f"File: {filename}", font=("Arial", 10, "bold")).pack(pady=(0, 10))
        
        # --- Column Mapping ---
        ttk.Label(main_frame, text="Map your CSV columns:").pack(pady=(0, 5))
        
        # X-Axis
        frame_x = ttk.Frame(main_frame)
        frame_x.pack(pady=5, fill=tk.X)
        ttk.Label(frame_x, text="X-Axis (Time/Freq):").pack(side=tk.LEFT)
        self.x_var = tk.StringVar()
        self.x_combo = ttk.Combobox(frame_x, textvariable=self.x_var, values=columns, state="readonly", width=25)
        self.x_combo.pack(side=tk.RIGHT)
        if columns: self.x_combo.current(0)
        
        # Y-Axis
        frame_y = ttk.Frame(main_frame)
        frame_y.pack(pady=5, fill=tk.X)
        ttk.Label(frame_y, text="Y-Axis (Volts/Mag):").pack(side=tk.LEFT)
        self.y_var = tk.StringVar()
        self.y_combo = ttk.Combobox(frame_y, textvariable=self.y_var, values=columns, state="readonly", width=25)
        self.y_combo.pack(side=tk.RIGHT)
        if len(columns) > 1: self.y_combo.current(1)
        
        # --- Data Type Section ---
        self.type_var = tk.StringVar(value="time")
        frame_type = ttk.LabelFrame(main_frame, text="Data Type", padding=10)
        frame_type.pack(pady=15, fill=tk.X)
        
        # Radio Buttons
        rb_time = ttk.Radiobutton(frame_type, text="Time Domain (Perform FFT)", 
                        variable=self.type_var, value="time", command=self.toggle_freq_input)
        rb_time.pack(anchor=tk.W, pady=2)
        
        # Sampling Frequency Input (Nested in the type frame)
        self.fs_frame = ttk.Frame(frame_type)
        self.fs_frame.pack(fill=tk.X, padx=20, pady=(0, 5))
        
        ttk.Label(self.fs_frame, text="Sampling Freq (Hz):").pack(side=tk.LEFT)
        self.fs_var = tk.StringVar()
        self.fs_entry = ttk.Entry(self.fs_frame, textvariable=self.fs_var, width=15)
        self.fs_entry.pack(side=tk.LEFT, padx=5)
        ttk.Label(self.fs_frame, text="(Leave empty to Auto-detect)").pack(side=tk.LEFT, padx=5)

        rb_freq = ttk.Radiobutton(frame_type, text="Frequency Domain (Already FFT)", 
                        variable=self.type_var, value="freq", command=self.toggle_freq_input)
        rb_freq.pack(anchor=tk.W, pady=2)

        # Confirm Button
        ttk.Button(main_frame, text="Import Trace", command=self.on_confirm).pack(side=tk.BOTTOM, pady=10)

        # Initialize state
        self.toggle_freq_input()

    def toggle_freq_input(self):
        """Enable/Disable sampling frequency input based on domain selection"""
        if self.type_var.get() == "time":
            self.fs_entry.config(state="normal")
        else:
            self.fs_entry.config(state="disabled")

    def on_confirm(self):
        # Handle Sampling Frequency input
        fs_val = None
        if self.type_var.get() == "time":
            val_str = self.fs_var.get().strip()
            if val_str:
                try:
                    fs_val = float(val_str)
                except ValueError:
                    tk.messagebox.showerror("Invalid Input", "Sampling Frequency must be a number.")
                    return

        self.result = {
            'x_col': self.x_var.get(),
            'y_col': self.y_var.get(),
            'domain': self.type_var.get(),
            'sample_rate': fs_val  # Pass the manual value (or None)
        }
        self.destroy()