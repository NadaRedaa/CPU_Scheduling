from typing import Dict, List
from Process import Process
from Metrics import Metrics
BOLD  = "\033[1m"
RESET = "\033[0m"
GREEN = "\033[32m"
CYAN  = "\033[36m"
class Comparison:
    @staticmethod
    def compare(results: Dict[str, List[Process]]) -> None:
        if not results:
            print("No results to compare.")
            return
        stats = {}
        for algo, procs in results.items():
            data = Metrics.compute(procs)
            stats[algo] = {
                "avg_wt":  data["avg_wt"],
                "avg_tat": data["avg_tat"],
                "avg_rt":  data["avg_rt"],
            }
        def winner_of(metric: str) -> str:
            return min(stats, key=lambda a: stats[a][metric])
        win_wt  = winner_of("avg_wt")
        win_tat = winner_of("avg_tat")
        win_rt  = winner_of("avg_rt")
        print(f"\n{'='*65}")
        print(f"  {BOLD}Algorithm Comparison{RESET}")
        print(f"{'='*65}")
        col = "{:<20} {:>12} {:>12} {:>12}"
        print(col.format("Algorithm", "Avg WT", "Avg TAT", "Avg RT"))
        print("-" * 65)
        for algo, s in stats.items():
            wt_str  = f"{s['avg_wt']:.2f}"
            tat_str = f"{s['avg_tat']:.2f}"
            rt_str  = f"{s['avg_rt']:.2f}"
            if algo == win_wt:
                wt_str  = f"{BOLD}{GREEN}{wt_str}{RESET}"
            if algo == win_tat:
                tat_str = f"{BOLD}{GREEN}{tat_str}{RESET}"
            if algo == win_rt:
                rt_str  = f"{BOLD}{GREEN}{rt_str}{RESET}"
            print(f"  {algo:<18} {wt_str:>20} {tat_str:>20} {rt_str:>20}")
        print("-" * 65)
        print(f"  {CYAN}Winners:{RESET}  WT → {BOLD}{win_wt}{RESET}  |  TAT → {BOLD}{win_tat}{RESET}  |  RT → {BOLD}{win_rt}{RESET}")
        print("=" * 65)
        Comparison._print_verdict(stats, win_wt, win_tat, win_rt)
    @staticmethod
    def _print_verdict(stats: dict, win_wt: str, win_tat: str, win_rt: str) -> None:
        print(f"\n  {BOLD}Verdict{RESET}")
        print(f"  {'─'*58}")
        lines = [
            "  • SJF minimises waiting time by always picking the shortest "
            "available job first, making it highly EFFICIENT for "
            "throughput-oriented workloads.",

            "  • Round Robin is the most FAIR algorithm: every process gets "
            "equal CPU slices (quantum), so no single job can monopolise "
            "the processor. This comes at the cost of higher average WT "
            "due to context switches.",

            "  • SJF can cause STARVATION for long processes if shorter "
            "jobs keep arriving. Round Robin avoids starvation by design.",

            f"  • For this workload: best Avg WT → {BOLD}{win_wt}{RESET}, "
            f"best Avg TAT → {BOLD}{win_tat}{RESET}, "
            f"best Avg RT → {BOLD}{win_rt}{RESET}.",
        ]
        for line in lines:
            print(line)
        print(f"  {'─'*58}\n")
