"""
advanced_scheduler.py - GE+ with physics-aware cost and lookahead.
"""

import numpy as np
from copy import deepcopy
from dataclasses import dataclass
from typing import List, Optional, Tuple

@dataclass
class SourceState:
    id: int
    load: float = 0.0
    poisoning: float = 0.0
    last_used: int = -1

class AdvancedGreedyEligible:
    """
    Advanced GE algorithm with physics-aware cost function and lookahead.
    """
    
    def __init__(self, n_sources: int, k_rest: int = 1, 
                 alpha_load: float = 0.6, alpha_poison: float = 0.25,
                 alpha_rec: float = 0.15, lookahead: int = 2, 
                 use_physics: bool = True):
        self.n = n_sources
        self.k = k_rest
        self.a_l = alpha_load
        self.a_p = alpha_poison
        self.a_r = alpha_rec
        self.lookahead = lookahead
        self.use_phys = use_physics
        self.sources = [SourceState(i) for i in range(n_sources)]
        self.history = []
        self.cycle = 0
        self.phys_model = None

    def set_physical_model(self, model):
        """Attach the Berg physics model for physics-aware decisions."""
        self.phys_model = model
        for s in self.sources:
            s.poisoning = model.theta

    def _eligible(self) -> List[int]:
        """Get eligible sources respecting K-rest rule."""
        last_k = self.history[-self.k:] if self.k > 0 else []
        el = [i for i in range(self.n) if i not in last_k]
        return el if el else list(range(self.n))

    def _is_contiguous(self, indices: List[int]) -> bool:
        """Check if indices form a contiguous block."""
        if len(indices) <= 1:
            return True
        sorted_idx = sorted(indices)
        return all(sorted_idx[i] + 1 == sorted_idx[i+1] 
                   for i in range(len(sorted_idx) - 1))

    def _check_swap_validity(self, assign: List[int], block_i: List[int], block_j: List[int]) -> bool:
        """Check if block swap violates consecutive-free rule."""
        temp = assign.copy()
        for idx in block_i:
            temp[idx] = -1
        for idx in block_j:
            temp[idx] = -2
        
        for idx in block_i:
            temp[idx] = assign[block_j[block_i.index(idx)]]
        for idx in block_j:
            temp[idx] = assign[block_i[block_j.index(idx)]]
        
        for i in range(len(assign) - 1):
            if temp[i] == temp[i+1]:
                return False
        return True

    def _hybrid_cost(self, sid: int, dur: float) -> float:
        """Compute hybrid cost for a source."""
        src = self.sources[sid]
        max_l = max([s.load for s in self.sources]) + 1e-6
        norm_l = src.load / max_l
        
        poison = src.poisoning if self.use_phys and self.phys_model else 0.5
        
        rec = 0.0
        if self.cycle > 0:
            rec = max(0.0, 1.0 - (self.cycle - src.last_used) / (self.k + 2))
        
        cost = self.a_l * norm_l + self.a_p * poison + self.a_r * rec
        
        # Penalty for immediate repetition
        if sid == (self.history[-1] if self.history else -1):
            cost += 0.1
        
        return cost

    def _simulate_future(self, sid: int, remaining: List[float], depth: int) -> float:
        """Recursive lookahead simulation."""
        if depth == 0 or not remaining:
            return np.max([s.load for s in self.sources])
        
        best = float('inf')
        for cand in self._eligible()[:2]:
            tmp = deepcopy(self.sources)
            tmp_h = self.history.copy()
            
            self.sources[cand].load += remaining[0]
            self.history.append(cand)
            
            fut = self._simulate_future(cand, remaining[1:], depth - 1)
            
            self.sources = tmp
            self.history = tmp_h
            
            best = min(best, fut)
        
        return best

    def assign_cycle(self, duration: float, remaining: Optional[List[float]] = None) -> int:
        """Assign a cycle to a source using advanced decision logic."""
        eligible = self._eligible()
        
        if self.lookahead > 0 and remaining:
            best_s, best_sc = None, float('inf')
            for s in eligible[:4]:
                tmp = deepcopy(self.sources)
                tmp_h = self.history.copy()
                
                self.sources[s].load += duration
                self.history.append(s)
                
                fut = self._simulate_future(s, remaining, self.lookahead)
                cur = self._hybrid_cost(s, duration)
                sc = cur + 0.3 * fut
                
                self.sources = tmp
                self.history = tmp_h
                
                if sc < best_sc:
                    best_sc, best_s = sc, s
            
            selected = best_s if best_s is not None else eligible[0]
        else:
            selected = min(eligible, key=lambda s: self._hybrid_cost(s, duration))
        
        self.sources[selected].load += duration
        self.sources[selected].last_used = self.cycle
        self.history.append(selected)
        self.cycle += 1
        
        return selected

    def reset(self):
        """Reset to initial state."""
        self.sources = [SourceState(i) for i in range(self.n)]
        self.history = []
        self.cycle = 0


class BlockSwapOptimizer:
    """
    Block swap optimizer for post-processing.
    Swaps blocks of consecutive cycles between sources.
    """
    
    def __init__(self, max_block: int = 3, max_iter: int = 100):
        self.max_block = max_block
        self.max_iter = max_iter

    def _is_contiguous(self, indices: List[int]) -> bool:
        """Check if indices form a contiguous block."""
        if len(indices) <= 1:
            return True
        sorted_idx = sorted(indices)
        return all(sorted_idx[i] + 1 == sorted_idx[i+1] 
                   for i in range(len(sorted_idx) - 1))

    def _check_swap_validity(self, assign: List[int], block_i: List[int], block_j: List[int]) -> bool:
        """Check if block swap violates consecutive-free rule."""
        temp = assign.copy()
        for idx in block_i:
            temp[idx] = -1
        for idx in block_j:
            temp[idx] = -2
        
        for idx in block_i:
            temp[idx] = assign[block_j[block_i.index(idx)]]
        for idx in block_j:
            temp[idx] = assign[block_i[block_j.index(idx)]]
        
        for i in range(len(assign) - 1):
            if temp[i] == temp[i+1]:
                return False
        return True

    def optimize(self, assign: List[int], times: List[float], n_sources: int) -> List[int]:
        """Optimize assignment by swapping blocks of consecutive cycles."""
        assign = assign.copy()
        m = len(assign)
        
        loads = [0.0] * n_sources
        for i, s in enumerate(assign):
            loads[s] += times[i]
        
        cur_ms = max(loads)
        
        for _ in range(self.max_iter):
            p_max = np.argmax(loads)
            p_min = np.argmin(loads)
            
            if loads[p_max] - loads[p_min] < 1e-6:
                break
            
            max_idx = [i for i, s in enumerate(assign) if s == p_max]
            min_idx = [i for i, s in enumerate(assign) if s == p_min]
            
            improved = False
            
            for bs in range(1, min(self.max_block, len(max_idx), len(min_idx)) + 1):
                for i in range(len(max_idx) - bs + 1):
                    b1 = max_idx[i:i + bs]
                    if not self._is_contiguous(b1):
                        continue
                    
                    for j in range(len(min_idx) - bs + 1):
                        b2 = min_idx[j:j + bs]
                        if not self._is_contiguous(b2):
                            continue
                        
                        if not self._check_swap_validity(assign, b1, b2):
                            continue
                        
                        new_loads = loads.copy()
                        for idx in b1:
                            new_loads[p_min] += times[idx]
                        for idx in b2:
                            new_loads[p_max] += times[idx]
                        
                        # Recalculate loads for p_max and p_min
                        new_loads[p_max] = sum(times[i] for i in range(m) if assign[i] == p_max)
                        new_loads[p_min] = sum(times[i] for i in range(m) if assign[i] == p_min)
                        
                        # Apply swap
                        for idx in b1:
                            assign[idx] = p_min
                        for idx in b2:
                            assign[idx] = p_max
                        
                        # Recalculate loads
                        loads = [0.0] * n_sources
                        for idx, s in enumerate(assign):
                            loads[s] += times[idx]
                        
                        new_ms = max(loads)
                        
                        if new_ms < cur_ms - 1e-6:
                            cur_ms = new_ms
                            improved = True
                            break
                    
                    if improved:
                        break
                if improved:
                    break
            
            if not improved:
                break
        
        return assign


class AdvancedSchedulerInterface:
    """
    Unified interface for advanced scheduling with physics-aware decisions.
    """
    
    def __init__(self, n_sources: int, k_rest: int = 1,
                 alpha_load: float = 0.6, alpha_poison: float = 0.25,
                 alpha_rec: float = 0.15, lookahead: int = 2,
                 use_physics: bool = True, use_block_swap: bool = True):
        self.n_sources = n_sources
        self.scheduler = AdvancedGreedyEligible(
            n_sources, k_rest, alpha_load, alpha_poison, alpha_rec,
            lookahead, use_physics
        )
        self.swap_optimizer = BlockSwapOptimizer() if use_block_swap else None
        self.use_block_swap = use_block_swap
        self.name = "GE+Swap"

    def set_physical_model(self, model):
        """Attach the Berg physics model."""
        self.scheduler.set_physical_model(model)

    def run(self, cycle_times: List[float], pressures: Optional[List[float]] = None) -> dict:
        """Run full scheduling with advanced algorithm."""
        m = len(cycle_times)
        assign = []
        loads = [0.0] * self.n_sources
        
        for i, duration in enumerate(cycle_times):
            remaining = cycle_times[i+1:i+1+self.scheduler.lookahead]
            src = self.scheduler.assign_cycle(duration, remaining)
            assign.append(src)
            loads[src] += duration
        
        if self.use_block_swap and self.swap_optimizer:
            assign = self.swap_optimizer.optimize(assign, cycle_times, self.n_sources)
            loads = [0.0] * self.n_sources
            for i, src in enumerate(assign):
                loads[src] += cycle_times[i]
        
        return {
            'assign': assign,
            'loads': loads,
            'makespan': max(loads),
            'schedule_history': self.scheduler.history,
            'source_states': self.scheduler.sources
        }