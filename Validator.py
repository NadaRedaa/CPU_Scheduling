class Process:
    def __init__(self, pid: str, arrival: int, burst: int):
        self.pid = pid
        self.arrival = arrival
        self.burst = burst         
        self.remaining = burst      
        self.start_time = None      
        self.finish_time = None    
    @property
    def response_time(self) -> int:
        if self.start_time is None:
            return None
        return self.start_time - self.arrival
    @property
    def turnaround_time(self) -> int:
        if self.finish_time is None:
            return None
        return self.finish_time - self.arrival
    @property
    def waiting_time(self) -> int:
        if self.turnaround_time is None:
            return None
        return self.turnaround_time - self.burst
    def reset(self):
        self.remaining = self.burst
        self.start_time = None
        self.finish_time = None
    def __repr__(self):
        return (
            f"Process(pid={self.pid!r}, arrival={self.arrival}, "
            f"burst={self.burst}, remaining={self.remaining})"
        )
