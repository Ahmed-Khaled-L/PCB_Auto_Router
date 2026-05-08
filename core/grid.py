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
        """Returns valid adjacent nodes, allowing traces and pins of the same net to be walked on."""
        neighbors = []
        directions = [
            (0, -1), (0, 1), (-1, 0), (1, 0),   
            (-1, -1), (1, -1), (-1, 1), (1, 1)  
        ]
        
        for dx, dy in directions:
            neighbor = self.get_node(node.x + dx, node.y + dy)
            
            if neighbor:
                is_blocked = neighbor.is_obstacle
                
                # --- FIX: REMOVED neighbor.is_trace ---
                # If the obstacle is ANY node in our electrical group (trace or pin), bypass it!
                if is_blocked and current_net:
                    if getattr(neighbor, 'net_group', None) == getattr(current_net, 'group_id', -1):
                        is_blocked = False

                if not is_blocked:
                    if dx != 0 and dy != 0: 
                        adj1 = self.get_node(node.x + dx, node.y)
                        adj2 = self.get_node(node.x, node.y + dy)
                        
                        # Apply the identical group bypass logic to diagonal clipping
                        adj1_blocked = adj1.is_obstacle if adj1 else False
                        if adj1_blocked and adj1 and current_net:
                            if getattr(adj1, 'net_group', None) == getattr(current_net, 'group_id', -1):
                                adj1_blocked = False
                                
                        adj2_blocked = adj2.is_obstacle if adj2 else False
                        if adj2_blocked and adj2 and current_net:
                            if getattr(adj2, 'net_group', None) == getattr(current_net, 'group_id', -1):
                                adj2_blocked = False

                        if adj1_blocked or adj2_blocked:
                            continue 

                    neighbors.append(neighbor)
        return neighbors

    def lock_path(self, net):
        # 1. Lock the traces
        for node in net.path[1:-1]:
            node.is_obstacle = True
            node.is_trace = True
            node.net_group = getattr(net, 'group_id', None)
        
        # 2. FIX: Tag the start/end pins inside the GRID MATRIX
        # Do not rely on net.start_node as it may be a detached factory object
        start_grid_node = self.get_node(net.start_node.x, net.start_node.y)
        if start_grid_node:
            start_grid_node.net_group = getattr(net, 'group_id', None)
            
        end_grid_node = self.get_node(net.end_node.x, net.end_node.y)
        if end_grid_node:
            end_grid_node.net_group = getattr(net, 'group_id', None)

    def add_obstacle(self, x, y):
        node = self.get_node(x, y)
        if node:
            node.is_obstacle = True

    def reset_search_states(self):
        """
        Loops through the entire matrix and clears the 'visited' and 'parent' 
        flags so the A* router starts with a fresh mathematical canvas.
        """
        for x in range(self.width):
            for y in range(self.height):
                self.matrix[x][y].reset_search_state()


    def clear_all_routes(self, nets=None):
        """NUCLEAR SWEEP: Obliterates all optimizer ghost traces and group tags."""
        for x in range(self.width):
            for y in range(self.height):
                node = self.matrix[x][y]
                
                # 1. Revert any routed traces to walkable floor space
                if getattr(node, 'is_trace', False):
                    node.is_obstacle = False
                    node.is_trace = False
                    
                # 2. PURGE ALL GROUP TAGS (Ghost T-Junction prevention)
                # Physical pins keep is_obstacle=True, but lose their group identity
                # until they are actively re-tagged by lock_path().
                node.net_group = None
                
        # 3. Wipe the object arrays so PyGame visualizer starts perfectly fresh
        if nets:
            for net in nets:
                net.path = []
                net.search_history = []
                
        self.reset_search_states()