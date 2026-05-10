from typing import List, Tuple
from Process import Process
class SJF:
    def schedule(self, processes: List[Process]) -> List[Tuple[str, int, int]]:
        for p in processes:
            p.reset()
        remaining = list(processes)      
        gantt: List[Tuple[str, int, int]] = []
        time = 0
        while remaining:
            available = [p for p in remaining if p.arrival <= time]
            if not available:
                time = min(p.arrival for p in remaining)
                continue
            current = min(available, key=lambda p: (p.burst, p.pid))
            current.start_time = time
            gantt.append((current.pid, time, time + current.burst))
            time += current.burst
            current.remaining = 0
            current.finish_time = time
            remaining.remove(current)
        return gantt
