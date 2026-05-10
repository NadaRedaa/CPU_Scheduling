import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import copy, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from Process import Process
from Validator import Validator
from SJF import SJF
from SRTF import SRTF
from RoundRobin import RoundRobin
from Metrics import Metrics
PROCESS_COLORS = [
    "#E74C3C", "#3498DB", "#2ECC71", "#F39C12",
    "#9B59B6", "#1ABC9C", "#E67E22", "#E91E63",
    "#00BCD4", "#FF5722",
]
BG         = "#F5F6FA"
PANEL_BG   = "#FFFFFF"
HDR_BG     = "#1A1F36"
HDR_FG     = "#FFFFFF"
ACCENT     = "#1A1F36"
ACCENT2    = "#3498DB"
SUCCESS    = "#27AE60"
DANGER     = "#E74C3C"
MUTED      = "#95A5A6"
BORDER     = "#E0E4EC"
ROW_ALT    = "#F8F9FD"
FONT_TITLE = ("Segoe UI", 16, "bold")
FONT_SUB   = ("Segoe UI", 10)
FONT_BOLD  = ("Segoe UI", 10, "bold")
FONT_LABEL = ("Segoe UI", 9, "bold")
FONT_SMALL = ("Segoe UI", 9)
FONT_MONO  = ("Consolas", 10)
class SchedulerApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("CPU Scheduling Simulator — RR vs SJF vs SRTF")
        self.root.configure(bg=BG)
        self.root.geometry("1150x900")
        self.root.minsize(900, 700)
        self.processes: list = []
        self._pid_color: dict = {}
        self._color_idx = 0
        self._setup_styles()
        self._build_ui()
    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview",
            background=PANEL_BG, foreground=ACCENT,
            fieldbackground=PANEL_BG, rowheight=26,
            font=FONT_SMALL, borderwidth=0)
        style.configure("Treeview.Heading",
            background=HDR_BG, foreground=HDR_FG,
            font=FONT_LABEL, relief="flat", padding=(6, 6))
        style.map("Treeview",
            background=[("selected", ACCENT2)],
            foreground=[("selected", "white")])
        style.configure("TEntry",
            fieldbackground=PANEL_BG, foreground=ACCENT,
            bordercolor=BORDER, relief="flat", padding=6)
        style.configure("TScrollbar",
            background=BORDER, troughcolor=BG, arrowsize=12)
    def _build_ui(self):
        outer = tk.Frame(self.root, bg=BG)
        outer.pack(fill="both", expand=True)
        cv = tk.Canvas(outer, bg=BG, highlightthickness=0)
        vsb = ttk.Scrollbar(outer, orient="vertical", command=cv.yview)
        cv.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        cv.pack(side="left", fill="both", expand=True)
        self.sf = tk.Frame(cv, bg=BG)
        win = cv.create_window((0, 0), window=self.sf, anchor="nw")
        self.sf.bind("<Configure>", lambda e: cv.configure(scrollregion=cv.bbox("all")))
        cv.bind("<Configure>", lambda e: cv.itemconfig(win, width=e.width))
        cv.bind_all("<MouseWheel>",
            lambda e: cv.yview_scroll(int(-1*(e.delta/120)), "units"))
        f = self.sf
        hdr = tk.Frame(f, bg=HDR_BG)
        hdr.pack(fill="x")
        tk.Label(hdr, text="CPU Scheduling Simulator",
                 font=FONT_TITLE, bg=HDR_BG, fg=HDR_FG, pady=14).pack()
        tk.Label(hdr, text="Round Robin  ·  SJF (Non-Preemptive)  ·  SRTF (Preemptive)",
                 font=FONT_SUB, bg=HDR_BG, fg="#8892B0").pack(pady=(0, 14))
        self._build_input_section(f)
        self._build_process_table_section(f)
        self._build_action_buttons(f)
        self._section_header(f, "4", "Ready Queue — Round Robin")
        self.rq_canvas_frame = self._panel(f)
        self.rq_placeholder = tk.Label(self.rq_canvas_frame,
            text="Run the scheduler to see the ready queue.",
            font=FONT_SMALL, fg=MUTED, bg=PANEL_BG, pady=10)
        self.rq_placeholder.pack()
        self._section_header(f, "5", "Gantt Chart — Round Robin")
        self.gantt_rr_frame = self._panel(f)
        self._gantt_placeholder(self.gantt_rr_frame)
        self._section_header(f, "6", "Gantt Chart — SJF (Non-Preemptive)")
        self.gantt_sjf_frame = self._panel(f)
        self._gantt_placeholder(self.gantt_sjf_frame)
        self._section_header(f, "7", "Gantt Chart — SRTF (Preemptive)")
        self.gantt_srtf_frame = self._panel(f)
        self._gantt_placeholder(self.gantt_srtf_frame)
        self._section_header(f, "8", "Results Table — Round Robin")
        self.tbl_rr_frame = self._panel(f, pady_bottom=4)
        self.tbl_rr = self._build_results_treeview(self.tbl_rr_frame)
        self.avg_rr_label = tk.Label(self.tbl_rr_frame, text="",
            font=FONT_BOLD, bg=PANEL_BG, fg=ACCENT2, anchor="e", padx=12)
        self.avg_rr_label.pack(fill="x", pady=(0, 8))
        self._section_header(f, "9", "Results Table — SJF (Non-Preemptive)")
        self.tbl_sjf_frame = self._panel(f, pady_bottom=4)
        self.tbl_sjf = self._build_results_treeview(self.tbl_sjf_frame)
        self.avg_sjf_label = tk.Label(self.tbl_sjf_frame, text="",
            font=FONT_BOLD, bg=PANEL_BG, fg=ACCENT2, anchor="e", padx=12)
        self.avg_sjf_label.pack(fill="x", pady=(0, 8))
        self._section_header(f, "10", "Results Table — SRTF (Preemptive)")
        self.tbl_srtf_frame = self._panel(f, pady_bottom=4)
        self.tbl_srtf = self._build_results_treeview(self.tbl_srtf_frame)
        self.avg_srtf_label = tk.Label(self.tbl_srtf_frame, text="",
            font=FONT_BOLD, bg=PANEL_BG, fg=ACCENT2, anchor="e", padx=12)
        self.avg_srtf_label.pack(fill="x", pady=(0, 8))
        self._section_header(f, "11", "Comparison Summary")
        self.cmp_frame = self._panel(f)
        tk.Label(self.cmp_frame,
            text="Run the scheduler to see the comparison.",
            font=FONT_SMALL, fg=MUTED, bg=PANEL_BG, pady=10).pack()
        self._section_header(f, "12", "Final Conclusion")
        self.conclusion_frame = self._panel(f, pady_bottom=20)
        self.conclusion_box = tk.Text(self.conclusion_frame,
            height=9, font=FONT_MONO, bg=ROW_ALT, fg=ACCENT,
            relief="flat", bd=0, padx=14, pady=10,
            wrap="word", state="disabled")
        self.conclusion_box.pack(fill="x", padx=8, pady=8)
    def _panel(self, parent, pady_bottom=10):
        frame = tk.Frame(parent, bg=PANEL_BG,
                         highlightbackground=BORDER, highlightthickness=1)
        frame.pack(fill="x", padx=20, pady=(0, pady_bottom))
        return frame
    def _section_header(self, parent, num: str, title: str):
        row = tk.Frame(parent, bg=BG)
        row.pack(fill="x", padx=20, pady=(10, 2))
        tk.Label(row, text=f" {num} ",
                 font=("Segoe UI", 9, "bold"),
                 bg=ACCENT2, fg="white", padx=6, pady=2).pack(side="left")
        tk.Label(row, text=f"  {title}",
                 font=FONT_BOLD, bg=BG, fg=ACCENT).pack(side="left")
    def _gantt_placeholder(self, frame):
        tk.Label(frame, text="Gantt chart will appear here after running.",
                 font=FONT_SMALL, fg=MUTED, bg=PANEL_BG, pady=12).pack()
    def _build_results_treeview(self, parent) -> ttk.Treeview:
        cols = ("PID", "Arrival", "Burst", "Start", "Finish", "RT", "TAT", "WT")
        tbl = ttk.Treeview(parent, columns=cols, show="headings", height=4)
        for c in cols:
            tbl.heading(c, text=c)
            tbl.column(c, width=100, anchor="center")
        tbl.tag_configure("avg", background="#EBF5FB", font=FONT_BOLD)
        tbl.tag_configure("alt", background=ROW_ALT)
        tbl.pack(fill="x", padx=8, pady=(8, 2))
        return tbl
    def _build_input_section(self, parent):
        panel = tk.LabelFrame(parent,
            text="  Sections 1 & 2  —  Input Panel + Quantum  ",
            font=FONT_LABEL, bg=PANEL_BG, fg=ACCENT,
            highlightbackground=BORDER, bd=1, relief="solid",
            padx=16, pady=12)
        panel.pack(fill="x", padx=20, pady=(10, 0))
        for col, lbl in enumerate(["PID", "Arrival Time", "Burst Time"]):
            tk.Label(panel, text=lbl, font=FONT_LABEL,
                     bg=PANEL_BG, fg=ACCENT).grid(
                     row=0, column=col, padx=10, pady=(0, 4), sticky="w")
        self.ent_pid     = ttk.Entry(panel, width=12, font=FONT_SMALL)
        self.ent_arrival = ttk.Entry(panel, width=12, font=FONT_SMALL)
        self.ent_burst   = ttk.Entry(panel, width=12, font=FONT_SMALL)
        self.ent_pid.grid    (row=1, column=0, padx=10, pady=2, sticky="w")
        self.ent_arrival.grid(row=1, column=1, padx=10, pady=2, sticky="w")
        self.ent_burst.grid  (row=1, column=2, padx=10, pady=2, sticky="w")
        for e in (self.ent_pid, self.ent_arrival, self.ent_burst):
            e.bind("<Return>", lambda ev: self._add_process())
        tk.Button(panel, text="＋  Add Process",
                  font=FONT_LABEL, bg=ACCENT2, fg="white",
                  relief="flat", padx=12, pady=5, cursor="hand2",
                  activebackground="#2980B9", activeforeground="white",
                  command=self._add_process).grid(
                  row=1, column=3, padx=14, pady=2)
        sep = tk.Frame(panel, bg=BORDER, height=1)
        sep.grid(row=2, column=0, columnspan=5, sticky="ew", pady=10)
        tk.Label(panel, text="Time Quantum  (Round Robin)",
                 font=FONT_LABEL, bg=PANEL_BG, fg=ACCENT).grid(
                 row=3, column=0, columnspan=2, sticky="w", padx=10)
        self.ent_quantum = ttk.Entry(panel, width=8, font=FONT_SMALL)
        self.ent_quantum.insert(0, "2")
        self.ent_quantum.grid(row=3, column=2, padx=10, sticky="w")
        tk.Label(panel, text="Must be a positive integer (> 0)",
                 font=("Segoe UI", 8), bg=PANEL_BG, fg=MUTED).grid(
                 row=3, column=3, padx=4, sticky="w")
    def _build_process_table_section(self, parent):
        self._section_header(parent, "3", "Process Table")
        frame = self._panel(parent)
        cols = ("PID", "Arrival Time", "Burst Time")
        self.proc_table = ttk.Treeview(frame, columns=cols,
                                        show="headings", height=4)
        for c in cols:
            self.proc_table.heading(c, text=c)
            self.proc_table.column(c, width=160, anchor="center")
        self.proc_table.pack(fill="x", padx=8, pady=8)
        tk.Button(frame, text="✕  Remove Selected",
                  font=FONT_SMALL, bg=DANGER, fg="white",
                  relief="flat", padx=10, pady=3, cursor="hand2",
                  command=self._remove_selected).pack(
                  anchor="e", padx=8, pady=(0, 8))
    def _build_action_buttons(self, parent):
        row = tk.Frame(parent, bg=BG)
        row.pack(pady=10)
        tk.Button(row, text="▶   Run All Algorithms",
                  font=("Segoe UI", 11, "bold"),
                  bg=SUCCESS, fg="white", relief="flat",
                  padx=24, pady=9, cursor="hand2",
                  activebackground="#219A52", activeforeground="white",
                  command=self._run_both).pack(side="left", padx=8)
        tk.Button(row, text="✕   Clear All",
                  font=("Segoe UI", 11),
                  bg=DANGER, fg="white", relief="flat",
                  padx=24, pady=9, cursor="hand2",
                  activebackground="#C0392B", activeforeground="white",
                  command=self._clear_all).pack(side="left", padx=8)
    def _add_process(self):
        try:
            pid     = self.ent_pid.get().strip()
            arrival = int(self.ent_arrival.get().strip())
            burst   = int(self.ent_burst.get().strip())
            if not pid:
                raise ValueError("PID cannot be empty.")
            Validator.validate([Process(pid, arrival, burst)])
            if any(p.pid == pid for p in self.processes):
                raise ValueError(f"Duplicate PID: '{pid}'.")
            self.processes.append(Process(pid, arrival, burst))
            tag = "alt" if len(self.processes) % 2 == 0 else ""
            self.proc_table.insert("", "end",
                values=(pid, arrival, burst), tags=(tag,))
            self.proc_table.tag_configure("alt", background=ROW_ALT)
            self.proc_table.config(height=min(len(self.processes), 8))
            for e in (self.ent_pid, self.ent_arrival, self.ent_burst):
                e.delete(0, tk.END)
            self.ent_pid.focus()
        except ValueError as e:
            messagebox.showerror("Input Error", str(e))
    def _remove_selected(self):
        sel = self.proc_table.selection()
        if not sel:
            return
        for item in sel:
            idx = self.proc_table.index(item)
            self.proc_table.delete(item)
            if 0 <= idx < len(self.processes):
                self.processes.pop(idx)
    def _clear_all(self):
        self.processes.clear()
        self._pid_color.clear()
        self._color_idx = 0
        self.proc_table.delete(*self.proc_table.get_children())
        self.tbl_rr.delete(*self.tbl_rr.get_children())
        self.tbl_sjf.delete(*self.tbl_sjf.get_children())
        self.tbl_srtf.delete(*self.tbl_srtf.get_children())   
        self.avg_rr_label.config(text="")
        self.avg_sjf_label.config(text="")
        self.avg_srtf_label.config(text="")
        for fr in (self.gantt_rr_frame, self.gantt_sjf_frame, self.gantt_srtf_frame):
            for w in fr.winfo_children():
                w.destroy()
            self._gantt_placeholder(fr)
        for w in self.rq_canvas_frame.winfo_children():
            w.destroy()
        self.rq_placeholder = tk.Label(self.rq_canvas_frame,
            text="Run the scheduler to see the ready queue.",
            font=FONT_SMALL, fg=MUTED, bg=PANEL_BG, pady=10)
        self.rq_placeholder.pack()
        for w in self.cmp_frame.winfo_children():
            w.destroy()
        tk.Label(self.cmp_frame,
            text="Run the scheduler to see the comparison.",
            font=FONT_SMALL, fg=MUTED, bg=PANEL_BG, pady=10).pack()
        self._set_conclusion("")
    def _color_for(self, pid: str) -> str:
        if pid not in self._pid_color:
            self._pid_color[pid] = PROCESS_COLORS[self._color_idx % len(PROCESS_COLORS)]
            self._color_idx += 1
        return self._pid_color[pid]
    def _run_both(self):
        if not self.processes:
            messagebox.showwarning("No Processes", "Add at least one process first.")
            return
        try:
            quantum = int(self.ent_quantum.get().strip())
        except ValueError:
            messagebox.showerror("Quantum Error", "Quantum must be a positive integer.")
            return
        try:
            Validator.validate(self.processes, quantum)
        except ValueError as e:
            messagebox.showerror("Validation Error", str(e))
            return
        rr_procs   = copy.deepcopy(self.processes)
        rr_gantt   = RoundRobin(quantum).schedule(rr_procs)
        sjf_procs  = copy.deepcopy(self.processes)
        sjf_gantt  = SJF().schedule(sjf_procs)
        srtf_procs = copy.deepcopy(self.processes)
        srtf_gantt = SRTF().schedule(srtf_procs)
        self._update_ready_queue(rr_gantt, quantum)
        self._draw_gantt(self.gantt_rr_frame,   rr_gantt,   f"Round Robin  (Q = {quantum})")
        self._draw_gantt(self.gantt_sjf_frame,  sjf_gantt,  "SJF  (Non-Preemptive)")
        self._draw_gantt(self.gantt_srtf_frame, srtf_gantt, "SRTF  (Preemptive)")      
        self._fill_results(self.tbl_rr,   self.avg_rr_label,   rr_procs,   f"Round Robin (Q={quantum})")
        self._fill_results(self.tbl_sjf,  self.avg_sjf_label,  sjf_procs,  "SJF")
        self._fill_results(self.tbl_srtf, self.avg_srtf_label, srtf_procs, "SRTF")    
        self._update_comparison(rr_procs, sjf_procs, srtf_procs, quantum)  
        self._update_conclusion(rr_procs, sjf_procs, srtf_procs, quantum)
    def _update_ready_queue(self, gantt, quantum):
        for w in self.rq_canvas_frame.winfo_children():
            w.destroy()
        tk.Label(self.rq_canvas_frame,
            text=f"Execution order  (Q = {quantum}):",
            font=FONT_LABEL, bg=PANEL_BG, fg=ACCENT).pack(
            anchor="w", padx=12, pady=(8, 4))
        scroll_outer = tk.Frame(self.rq_canvas_frame, bg=PANEL_BG)
        scroll_outer.pack(fill="x", padx=12, pady=(0, 10))
        cv = tk.Canvas(scroll_outer, bg=PANEL_BG, height=52, highlightthickness=0)
        hsb = ttk.Scrollbar(scroll_outer, orient="horizontal", command=cv.xview)
        cv.configure(xscrollcommand=hsb.set)
        hsb.pack(side="bottom", fill="x")
        cv.pack(side="top", fill="x")
        inner = tk.Frame(cv, bg=PANEL_BG)
        cv.create_window((0, 0), window=inner, anchor="nw")
        for pid, start, end in gantt:
            color = self._color_for(pid)
            box = tk.Frame(inner, bg=color, padx=6, pady=4)
            box.pack(side="left", padx=2, pady=4)
            tk.Label(box, text=pid,
                     font=("Segoe UI", 8, "bold"),
                     bg=color, fg="white").pack()
            tk.Label(box, text=f"{start}→{end}",
                     font=("Segoe UI", 7),
                     bg=color, fg="white").pack()
        inner.update_idletasks()
        cv.configure(scrollregion=cv.bbox("all"))
    def _draw_gantt(self, frame: tk.Frame, gantt, title: str):
        for w in frame.winfo_children():
            w.destroy()
        if not gantt:
            self._gantt_placeholder(frame)
            return
        end_time = max(e for _, _, e in gantt)
        fig_w = max(8, end_time * 0.55)
        fig, ax = plt.subplots(figsize=(fig_w, 1.9))
        fig.patch.set_facecolor(PANEL_BG)
        ax.set_facecolor(PANEL_BG)
        for pid, start, end in gantt:
            color = self._color_for(pid)
            ax.barh(0, end - start, left=start, height=0.55,
                    color=color, edgecolor="white", linewidth=1.5)
            mid = (start + end) / 2
            ax.text(mid, 0, pid,
                    ha="center", va="center",
                    color="white", fontsize=9, fontweight="bold")
        ticks = sorted({s for _, s, _ in gantt} | {e for _, _, e in gantt})
        ax.set_xticks(ticks)
        ax.set_xticklabels([str(t) for t in ticks], fontsize=8, color=ACCENT)
        ax.set_yticks([])
        ax.set_xlim(left=0)
        ax.set_title(title, fontsize=10, fontweight="bold",
                     color=ACCENT, pad=7, loc="left")
        for spine in ax.spines.values():
            spine.set_visible(False)
        ax.tick_params(bottom=False)
        plt.tight_layout(pad=0.4)
        cv = FigureCanvasTkAgg(fig, frame)
        cv.draw()
        cv.get_tk_widget().pack(fill="x", padx=6, pady=6)
        plt.close(fig)
    def _fill_results(self, tbl: ttk.Treeview, avg_label: tk.Label,
                      procs, algo_name: str):
        tbl.delete(*tbl.get_children())
        data = Metrics.compute(procs)
        for i, r in enumerate(data["rows"]):
            tag = "alt" if i % 2 else ""
            tbl.insert("", "end", tags=(tag,), values=(
                r["pid"], r["arrival"], r["burst"],
                r["start"], r["finish"],
                r["rt"], r["tat"], r["wt"],
            ))
        tbl.tag_configure("alt", background=ROW_ALT)
        tbl.insert("", "end", tags=("avg",), values=(
            "AVG", "—", "—", "—", "—",
            f"{data['avg_rt']:.2f}",
            f"{data['avg_tat']:.2f}",
            f"{data['avg_wt']:.2f}",
        ))
        tbl.config(height=min(len(procs) + 2, 8))
        avg_label.config(
            text=f"{algo_name}  →  "
                 f"Avg WT: {data['avg_wt']:.2f}   "
                 f"Avg TAT: {data['avg_tat']:.2f}   "
                 f"Avg RT: {data['avg_rt']:.2f}"
        )
    def _update_comparison(self, rr_procs, sjf_procs, srtf_procs, quantum):
        for w in self.cmp_frame.winfo_children():
            w.destroy()
        rr   = Metrics.compute(rr_procs)
        sjf  = Metrics.compute(sjf_procs)
        srtf = Metrics.compute(srtf_procs)
        metrics = [
            ("Avg Waiting Time",    "avg_wt"),
            ("Avg Turnaround Time", "avg_tat"),
            ("Avg Response Time",   "avg_rt"),
        ]
        grid = tk.Frame(self.cmp_frame, bg=PANEL_BG)
        grid.pack(padx=14, pady=12, anchor="w")
        headers = ["Metric", f"Round Robin (Q={quantum})", "SJF", "SRTF", "Winner ✓"]
        col_w   = [22, 22, 16, 16, 22]
        for c, (h, w) in enumerate(zip(headers, col_w)):
            tk.Label(grid, text=h,
                     font=FONT_LABEL, bg=HDR_BG, fg=HDR_FG,
                     width=w, pady=6, anchor="center",
                     relief="flat").grid(row=0, column=c, padx=1, pady=1)
        for row_i, (label, key) in enumerate(metrics, 1):
            rv  = rr[key]
            sv  = sjf[key]
            stv = srtf[key]
            best_val = min(rv, sv, stv)
            if best_val == rv:
                winner = f"Round Robin (Q={quantum})"
                win_col = 1
            elif best_val == sv:
                winner = "SJF"
                win_col = 2
            else:
                winner = "SRTF"
                win_col = 3
            bgs = [PANEL_BG, PANEL_BG, PANEL_BG, PANEL_BG, PANEL_BG]
            bgs[win_col] = "#D5F5E3"
            bgs[4]       = "#D5F5E3"
            tk.Label(grid, text=label,
                     font=FONT_SMALL, bg=bgs[0],
                     width=col_w[0], pady=5, anchor="center").grid(
                     row=row_i, column=0, padx=1, pady=1)
            tk.Label(grid, text=f"{rv:.2f}",
                     font=FONT_SMALL, bg=bgs[1],
                     width=col_w[1], pady=5, anchor="center").grid(
                     row=row_i, column=1, padx=1, pady=1)
            tk.Label(grid, text=f"{sv:.2f}",
                     font=FONT_SMALL, bg=bgs[2],
                     width=col_w[2], pady=5, anchor="center").grid(
                     row=row_i, column=2, padx=1, pady=1)
            tk.Label(grid, text=f"{stv:.2f}",
                     font=FONT_SMALL, bg=bgs[3],
                     width=col_w[3], pady=5, anchor="center").grid(
                     row=row_i, column=3, padx=1, pady=1)
            tk.Label(grid, text=winner,
                     font=FONT_BOLD, bg=bgs[4],
                     width=col_w[4], pady=5, anchor="center").grid(
                     row=row_i, column=4, padx=1, pady=1)
    def _update_conclusion(self, rr_procs, sjf_procs, srtf_procs, quantum):
        rr   = Metrics.compute(rr_procs)
        sjf  = Metrics.compute(sjf_procs)
        srtf = Metrics.compute(srtf_procs)
        def best(key):
            vals = {"Round Robin": rr[key], "SJF": sjf[key], "SRTF": srtf[key]}
            winner = min(vals, key=vals.get)
            min_val = vals[winner]
            tied = [k for k, v in vals.items() if v == min_val]
            if len(tied) > 1:
                return "Tie (" + " / ".join(tied) + ")"
            if winner == "Round Robin":
                return f"Round Robin (Q={quantum})"
            return winner
        lines = [
            "═" * 62,
            "  PERFORMANCE SUMMARY",
            "═" * 62,
            f"  Avg Waiting Time    →  RR={rr['avg_wt']:.2f}  SJF={sjf['avg_wt']:.2f}  SRTF={srtf['avg_wt']:.2f}   Best: {best('avg_wt')}",
            f"  Avg Turnaround Time →  RR={rr['avg_tat']:.2f}  SJF={sjf['avg_tat']:.2f}  SRTF={srtf['avg_tat']:.2f}   Best: {best('avg_tat')}",
            f"  Avg Response Time   →  RR={rr['avg_rt']:.2f}  SJF={sjf['avg_rt']:.2f}  SRTF={srtf['avg_rt']:.2f}   Best: {best('avg_rt')}",
            "",
            "  ANALYSIS",
            "─" * 62,
            f"  • Fairness:    Round Robin gives each process a time slice of {quantum} units,",
            "                 ensuring no process is starved.",
            "",
            "  • Efficiency:  SJF minimises average waiting time for non-preemptive",
            "                 scenarios; long jobs may wait if short jobs keep arriving.",
            "",
            "  • Preemption:  SRTF (preemptive SJF) generally achieves the lowest",
            "                 waiting and turnaround times but has higher context-switch",
            "                 overhead and can starve long processes.",
            "",
            "  RECOMMENDATION",
            "─" * 62,
            "  → Round Robin  — interactive / time-sharing systems (fairness matters).",
            "  → SJF          — batch systems with known burst times (throughput focus).",
            "  → SRTF         — batch systems where optimal avg wait time is critical.",
            "═" * 62,
        ]
        self._set_conclusion("\n".join(lines))
    def _set_conclusion(self, text: str):
        self.conclusion_box.config(state="normal")
        self.conclusion_box.delete("1.0", tk.END)
        self.conclusion_box.insert(tk.END, text)
        self.conclusion_box.config(state="disabled")
if __name__ == "__main__":
    root = tk.Tk()
    app = SchedulerApp(root)
    root.mainloop()