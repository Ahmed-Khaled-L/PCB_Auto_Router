# core/optimizers/greedy_optimizer.py
from core.interfaces.base_optimizer import BaseOptimizer
from core.heuristics import euclidean_distance

class GreedyOptimizer(BaseOptimizer):
    def optimize(self, nets):
        """Sorts the nets from shortest to longest Euclidean distance."""
        print("[OPTIMIZER] Sorting nets using Greedy (Shortest-First) Strategy.")
        # Returns a new list sorted by straight-line distance
        return sorted(nets, key=lambda net: euclidean_distance(net.start_node, net.end_node))