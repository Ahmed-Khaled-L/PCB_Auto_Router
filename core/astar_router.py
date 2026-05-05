import heapq
from core.heuristics import octile_distance
from core.interfaces.base_router import BaseRouter

class AStarRouter(BaseRouter):
    def route(self, net):
        """Standard, synchronous A* search."""
        start_node = net.start_node
        end_node = net.end_node
        start_node.parent = None
        
        open_set = []
        counter = 0 
        g_score = {start_node: 0}
        closed_set = set()

        heapq.heappush(open_set, (octile_distance(start_node, end_node), counter, start_node))
        start_node.visited = True

        while open_set:
            # Pop the lowest f_score node
            _, _, current = heapq.heappop(open_set)

            # 1. Record this node for the GUI animation!
            if current not in net.search_history:
                net.search_history.append(current)

            # Target reached!
            if current == end_node:
                return self._reconstruct_path(current, net)

            closed_set.add(current)

            for neighbor in self.grid.get_neighbors(current):
                if neighbor in closed_set:
                    continue
                
                neighbor.visited = True
                
                # Check if moving diagonally
                is_diagonal = (current.x != neighbor.x) and (current.y != neighbor.y)
                step_cost = 1.414 if is_diagonal else 1.0

                # --- NEW: BEND PENALTY LOGIC ---
                bend_penalty = 0.0
                if current.parent is not None:
                    # Calculate previous direction
                    prev_dx = current.x - current.parent.x
                    prev_dy = current.y - current.parent.y
                    
                    # Calculate new direction
                    new_dx = neighbor.x - current.x
                    new_dy = neighbor.y - current.y
                    
                    # If the directions don't match, we are making a turn!
                    if (prev_dx != new_dx) or (prev_dy != new_dy):
                        bend_penalty = 100.0 # Add a small cost for turning
                
                # Add the step cost AND the penalty
                tentative_g_score = g_score[current] + step_cost + bend_penalty

                # If this path to neighbor is better than any previous one
                if tentative_g_score < g_score.get(neighbor, float('inf')):
                    neighbor.parent = current
                    g_score[neighbor] = tentative_g_score
                    f_score = tentative_g_score + octile_distance(neighbor, end_node)
                    
                    counter += 1
                    heapq.heappush(open_set, (f_score, counter, neighbor))
        
        # Open set emptied without reaching target
        return False