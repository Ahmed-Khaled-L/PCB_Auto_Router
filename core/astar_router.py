import heapq
from core.heuristics import octile_distance

class AStarRouter:
    def __init__(self, grid):
        self.grid = grid
        self.reset()

    def reset(self):
        """Clears previous search states."""
        self.open_set = []
        self.counter = 0
        self.g_score = {}
        self.closed_set = set()
        self.net = None
        self.end_node = None
        self.is_finished = False
        self.success = False

    def initialize_search(self, net):
        """Sets up the initial state for the animation loop."""
        self.reset()
        self.net = net
        start_node = net.start_node
        self.end_node = net.end_node
        
        self.g_score[start_node] = 0
        f_score_start = octile_distance(start_node, self.end_node)
        
        heapq.heappush(self.open_set, (f_score_start, self.counter, start_node))
        start_node.visited = True

    def step(self):
        """Processes a single node. Returns True if found, False if failed, None if searching."""
        if self.is_finished:
            return self.success
            
        if not self.open_set:
            self.is_finished = True
            self.success = False
            return False

        # Pop the lowest f_score node
        _, _, current = heapq.heappop(self.open_set)

        # Target reached!
        if current == self.end_node:
            self._reconstruct_path(current, self.net)
            self.is_finished = True
            self.success = True
            return True

        self.closed_set.add(current)

        for neighbor in self.grid.get_neighbors(current):
            if neighbor in self.closed_set:
                continue
                
            neighbor.visited = True 
            
            is_diagonal = (current.x != neighbor.x) and (current.y != neighbor.y)
            step_cost = 1.414 if is_diagonal else 1.0
            
            tentative_g_score = self.g_score[current] + step_cost
            
            if tentative_g_score < self.g_score.get(neighbor, float('inf')):
                neighbor.parent = current
                self.g_score[neighbor] = tentative_g_score
                
                f_score = tentative_g_score + octile_distance(neighbor, self.end_node)
                
                self.counter += 1
                heapq.heappush(self.open_set, (f_score, self.counter, neighbor))
        
        return None # Search is still ongoing

    def _reconstruct_path(self, current_node, net):
        path = []
        while current_node is not None:
            path.append(current_node)
            current_node = current_node.parent
        path.reverse()
        net.path = path