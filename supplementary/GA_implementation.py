"""
GA_implementation.py - Genetic algorithm baseline for comparison.
"""

import numpy as np

def genetic_algorithm(n_sources, cycle_times, pop_size=100, generations=500):
    """
    Simple genetic algorithm for scheduling.
    
    Returns:
    --------
    dict: {'assign': list, 'loads': list, 'makespan': float}
    """
    m = len(cycle_times)
    
    def fitness(assign):
        loads = np.zeros(n_sources)
        for i, s in enumerate(assign):
            loads[s] += cycle_times[i]
        # Penalize consecutive assignments
        penalty = sum(1 for i in range(1, m) if assign[i] == assign[i-1]) * 10
        return max(loads) + penalty
    
    # Initialize population
    pop = [np.random.randint(0, n_sources, m).tolist() for _ in range(pop_size)]
    
    for _ in range(generations):
        scores = [fitness(ind) for ind in pop]
        sorted_idx = np.argsort(scores)
        pop = [pop[i] for i in sorted_idx[:pop_size // 2]]
        
        # Crossover and mutation
        new_pop = pop.copy()
        while len(new_pop) < pop_size:
            p1, p2 = pop[np.random.choice(len(pop), 2, replace=False)]
            crossover_point = np.random.randint(1, m)
            child = p1[:crossover_point] + p2[crossover_point:]
            if np.random.random() < 0.1:
                child[np.random.randint(0, m)] = np.random.randint(0, n_sources)
            new_pop.append(child)
        pop = new_pop
    
    best = min(pop, key=fitness)
    loads = np.zeros(n_sources)
    for i, s in enumerate(best):
        loads[s] += cycle_times[i]
    
    return {
        'assign': best,
        'loads': loads,
        'makespan': max(loads)
    }