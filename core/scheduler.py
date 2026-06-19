"""
scheduler.py - Standard online schedulers: GE, Cyclic, JSQ-CF.
"""

import numpy as np

class Scheduler:
    def __init__(self, n_sources):
        self.n_sources = n_sources
        self.loads = np.zeros(n_sources)
        self.schedule = []
        self.prev = -1
        self.name = "Base"

    def reset(self):
        self.loads = np.zeros(self.n_sources)
        self.schedule = []
        self.prev = -1

class GreedyEligible(Scheduler):
    def __init__(self, n_sources):
        super().__init__(n_sources)
        self.name = "GE"
    
    def assign_cycle(self, duration, **kwargs):
        eligible = [i for i in range(self.n_sources) if i != self.prev]
        if not eligible:
            eligible = list(range(self.n_sources))
        s = min(eligible, key=lambda i: self.loads[i])
        self.schedule.append(s)
        self.loads[s] += duration
        self.prev = s
        return s

class CyclicScheduler(Scheduler):
    def __init__(self, n_sources):
        super().__init__(n_sources)
        self.name = "Cyclic"
        self.next = 0
    
    def reset(self):
        super().reset()
        self.next = 0
    
    def assign_cycle(self, duration, **kwargs):
        s = self.next
        self.schedule.append(s)
        self.loads[s] += duration
        self.prev = s
        if self.n_sources > 1:
            self.next = (self.next + 1) % self.n_sources
            if self.next == self.prev:
                self.next = (self.next + 1) % self.n_sources
        return s

class JSQCFScheduler(Scheduler):
    def __init__(self, n_sources):
        super().__init__(n_sources)
        self.name = "JSQ-CF"
    
    def assign_cycle(self, duration, **kwargs):
        eligible = [i for i in range(self.n_sources) if i != self.prev]
        if not eligible:
            eligible = list(range(self.n_sources))
        s = min(eligible, key=lambda i: self.loads[i])
        self.schedule.append(s)
        self.loads[s] += duration
        self.prev = s
        return s

def create_scheduler(name, n_sources):
    schedulers = {
        'GE': GreedyEligible,
        'Cyclic': CyclicScheduler,
        'JSQ-CF': JSQCFScheduler,
    }
    if name not in schedulers:
        raise ValueError(f"Unknown scheduler: {name}. Options: {list(schedulers.keys())}")
    return schedulers[name](n_sources)