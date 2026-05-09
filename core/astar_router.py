import heapq
from core.heuristics import manhattan_distance
from core.interfaces.base_router import BaseRouter

class AStarRouter(BaseRouter):
    def route(self, net):
        """Professional EDA Vector Routing with 'Super Highway' Mechanic."""
        net.search_history = []
        net.path = []
        start_node, end_node = net.start_node, net.end_node
        
        start_node.is_obstacle = False
        end_node.is_obstacle = False
        
        try:
            open_set = []
            counter = 0
            initial_state = (start_node, 0, 0)
            g_score = {initial_state: 0}
            came_from = {}
            
        
            heuristic = lambda n: manhattan_distance(n, end_node) * 10
            
            heapq.heappush(open_set, (heuristic(start_node), counter, initial_state))
            start_node.visited = True
            
            while open_set:
                _, _, current_state = heapq.heappop(open_set)
                current_node, p_dx, p_dy = current_state
                
                if current_node not in net.search_history:
                    net.search_history.append(current_node)
                
                
                if current_node == end_node:
                    return self._reconstruct_state_path(current_state, came_from, net)
                
                for neighbor in self.grid.get_neighbors(current_node, net):
                    n_dx = neighbor.x - current_node.x
                    n_dy = neighbor.y - current_node.y
                    neighbor_state = (neighbor, n_dx, n_dy)
                    neighbor.visited = True
                    
                    
                    if getattr(neighbor, 'net_group', None) == getattr(net, 'group_id', -1):
                        step_cost, bend_penalty = 1, 0
                    else:
                        is_diagonal = (n_dx != 0 and n_dy != 0)
                        step_cost = 25 if is_diagonal else 10 
                        bend_penalty = self._calculate_bend_penalty(p_dx, p_dy, n_dx, n_dy, is_diagonal)
                    
                    tentative_g_score = g_score[current_state] + step_cost + bend_penalty
                    
                    if tentative_g_score < g_score.get(neighbor_state, float('inf')):
                        came_from[neighbor_state] = current_state
                        g_score[neighbor_state] = tentative_g_score
                        
                        f_score = tentative_g_score + heuristic(neighbor)
                        counter += 1
                        heapq.heappush(open_set, (f_score, counter, neighbor_state))
                        
            return False
            
        finally:
            start_node.is_obstacle = True
            end_node.is_obstacle = True

    def _calculate_bend_penalty(self, p_dx, p_dy, n_dx, n_dy, is_diagonal):
        """Calculates momentum penalties without cluttering the main loop."""
        if (p_dx, p_dy) == (0, 0) or (p_dx == n_dx and p_dy == n_dy):
            return 0
            
        dot_product = (p_dx * n_dx) + (p_dy * n_dy)
        if is_diagonal and (p_dx == 0 or p_dy == 0): return 5
        if not is_diagonal and (p_dx != 0 and p_dy != 0): return 5
        if dot_product == 0: return 30   # 90-degree bend
        if dot_product < 0: return 100   # U-turn
        if is_diagonal: return 50
        return 0

    def _reconstruct_state_path(self, current_state, came_from, net):
        """Yields a pure, unbroken path array leading directly to the node."""
        path = []
        while current_state in came_from:
            path.append(current_state[0])
            current_state = came_from[current_state]
            
        path.append(net.start_node)
        path.reverse()
        net.path = path
        return True