from abc import ABC, abstractmethod

class BaseOptimizer(ABC):
    """Abstract base class for determining the optimal sequence to route multiple nets."""
    
    def __init__(self, grid, router):
        self.grid = grid
        self.router = router # Inject ANY BaseRouter here (A*, BFS, etc.)

    @abstractmethod
    def optimize(self, nets):
        """
        Takes a list of unrouted nets, evaluates them, and returns 
        the sequence in which they should be routed to minimize deadlocks.
        """
        pass