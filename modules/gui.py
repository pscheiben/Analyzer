import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import os

# Matplotlib
import matplotlib.pyplot as plt  # <--- FIXED: Added this import
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
        self.root.title("PicoScope Analyzer & Comparator")
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

        self.remove_dc_var = tk.BooleanVar(value=True)
        self.chk_dc = ttk.Checkbutton(control_frame, text="Remove DC (Time Dom.)", 
                                      variable=self.remove_dc_var, command=self.refresh_plot_event)
        self.chk_dc.pack(pady=10, anchor="w")

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
        
        # --- RIGHT PANEL (Plot) ---
        plot_frame = ttk.Frame(self.root)
        plot_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.fig = Figure(figsize=(8, 6), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.grid(True)
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        toolbar = NavigationToolbar2Tk(self.canvas, plot_frame)
        toolbar.update()
        
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
            
            # Uniqueness check
            existing_names = [t.name for t in self.traces]
            if trace_name in existing_names:
                count = 1
                while f"{trace_name}_{count}" in existing_names: count += 1
                trace_name = f"{trace_name}_{count}"

            full_df = pd.read_csv(file_path, nrows=config.NUM_SAMPLES)
            
            if map_data['domain'] == "time":
                new_trace = trace_model.Trace.from_time_domain(
                    name=trace_name,
                    time_data=full_df[map_data['x_col']].values,
                    volt_data=full_df[map_data['y_col']].values,
                    remove_dc=self.remove_dc_var.get()
                )
            else:
                new_trace = trace_model.Trace.from_freq_domain(
                    name=trace_name,
                    freq_data=full_df[map_data['x_col']].values,
                    mag_data=full_df[map_data['y_col']].values
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

    def refresh_plot_event(self):
        self.refresh_plot()

    def refresh_plot(self):
        current_xlim = self.ax.get_xlim()
        current_ylim = self.ax.get_ylim()
        is_zoomed = (current_xlim != (0.0, 1.0)) and (current_xlim[1] > 1.0)
        
        self.ax.clear()
        n_peaks = int(self.peak_slider.get())
        search_range = current_xlim if is_zoomed else None
        global_max_freq = 0
        has_active = any(t.is_active for t in self.traces)
        
        for trace in self.traces:
            if not trace.visible or len(trace.freqs) == 0:
                continue
            
            if trace.freqs[-1] > global_max_freq:
                global_max_freq = trace.freqs[-1]
            
            # --- FIXED: Robust Color Assignment ---
            if trace.color is None:
                try:
                    # Try modern internal API
                    trace.color = next(self.ax._get_lines.prop_cycler)['color']
                except (AttributeError, StopIteration):
                    # Fallback to stable rcParams
                    cycle = plt.rcParams['axes.prop_cycle'].by_key()['color']
                    trace.color = cycle[len(self.traces) % len(cycle)]
            # ---------------------------------------

            lw = 2.5 if trace.is_active else 1.0
            alpha = 1.0 if (trace.is_active or not has_active) else 0.4

            self.ax.plot(
                trace.freqs, trace.mags, 
                label=trace.name, 
                color=trace.color, 
                linewidth=lw, 
                alpha=alpha, 
                zorder=5
            )
            
            if n_peaks > 0 and (trace.is_active or not has_active):
                top_peaks = analysis.get_top_peaks(
                    trace.freqs, trace.mags, 
                    top_n=n_peaks, min_dist_hz=500, 
                    freq_range=search_range
                )
                
                for freq, mag in top_peaks:
                    self.ax.plot(freq, mag, "x", color=trace.color, zorder=6)
                    self.ax.annotate(
                        f"{freq/1000:.1f}k", xy=(freq, mag), 
                        xytext=(0, 10), textcoords="offset points", 
                        ha='center', color=trace.color, 
                        fontsize=8, rotation=90, fontweight='bold', zorder=7
                    )

        self.ax.set_title("Spectrum Comparison")
        self.ax.set_xlabel("Frequency (Hz)")
        self.ax.set_ylabel("Magnitude")
        self.ax.grid(True, alpha=0.3)
        
        if any(t.visible for t in self.traces):
            leg = self.ax.legend(fancybox=True, shadow=True)
            for legline in leg.get_lines():
                legline.set_picker(True)
                legline.set_pickradius(10)
            
        active_trace = next((t for t in self.traces if t.is_active), None)

        if is_zoomed:
            self.ax.set_xlim(current_xlim)
            self.ax.set_ylim(current_ylim)
        elif active_trace:
            self.ax.set_xlim(left=0, right=max(active_trace.freqs))
            self.ax.set_ylim(bottom=0, top=max(active_trace.mags) * 1.1)
        else:
            self.ax.relim()
            self.ax.autoscale_view(scalex=False, scaley=True)
            if global_max_freq > 0:
                self.ax.set_xlim(left=0, right=global_max_freq)
            
        self.canvas.draw()