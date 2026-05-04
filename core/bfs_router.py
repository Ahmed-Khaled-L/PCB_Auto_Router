
#Lee's Algorithm


from collections import deque

class BFSRouter:
    def __init__(self, grid):
        self.grid = grid

    def route(self, net):
        queue = deque([net.start_node])
        net.start_node.visited = True

        while queue:
            current = queue.popleft()

            # Target reached! Backtrack to build the path.
            if current == net.end_node:
                return self._reconstruct_path(current, net)

            for neighbor in self.grid.get_neighbors(current):
                if not neighbor.visited:
                    neighbor.visited = True
                    neighbor.parent = current
                    queue.append(neighbor)
                    
        return False # No path found

    def _reconstruct_path(self, current_node, net):
        path = []
        while current_node is not None:
            path.append(current_node)
            current_node = current_node.parent
        path.reverse() # Reverse to get start-to-end
        net.path = path
        return True