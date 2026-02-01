import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import os

# Matplotlib
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
        
        # Store a LIST of traces
        self.traces = [] 
        
        self.setup_layout()
        
    def setup_layout(self):
        # --- LEFT PANEL ---
        control_frame = ttk.Frame(self.root, padding=10)
        control_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        # Load / Clear
        self.btn_load = ttk.Button(control_frame, text="Add Trace (CSV)", command=self.load_csv)
        self.btn_load.pack(pady=5, fill=tk.X)
        
        self.btn_clear = ttk.Button(control_frame, text="Clear All", command=self.clear_all)
        self.btn_clear.pack(pady=5, fill=tk.X)

        # DC Offset Checkbox
        self.remove_dc_var = tk.BooleanVar(value=True)
        self.chk_dc = ttk.Checkbutton(control_frame, text="Remove DC (Time Dom.)", 
                                      variable=self.remove_dc_var, command=self.refresh_plot_event)
        self.chk_dc.pack(pady=10, anchor="w")

      
        # --- RESTORED: Peak Slider ---
        ttk.Label(control_frame, text="Max Peaks to Label:").pack(pady=(15, 0))
        self.peak_slider = tk.Scale(
            control_frame, from_=0, to=10, orient=tk.HORIZONTAL, 
            command=self.on_slider_change
        )
        self.peak_slider.set(5)
        self.peak_slider.pack(pady=5, fill=tk.X)
        # -----------------------------
        
        # --- RIGHT PANEL (Plot) ---
        plot_frame = ttk.Frame(self.root)
        plot_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.fig = Figure(figsize=(8, 6), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.grid(True)
        
# 1. Create the canvas FIRST
        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
        self.canvas.draw()
        
        # 2. Pack the widget
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # 3. Setup toolbar
        toolbar = NavigationToolbar2Tk(self.canvas, plot_frame)
        toolbar.update()
        
        # 4. NOW connect the event listener (Canvas must exist!)
        self.fig.canvas.mpl_connect('pick_event', self.on_pick)

    def load_csv(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if not file_path:
            return
            
        try:
            # 1. Preview Headers
            df_preview = pd.read_csv(file_path, nrows=5)
            columns = list(df_preview.columns)
            filename = os.path.basename(file_path)
            
            # 2. Open Mapper Dialog
            dialog = loader_gui.ColumnMapperDialog(self.root, columns, filename)
            self.root.wait_window(dialog)
            
            if not dialog.result: return
                
            # 3. Load Data
            map_data = dialog.result
            full_df = pd.read_csv(file_path, nrows=config.NUM_SAMPLES)
            
            # 4. Create Trace
            if map_data['domain'] == "time":
                new_trace = trace_model.Trace.from_time_domain(
                    name=filename,
                    time_data=full_df[map_data['x_col']].values,
                    volt_data=full_df[map_data['y_col']].values,
                    # NO SAMPLE RATE PASSED - Calculated automatically now!
                    remove_dc=self.remove_dc_var.get()
                )
            else:
                new_trace = trace_model.Trace.from_freq_domain(
                    name=filename,
                    freq_data=full_df[map_data['x_col']].values,
                    mag_data=full_df[map_data['y_col']].values
                )
            
            self.traces.append(new_trace)
            self.refresh_plot()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load: {e}")
            print(e)

    def clear_all(self):
        self.traces = []
        self.refresh_plot()

    def on_slider_change(self, val):
        self.refresh_plot()

    def on_pick(self, event):
        # Identify the trace from the legend label
        trace_name = event.artist.get_label()
        print(f"Clicked trace: {trace_name}") # <--- DEBUG LINE
        
        for trace in self.traces:
            # Toggle logic: click the same one to de-select, or click a new one
            if trace.name == trace_name:
                trace.is_active = not trace.is_active
            else:
                trace.is_active = False
        
        self.refresh_plot()
        
    def refresh_plot_event(self):
        # Wrapper for checkbox command (doesn't pass arguments)
        self.refresh_plot()

    def refresh_plot(self):
        # 1. Check if user is currently zoomed in
        current_xlim = self.ax.get_xlim()
        current_ylim = self.ax.get_ylim()
        is_zoomed = (current_xlim != (0.0, 1.0)) and (current_xlim[1] > 1.0)
        
        self.ax.clear()
        
        n_peaks = int(self.peak_slider.get())
        search_range = current_xlim if is_zoomed else None
        global_max_freq = 0
        
        # 2. Plot EVERY trace
        for trace in self.traces:
            if len(trace.freqs) == 0: continue
            
            # Update global max for scaling
            max_f = trace.freqs[-1] 
            if max_f > global_max_freq:
                global_max_freq = max_f
            
            # --- ACTIVE TRACE LOGIC ---
            # If no trace is active, treat them all as visible. 
            # If one is active, fade the others.
            has_active = any(t.is_active for t in self.traces)
            
            if not has_active or trace.is_active:
                alpha = 1.0
                lw = 1.5
                zorder = 5
            else:
                alpha = 0.2  # Faded
                lw = 0.7
                zorder = 2

            # Plot with dynamic styles
            line, = self.ax.plot(
                trace.freqs, 
                trace.mags, 
                label=trace.name, 
                linewidth=lw, 
                alpha=alpha,
                zorder=zorder
            )
            trace_color = line.get_color()
            
            # Only show peaks for the active trace (to avoid clutter)
            if n_peaks > 0 and (trace.is_active or not has_active):
                top_peaks = analysis.get_top_peaks(
                    trace.freqs, 
                    trace.mags, 
                    top_n=n_peaks, 
                    min_dist_hz=500, 
                    freq_range=search_range
                )
                
                for freq, mag in top_peaks:
                    self.ax.plot(freq, mag, "x", color=trace_color, zorder=zorder)
                    self.ax.annotate(
                        f"{freq/1000:.1f}k", 
                        xy=(freq, mag), 
                        xytext=(0, 10), 
                        textcoords="offset points", 
                        ha='center', 
                        color=trace_color, 
                        fontsize=8,
                        rotation=90,
                        fontweight='bold',
                        zorder=zorder + 1
                    )

        # 3. Formatting
        self.ax.set_title("Spectrum Comparison")
        self.ax.set_xlabel("Frequency (Hz)")
        self.ax.set_ylabel("Magnitude")
        self.ax.grid(True, alpha=0.3)
        
        if self.traces:
            leg = self.ax.legend(fancybox=True, shadow=True)
            # Enable legend picking
            for legline in leg.get_lines():
                legline.set_picker(True)
                legline.set_pickradius(10)
            
        # 4. Critical Scaling Fix
        if is_zoomed:
            self.ax.set_xlim(current_xlim)
            self.ax.set_ylim(current_ylim)
        else:
            self.ax.relim()
            self.ax.autoscale_view(scalex=False, scaley=True) 
            if global_max_freq > 0:
                self.ax.set_xlim(left=0, right=global_max_freq)
            
        self.canvas.draw()