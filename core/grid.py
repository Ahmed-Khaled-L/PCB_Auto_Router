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
        """Returns valid adjacent nodes. A node is only blocked if it belongs to an alien net."""
        neighbors = []
        directions = [
            (0, -1), (0, 1), (-1, 0), (1, 0),   
            (-1, -1), (1, -1), (-1, 1), (1, 1)  
        ]
        
        group_id = getattr(current_net, 'group_id', -1) if current_net else -1

        # A node blocks us ONLY if it is an obstacle AND does not share our net_group
        def is_blocked(n):
            return n and n.is_obstacle and getattr(n, 'net_group', None) != group_id

        for dx, dy in directions:
            neighbor = self.get_node(node.x + dx, node.y + dy)
            
            if not neighbor or is_blocked(neighbor):
                continue
                
            # Apply identical blockage logic to diagonal clipping
            if dx != 0 and dy != 0: 
                adj1 = self.get_node(node.x + dx, node.y)
                adj2 = self.get_node(node.x, node.y + dy)
                if is_blocked(adj1) or is_blocked(adj2):
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
        """NUCLEAR SWEEP: Obliterates optimizer paths efficiently via Net objects."""
        if nets:
            for net in nets:
                # Revert path spaces to walkable floor
                for node in net.path[1:-1]:
                    node.is_obstacle = False
                    node.net_group = None
                    
                # Untag physical pins (they remain obstacles, but lose group identity)
                for target in (net.start_node, net.end_node):
                    grid_node = self.get_node(target.x, target.y)
                    if grid_node:
                        grid_node.net_group = None
                        
                # Wipe objects for visualizer
                net.path = []
                net.search_history = []
                
        self.reset_search_states()