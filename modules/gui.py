import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import numpy as np
import os

# Matplotlib
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

# Custom Modules
import analysis
import config
import loader_gui
import trace_model 

class AnalyzerApp:
    def __init__(self, root):
        self.root = root
        self.root.title(f"Peter's Analyzer & Comparator - v{config.VERSION}")
        self.traces = [] 
        self.setup_layout()
        
    def setup_layout(self):
        # --- LEFT PANEL ---
        control_frame = ttk.Frame(self.root, padding=10)
        control_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        self.btn_load = ttk.Button(control_frame, text="Add Trace (CSV)", command=self.load_csv)
        self.btn_load.pack(pady=5, fill=tk.X)
        
        self.btn_clear = ttk.Button(control_frame, text="Clear All", command=self.clear_all)
        self.btn_clear.pack(pady=5, fill=tk.X)

        # New Reset View Button
        self.btn_reset = ttk.Button(control_frame, text="Reset View", command=self.reset_view)
        self.btn_reset.pack(pady=5, fill=tk.X)

        self.remove_dc_var = tk.BooleanVar(value=True)
        
        ttk.Separator(control_frame, orient='horizontal').pack(fill=tk.X, pady=10)
        ttk.Label(control_frame, text="Toggle Traces:").pack(anchor="w")
        
        self.trace_list_frame = ttk.Frame(control_frame)
        self.trace_list_frame.pack(fill=tk.BOTH, expand=True, pady=5)
      
        ttk.Label(control_frame, text="Max Peaks to Label:").pack(pady=(15, 0))
        self.peak_slider = tk.Scale(
            control_frame, from_=0, to=10, orient=tk.HORIZONTAL, 
            command=self.on_slider_change
        )
        self.peak_slider.set(5)
        self.peak_slider.pack(pady=5, fill=tk.X)
        
        # --- Reference Selection ---
        ttk.Separator(control_frame, orient='horizontal').pack(fill=tk.X, pady=10)
        ttk.Label(control_frame, text="Reference Trace:").pack(anchor="w")

        self.ref_var = tk.StringVar(value="None")
        self.ref_combo = ttk.Combobox(control_frame, textvariable=self.ref_var, state="readonly")
        self.ref_combo['values'] = ["None"]
        self.ref_combo.pack(pady=5, fill=tk.X)
        self.ref_combo.bind("<<ComboboxSelected>>", self.refresh_plot_event)

        # --- RIGHT PANEL (Plot) ---
        plot_frame = ttk.Frame(self.root)
        plot_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.fig = Figure(figsize=(8, 6), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.grid(True)
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.toolbar = NavigationToolbar2Tk(self.canvas, plot_frame)
        self.toolbar.update()
        
        self.fig.canvas.mpl_connect('pick_event', self.on_pick)

    def update_trace_list(self):
        for widget in self.trace_list_frame.winfo_children():
            widget.destroy()

        for trace in self.traces:
            var = tk.BooleanVar(value=trace.visible)
            def toggle_cmd(t=trace, v=var):
                t.visible = v.get()
                self.refresh_plot()

            chk = ttk.Checkbutton(self.trace_list_frame, text=trace.name, 
                                  variable=var, command=toggle_cmd)
            chk.pack(anchor="w", pady=2)

        trace_names = ["None"] + [t.name for t in self.traces]
        self.ref_combo['values'] = trace_names
        
        if self.ref_var.get() not in trace_names:
            self.ref_var.set("None")
    
    def load_csv(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if not file_path: return
            
        try:
            df_preview = pd.read_csv(file_path, nrows=5)
            columns = list(df_preview.columns)
            filename = os.path.basename(file_path)
            
            dialog = loader_gui.ColumnMapperDialog(self.root, columns, filename)
            self.root.wait_window(dialog)
            if not dialog.result: return
                
            map_data = dialog.result
            channel_name = map_data['y_col']
            trace_name = f"{filename}_{channel_name}"
            
            full_df = pd.read_csv(file_path, nrows=config.NUM_SAMPLES)
            
            if map_data['is_freq_domain']:
                new_trace = trace_model.Trace.from_freq_domain(
                    name=trace_name,
                    freq_data=full_df[map_data['x_col']].values,
                    mag_data=full_df[map_data['y_col']].values
                )
            else:
                new_trace = trace_model.Trace.from_time_domain(
                    name=trace_name,
                    time_data=full_df[map_data['x_col']].values,
                    volt_data=full_df[map_data['y_col']].values,
                    remove_dc=self.remove_dc_var.get(),
                    manual_sample_rate=map_data['sample_rate']
                )
            
            self.traces.append(new_trace)
            self.update_trace_list() 
            self.refresh_plot()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load: {e}")

    def clear_all(self):
        self.traces = []
        self.update_trace_list()
        self.refresh_plot()

    def reset_view(self):
        """Resets the plot to the standard dBV view range."""
        if not self.traces:
            return
        
        max_f = max([max(t.freqs) for t in self.traces if t.visible and len(t.freqs) > 0], default=1.0)
        self.ax.set_xlim(0, max_f)
        self.ax.set_ylim(-120, 30)
        self.canvas.draw()

    def on_slider_change(self, val):
        self.refresh_plot()

    def on_pick(self, event):
        trace_name = event.artist.get_label()
        for trace in self.traces:
            if trace.name == trace_name:
                trace.is_active = not trace.is_active
            else:
                trace.is_active = False
        self.refresh_plot()

    def refresh_plot_event(self, event=None):
        self.refresh_plot()

    def refresh_plot(self):
        current_xlim = self.ax.get_xlim()
        current_ylim = self.ax.get_ylim()
        
        # Check if user has manually zoomed (simple heuristic)
        is_zoomed = (current_xlim != (0.0, 1.0)) and (current_xlim[0] != 0.0 or current_xlim[1] > 1.0)
        
        self.ax.clear()
        n_peaks = int(self.peak_slider.get())
        search_range = current_xlim if is_zoomed else None
        global_max_freq = 0
        has_active = any(t.is_active for t in self.traces)
        active_trace = next((t for t in self.traces if t.is_active), None)

        ref_name = self.ref_var.get()
        ref_trace = next((t for t in self.traces if t.name == ref_name), None)
        
        for trace in self.traces:
            if not trace.visible or len(trace.freqs) == 0:
                continue
            
            if trace.freqs[-1] > global_max_freq:
                global_max_freq = trace.freqs[-1]
            
            if trace.color is None:
                cycle = plt.rcParams['axes.prop_cycle'].by_key()['color']
                trace.color = cycle[len(self.traces) % len(cycle)]

            if ref_trace and trace != ref_trace:
                if not np.array_equal(trace.freqs, ref_trace.freqs):
                     ref_mags_interp = np.interp(trace.freqs, ref_trace.freqs, ref_trace.mags)
                     display_mags = trace.mags - ref_mags_interp
                else:
                     display_mags = trace.mags - ref_trace.mags
                label_text = f"{trace.name} (Rel)"
            else:
                display_mags = trace.mags
                label_text = trace.name

            display_freqs = trace.freqs
            lw = 2.5 if trace.is_active else 1.0
            alpha = 1.0 if (trace.is_active or not has_active) else 0.4

            # Updated Noise Floor labeling (dBV)
            floor_val = analysis.get_noise_floor(display_mags)
            self.ax.axhline(floor_val, color=trace.color, linestyle='--', linewidth=0.8, alpha=0.5)

            self.ax.plot(
                display_freqs, display_mags, 
                label=label_text, 
                color=trace.color, 
                linewidth=lw, 
                alpha=alpha, 
                zorder=5
            )
            
            if n_peaks > 0 and (trace.is_active or not has_active):
                top_peaks = analysis.get_top_peaks(
                    display_freqs, display_mags, 
                    top_n=n_peaks, min_dist_hz=500, 
                    freq_range=search_range
                )
                
                for freq, mag in top_peaks:
                    self.ax.plot(freq, mag, "x", color=trace.color, zorder=6)
                    self.ax.annotate(
                        f"{freq/1000:.1f}k\n({mag:.1f}dBV)", xy=(freq, mag), 
                        xytext=(0, 10), textcoords="offset points", 
                        ha='center', color=trace.color, 
                        fontsize=8, rotation=0, fontweight='bold', zorder=7
                    )

        self.ax.set_title("Spectrum Analysis (dBV Ref 1V)" if ref_name == "None" else f"Comparison (Ref: {ref_name})")
        self.ax.set_xlabel("Frequency (Hz)")
        self.ax.set_ylabel("Magnitude (dBV)" if ref_name == "None" else "Relative Magnitude (dB)")
        self.ax.grid(True, alpha=0.3)
        
        if any(t.visible for t in self.traces):
            leg = self.ax.legend(fancybox=True, shadow=True)
            for legline in leg.get_lines():
                legline.set_picker(True)
                legline.set_pickradius(10)
            
        # Apply the new requested scale logic
        if is_zoomed:
            self.ax.set_xlim(current_xlim)
            self.ax.set_ylim(current_ylim)
        elif active_trace:
            self.ax.set_xlim(left=0, right=max(active_trace.freqs))
            # New Absolute dBV range
            self.ax.set_ylim(bottom=-120, top=30) 
        else:
            self.ax.relim()
            self.ax.autoscale_view(scalex=False, scaley=False)
            if global_max_freq > 0:
                self.ax.set_xlim(left=0, right=global_max_freq)
                                   
            # Explicitly force your window here
            self.ax.set_ylim(bottom=-120, top=30)
            
        self.canvas.draw()