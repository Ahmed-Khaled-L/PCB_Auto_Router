from collections import deque
from core.interfaces.base_router import BaseRouter

class BFSRouter(BaseRouter):
    def route(self, net):
        """Standard, synchronous Breadth-First Search."""
        net.search_history = []
        net.path = []
        
        net.start_node.is_obstacle = False
        net.end_node.is_obstacle = False
        
        try:
            net.start_node.parent = None
            queue = deque([net.start_node])
            net.start_node.visited = True

            while queue:
                current = queue.popleft()

                # 1. Record this node for the GUI animation!
                if current not in net.search_history:
                    net.search_history.append(current)

                # Target reached!
                if current == net.end_node:
                    return self._reconstruct_path(current, net)
                
                for neighbor in self.grid.get_neighbors(current, net):
                    if not neighbor.visited:
                        neighbor.visited = True
                        neighbor.parent = current
                        queue.append(neighbor)
                        
            return False # No path found
            
        finally:
            net.start_node.is_obstacle = True
            net.end_node.is_obstacle = True