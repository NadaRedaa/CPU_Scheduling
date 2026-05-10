import copy
from Process import Process
from Validator import Validator
from SJF import SJF
from SRTF import SRTF
from RoundRobin import RoundRobin
from Metrics import Metrics
from GanttChart import GanttChart
from Comparison import Comparison
def run_scenario(name: str, raw_processes, quantum: int = 2) -> None:
    print(f"\n{'#'*65}")
    print(f"  Scenario {name}")
    print(f"{'#'*65}")
    try:
        Validator.validate(raw_processes, quantum)
        print("✅  Input validation passed.")
    except ValueError as e:
        print(f"❌  Validation Error: {e}")
        print("    → Scheduling aborted for this scenario.")
        return
    gantt_chart = GanttChart(block_width=4)
    print("\n===== SJF (Non-Preemptive) =====")
    sjf_procs = copy.deepcopy(raw_processes)
    sjf_gantt = SJF().schedule(sjf_procs)
    gantt_chart.draw(sjf_gantt, "SJF (Non-Preemptive)")
    Metrics.print_table(sjf_procs, "SJF (Non-Preemptive)")
    print("\n===== SRTF (Preemptive SJF) =====")
    srtf_procs = copy.deepcopy(raw_processes)
    srtf_gantt = SRTF().schedule(srtf_procs)
    gantt_chart.draw(srtf_gantt, "SRTF (Preemptive SJF)")
    Metrics.print_table(srtf_procs, "SRTF (Preemptive SJF)")
    print(f"\n===== Round Robin (Q={quantum}) =====")
    rr_procs = copy.deepcopy(raw_processes)
    rr_gantt = RoundRobin(quantum).schedule(rr_procs)
    gantt_chart.draw(rr_gantt, f"Round Robin (Q={quantum})")
    Metrics.print_table(rr_procs, f"Round Robin (Q={quantum})")
    Comparison.compare({
        "SJF":         sjf_procs,
        "SRTF":        srtf_procs,
        "Round Robin": rr_procs,
    })
run_scenario("A — Basic Mixed Workload", [
    Process("P1", 0, 6),
    Process("P2", 1, 4),
    Process("P3", 2, 2),
    Process("P4", 3, 5),
], quantum=2)
run_scenario("B — Short-Job-Heavy", [
    Process("P1", 0, 2),
    Process("P2", 1, 1),
    Process("P3", 2, 3),
    Process("P4", 3, 2),
], quantum=2)
run_scenario("C — Fairness (Equal Bursts)", [
    Process("P1", 0, 4),
    Process("P2", 0, 4),
    Process("P3", 0, 4),
], quantum=2)
run_scenario("D — Long-Job Sensitivity", [
    Process("P1", 0, 10),
    Process("P2", 1,  2),
    Process("P3", 2,  1),
], quantum=2)
run_scenario("E — Validation (Negative Arrival)", [
    Process("P1",  0, 4),
    Process("P2", -1, 3),
    Process("P3",  2, 2),
], quantum=2)
