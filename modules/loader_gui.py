import tkinter as tk
from tkinter import ttk, messagebox

class ColumnMapperDialog(tk.Toplevel):
    def __init__(self, parent, columns, filename):
        super().__init__(parent)
        self.title(f"Import Settings")
        
        self.geometry("450x500") 
        self.minsize(350, 500) 
        
        self.columns = columns
        self.result = None
        
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text=f"File: {filename}", font=("Arial", 10, "bold")).pack(pady=(0, 10))
        
        # --- Data Type Selection ---
        type_frame = ttk.LabelFrame(main_frame, text="Data Type", padding=10)
        type_frame.pack(fill=tk.X, pady=5)
        
        self.data_type_var = tk.StringVar(value="time")
        
        rb_time = ttk.Radiobutton(type_frame, text="Time Domain (Oscilloscope)", 
                                  variable=self.data_type_var, value="time", 
                                  command=self.update_ui_state)
        rb_time.pack(anchor="w", pady=2)
        
        rb_freq = ttk.Radiobutton(type_frame, text="Frequency Domain (Spectrum Analyzer)", 
                                  variable=self.data_type_var, value="freq", 
                                  command=self.update_ui_state)
        rb_freq.pack(anchor="w", pady=2)

        # --- Column Mapping ---
        self.lbl_map = ttk.Label(main_frame, text="Map your CSV columns:")
        self.lbl_map.pack(pady=(10, 5))
        
        # X-Axis
        frame_x = ttk.Frame(main_frame)
        frame_x.pack(pady=5, fill=tk.X)
        self.lbl_x = ttk.Label(frame_x, text="X-Axis (Time):")
        self.lbl_x.pack(side=tk.LEFT)
        self.x_var = tk.StringVar()
        self.x_combo = ttk.Combobox(frame_x, textvariable=self.x_var, values=columns, state="readonly", width=25)
        self.x_combo.pack(side=tk.RIGHT)
        if columns: self.x_combo.current(0)
        
        # Y-Axis
        frame_y = ttk.Frame(main_frame)
        frame_y.pack(pady=5, fill=tk.X)
        self.lbl_y = ttk.Label(frame_y, text="Y-Axis (Volts):")
        self.lbl_y.pack(side=tk.LEFT)
        self.y_var = tk.StringVar()
        self.y_combo = ttk.Combobox(frame_y, textvariable=self.y_var, values=columns, state="readonly", width=25)
        self.y_combo.pack(side=tk.RIGHT)
        if len(columns) > 1: self.y_combo.current(1)
        
        # --- Sampling Frequency Section (Time Domain Only) ---
        self.frame_fs = ttk.LabelFrame(main_frame, text="Time Domain Settings", padding=10)
        self.frame_fs.pack(pady=15, fill=tk.X)
        
        ttk.Label(self.frame_fs, text="Sampling Freq (Hz):").pack(side=tk.LEFT)
        self.fs_var = tk.StringVar(value="250000")
        self.fs_entry = ttk.Entry(self.frame_fs, textvariable=self.fs_var, width=15)
        self.fs_entry.pack(side=tk.LEFT, padx=5)

        # Confirm Button
        ttk.Button(main_frame, text="Import & Analyze", command=self.on_confirm).pack(side=tk.BOTTOM, pady=10)
        
        # Initialize UI state
        self.update_ui_state()

    def update_ui_state(self):
        """Updates labels and enables/disables fields based on Data Type."""
        if self.data_type_var.get() == "freq":
            self.lbl_x.config(text="X-Axis (Frequency):")
            self.lbl_y.config(text="Y-Axis (Magnitude):")
            # Hide or disable Sample Rate settings
            for child in self.frame_fs.winfo_children():
                child.configure(state='disabled')
        else:
            self.lbl_x.config(text="X-Axis (Time):")
            self.lbl_y.config(text="Y-Axis (Volts):")
            for child in self.frame_fs.winfo_children():
                child.configure(state='normal')

    def on_confirm(self):
        mode = self.data_type_var.get()
        fs_val = None
        
        if mode == "time":
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
            'sample_rate': fs_val,
            'is_freq_domain': (mode == "freq")
        }
        self.destroy()