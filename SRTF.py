from typing import List, Tuple
from Process import Process
class SRTF:
    def schedule(self, processes: List[Process]) -> List[Tuple[str, int, int]]:
        for p in processes:
            p.reset()
        n = len(processes)
        time = min(p.arrival for p in processes)
        completed = 0
        remaining = {p.pid: p.burst   for p in processes}
        arrivals  = {p.pid: p.arrival for p in processes}
        proc_map  = {p.pid: p         for p in processes}
        ticks: List[Tuple[str, int]] = []  

        while completed < n:
            available = [
                pid for pid in proc_map
                if arrivals[pid] <= time and remaining[pid] > 0
            ]

            if not available:
                time = min(arrivals[pid] for pid in proc_map if remaining[pid] > 0)
                continue
            chosen_pid = min(available, key=lambda pid: (remaining[pid], pid))
            chosen     = proc_map[chosen_pid]
            if chosen.start_time is None:
                chosen.start_time = time
            ticks.append((chosen_pid, time))
            remaining[chosen_pid] -= 1
            time += 1
            if remaining[chosen_pid] == 0:
                chosen.finish_time = time
                completed += 1
        gantt: List[Tuple[str, int, int]] = []
        if not ticks:
            return gantt
        seg_pid, seg_start = ticks[0]
        for i in range(1, len(ticks)):
            pid, t = ticks[i]
            if pid != seg_pid:
                gantt.append((seg_pid, seg_start, t))
                seg_pid, seg_start = pid, t
        gantt.append((seg_pid, seg_start, ticks[-1][1] + 1))
        return gantt
