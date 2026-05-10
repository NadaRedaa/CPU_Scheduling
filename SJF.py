from typing import List
from Process import Process
class Metrics:
    @staticmethod
    def compute(processes: List[Process]) -> dict:
        rows = []
        for p in processes:
            rows.append({
                "pid":     p.pid,
                "arrival": p.arrival,
                "burst":   p.burst,
                "start":   p.start_time,
                "finish":  p.finish_time,   
                "rt":      p.response_time,
                "tat":     p.turnaround_time,
                "wt":      p.waiting_time,
            })
        n = len(rows)
        avg_rt  = sum(r["rt"]  for r in rows) / n
        avg_tat = sum(r["tat"] for r in rows) / n
        avg_wt  = sum(r["wt"]  for r in rows) / n
        return {
            "rows":    rows,
            "avg_rt":  avg_rt,
            "avg_tat": avg_tat,
            "avg_wt":  avg_wt,
        }
    @staticmethod
    def print_table(processes: List[Process], algorithm_name: str = "") -> None:
        data = Metrics.compute(processes)

        header = f"\n{'='*68}"
        if algorithm_name:
            header += f"\n  Metrics — {algorithm_name}"
        header += f"\n{'='*68}"
        print(header)
        col = "{:<8} {:>8} {:>8} {:>8} {:>10} {:>6} {:>6} {:>6}"
        print(col.format("PID", "Arrival", "Burst", "Start", "CT(Finish)", "RT", "TAT", "WT"))
        print("-" * 68)
        for r in data["rows"]:
            print(col.format(
                r["pid"], r["arrival"], r["burst"],
                r["start"], r["finish"],
                r["rt"], r["tat"], r["wt"]
            ))
        print("-" * 68)
        avg_col = "{:<8} {:>8} {:>8} {:>8} {:>10} {:>6.2f} {:>6.2f} {:>6.2f}"
        print(avg_col.format(
            "AVG", "", "", "", "",
            data["avg_rt"], data["avg_tat"], data["avg_wt"]
        ))
        print("=" * 68)
