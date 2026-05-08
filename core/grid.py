from core.node import Node

class Grid:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        # Generate a 2D list of Node objects
        self.matrix = [[Node(x, y) for y in range(height)] for x in range(width)]

    def get_node(self, x, y):
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.matrix[x][y]
        return None

    def get_neighbors(self, node, current_net=None):
        """Returns valid adjacent nodes, allowing traces of the same net to be walked on."""
        neighbors = []
        directions = [
            (0, -1), (0, 1), (-1, 0), (1, 0),   
            (-1, -1), (1, -1), (-1, 1), (1, 1)  
        ]
        
        for dx, dy in directions:
            neighbor = self.get_node(node.x + dx, node.y + dy)
            
            if neighbor:
                is_blocked = neighbor.is_obstacle
                
                # --- NEW: TRACE MERGING ---
                # If the obstacle is our own electrical group's trace, it is a walkable highway!
                if is_blocked and neighbor.is_trace and current_net:
                    if getattr(neighbor, 'net_group', None) == getattr(current_net, 'group_id', -1):
                        is_blocked = False

                if not is_blocked:
                    if dx != 0 and dy != 0: 
                        adj1 = self.get_node(node.x + dx, node.y)
                        adj2 = self.get_node(node.x, node.y + dy)
                        
                        # Apply the identical group bypass logic to diagonal clipping
                        adj1_blocked = adj1.is_obstacle if adj1 else False
                        if adj1_blocked and adj1 and adj1.is_trace and current_net:
                            if getattr(adj1, 'net_group', None) == getattr(current_net, 'group_id', -1):
                                adj1_blocked = False
                                
                        adj2_blocked = adj2.is_obstacle if adj2 else False
                        if adj2_blocked and adj2 and adj2.is_trace and current_net:
                            if getattr(adj2, 'net_group', None) == getattr(current_net, 'group_id', -1):
                                adj2_blocked = False

                        if adj1_blocked or adj2_blocked:
                            continue 

                    neighbors.append(neighbor)
        return neighbors

    def add_obstacle(self, x, y):
        node = self.get_node(x, y)
        if node:
            node.is_obstacle = True

    def lock_path(self, net):
        if not net.path:
            return
            
        # Skip the start and end nodes [1:-1] so we don't accidentally alter component pads
        for node in net.path[1:-1]:
            node.is_obstacle = True
            node.is_trace = True 
            node.net_group = getattr(net, 'group_id', None) # Mark ownership

    def reset_search_states(self):
        """
        Loops through the entire matrix and clears the 'visited' and 'parent' 
        flags so the A* router starts with a fresh mathematical canvas.
        """
        for x in range(self.width):
            for y in range(self.height):
                self.matrix[x][y].reset_search_state()


    def clear_all_routes(self, nets):
        for net in nets:
            if net.path:
                for node in net.path[1:-1]:
                    node.is_obstacle = False
                    node.is_trace = False 
                    node.net_group = None
            net.path = [] 
            
        self.reset_search_states()