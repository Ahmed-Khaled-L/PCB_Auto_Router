import heapq
from core.heuristics import manhattan_distance
from core.interfaces.base_router import BaseRouter

class AStarRouter(BaseRouter):
    def route(self, net):
        """Professional EDA Vector Routing with Anti-Diagonal Forcing."""
        net.search_history = []
        net.path = []
        start_node = net.start_node
        end_node = net.end_node
        
        start_node.is_obstacle = False
        end_node.is_obstacle = False
        
        try:
            open_set = []
            counter = 0
            
            # STATE SPACE: (Node, delta_x, delta_y)
            initial_state = (start_node, 0, 0)
            g_score = {initial_state: 0}
            came_from = {}
            
            def heuristic(node_a, node_b):
                # Manhattan is mathematically tighter when diagonals are artificially penalized
                return manhattan_distance(node_a, node_b) * 10
            
            heapq.heappush(open_set, (heuristic(start_node, end_node), counter, initial_state))
            start_node.visited = True
            
            while open_set:
                _, _, current_state = heapq.heappop(open_set)
                current_node, p_dx, p_dy = current_state
                
                if current_node not in net.search_history:
                    net.search_history.append(current_node)
                
                # --- FIX 1: THE OUROBOROS PARADOX REMOVAL ---
                # Revert to strict target checking. We MUST reach the final pin.
                if current_node == end_node:
                    return self._reconstruct_state_path(current_state, came_from, net)
                
                for neighbor in self.grid.get_neighbors(current_node, net):
                    n_dx = neighbor.x - current_node.x
                    n_dy = neighbor.y - current_node.y
                    
                    neighbor_state = (neighbor, n_dx, n_dy)
                    neighbor.visited = True
                    
                    # --- FIX 2: THE "SUPER HIGHWAY" MECHANIC ---
                    is_shared_trace = (getattr(neighbor, 'net_group', None) == getattr(net, 'group_id', -1))
                    
                    if is_shared_trace:
                        # Existing traces of our group are highly attractive, 0-friction highways.
                        # The router will violently prefer to overlap them, creating natural T-Junctions!
                        step_cost = 1
                        bend_penalty = 0
                    else:
                        # Normal routing over empty floor space
                        is_diagonal = (n_dx != 0 and n_dy != 0)
                        step_cost = 25 if is_diagonal else 10 
                        
                        bend_penalty = 0
                        if (p_dx, p_dy) != (0, 0):
                            if (p_dx != n_dx) or (p_dy != n_dy):
                                dot_product = (p_dx * n_dx) + (p_dy * n_dy)
                                
                                if is_diagonal and (p_dx == 0 or p_dy == 0):
                                    bend_penalty = 5    
                                elif not is_diagonal and (p_dx != 0 and p_dy != 0):
                                    bend_penalty = 5    
                                elif dot_product == 0:
                                    bend_penalty = 30   
                                elif dot_product < 0:
                                    bend_penalty = 100  
                                    
                            elif is_diagonal:
                                bend_penalty = 50       
                    
                    tentative_g_score = g_score[current_state] + step_cost + bend_penalty
                    
                    if tentative_g_score < g_score.get(neighbor_state, float('inf')):
                        came_from[neighbor_state] = current_state
                        g_score[neighbor_state] = tentative_g_score
                        
                        f_score = tentative_g_score + heuristic(neighbor, end_node)
                        
                        counter += 1
                        heapq.heappush(open_set, (f_score, counter, neighbor_state))
                        
            return False
            
        finally:
            start_node.is_obstacle = True
            end_node.is_obstacle = True

    def _reconstruct_state_path(self, current_state, came_from, net):
        path = []
        while current_state in came_from:
            path.append(current_state[0])
            current_state = came_from[current_state]
            
        path.append(net.start_node)
        path.reverse()
        net.path = path
        return True