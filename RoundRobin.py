from collections import deque
from typing import List, Tuple
from Process import Process
class RoundRobin:
    def __init__(self, quantum: int):
        self.quantum = quantum
    def schedule(self, processes: List[Process]) -> List[Tuple[str, int, int]]:
        for p in processes:
            p.reset()
        pending = sorted(processes, key=lambda p: (p.arrival, p.pid))
        queue: deque = deque()
        gantt: List[Tuple[str, int, int]] = []
        time = 0
        pending_idx = 0
        while pending_idx < len(pending) and pending[pending_idx].arrival <= time:
            queue.append(pending[pending_idx])
            pending_idx += 1
        while queue:
            current = queue.popleft()
            if current.start_time is None:
                current.start_time = time
            run_for = min(self.quantum, current.remaining)
            gantt.append((current.pid, time, time + run_for))
            time += run_for
            current.remaining -= run_for
            newly_arrived = []
            while pending_idx < len(pending) and pending[pending_idx].arrival <= time:
                newly_arrived.append(pending[pending_idx])
                pending_idx += 1
            newly_arrived.sort(key=lambda p: p.pid)
            for p in newly_arrived:
                queue.append(p)
            if current.remaining > 0:
                queue.append(current)
            else:
                current.finish_time = time
            if not queue and pending_idx < len(pending):
                time = pending[pending_idx].arrival
                while pending_idx < len(pending) and pending[pending_idx].arrival <= time:
                    queue.append(pending[pending_idx])
                    pending_idx += 1
        return gantt
