from typing import List, Tuple
COLORS = [
    "\033[41m",  
    "\033[42m",  
    "\033[44m", 
    "\033[43m",  
    "\033[45m", 
    "\033[46m",  
    "\033[47m", 
    "\033[101m", 
    "\033[102m", 
    "\033[104m", 
]
RESET = "\033[0m"
BOLD  = "\033[1m"
class GanttChart:
    def __init__(self, block_width: int = 4):
        self.block_width = block_width
    def draw(
        self,
        gantt: List[Tuple[str, int, int]],
        algorithm_name: str = "",
    ) -> None:
        if not gantt:
            print("  [Empty Gantt — no segments to display]")
            return
        unique_pids = list(dict.fromkeys(seg[0] for seg in gantt))  
        color_map = {pid: COLORS[i % len(COLORS)] for i, pid in enumerate(unique_pids)}
        print(f"\n{'─'*60}")
        if algorithm_name:
            print(f"  {BOLD}Gantt Chart — {algorithm_name}{RESET}")
        print(f"{'─'*60}")
        bar = ""
        for pid, start, end in gantt:
            duration = end - start
            block = f" {pid} ".center(max(duration * self.block_width, len(pid) + 2))
            bar += color_map[pid] + block + RESET

        print("  " + bar)
        markers = ""
        prev_end = None
        for pid, start, end in gantt:
            duration = end - start
            cell_w = max(duration * self.block_width, len(pid) + 2)
            if prev_end is None:
                markers += str(start).ljust(cell_w)
            else:
                markers += str(start).ljust(cell_w)
            prev_end = end
        markers += str(gantt[-1][2])
        print("  " + markers)
        print()
        legend_parts = [
            f"{color_map[pid]}  {pid}  {RESET}"
            for pid in unique_pids
        ]
        print("  Legend: " + "  ".join(legend_parts))
        print(f"{'─'*60}")
