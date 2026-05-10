# 🖥️ CPU Scheduling Simulator (Python)

### 🎓 Project Overview
This project is a high-performance **CPU Scheduling Simulator** developed for the **Operating Systems** course at **Helwan University** (Faculty of Computers and Artificial Intelligence). It provides a graphical and terminal-based simulation of how an Operating System manages process execution.

---

## 🚀 Implemented Algorithms
The simulator accurately implements the following scheduling strategies:
1. **SJF (Shortest Job First):** Non-preemptive scheduling that selects the process with the smallest burst time.
2. **SRTF (Shortest Remaining Time First):** The preemptive version of SJF.
3. **Round Robin (RR):** Provides each process a fixed time slice (**Quantum**), ensuring fairness and preventing starvation.

---

## 📊 Key Features
* **Full Process Life-cycle:** Tracks Arrival, Burst, Start, Finish, Waiting, and Turnaround times.
* **Gantt Chart Visualization:** Generates a visual timeline for every algorithm to illustrate context switching and execution flow.
* **Performance Comparison:** A specialized module to compare algorithms based on **Average Waiting Time** and **Efficiency**.
* **Clean Architecture:** Organized using a professional package structure (Models, Schedulers, Metrics, and GUI).

---

## 📂 Project Structure
Following the standard repository guidelines:
```text
src/
├── model/      # Data classes (Process.py)
├── scheduler/  # Logic (SJF.py, SRTF.py, RoundRobin.py)
├── metrics/    # Calculations (Metrics.py, Comparison.py)
├── gui/        # Interface (scheduler_gui.py, GanttChart.py)
└── util/       # Validation (Validator.py)