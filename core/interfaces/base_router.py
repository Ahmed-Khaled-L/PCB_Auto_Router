from abc import ABC, abstractmethod

class BaseRouter(ABC):
    """Abstract base class for all synchronous single-net pathfinding algorithms."""
    
    def __init__(self, grid):
        self.grid = grid

    @abstractmethod
    def route(self, net):
        """
        Calculates the path from net.start_node to net.end_node.
        Returns True if a path was successfully found and saved to the net, False otherwise.
        """
        pass
        
    def _reconstruct_path(self, current_node, net):
        """Helper method to backtrack from the end_node to the start_node."""
        path = []
        while current_node is not None:
            path.append(current_node)
            current_node = current_node.parent
        path.reverse()
        net.path = path
        return True