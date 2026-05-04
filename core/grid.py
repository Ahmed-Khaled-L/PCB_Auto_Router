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

    def get_neighbors(self, node):
        """Returns valid adjacent nodes (8-way: Orthogonal and Diagonal)."""
        neighbors = []
        directions = [
            (0, -1), (0, 1), (-1, 0), (1, 0),   # N, S, W, E
            (-1, -1), (1, -1), (-1, 1), (1, 1)  # NW, NE, SW, SE
        ]
        
        for dx, dy in directions:
            neighbor = self.get_node(node.x + dx, node.y + dy)
            
            if neighbor and not neighbor.is_obstacle:
                # Prevent diagonal clipping through obstacle corners
                if dx != 0 and dy != 0: # If this is a diagonal move
                    adj1 = self.get_node(node.x + dx, node.y)
                    adj2 = self.get_node(node.x, node.y + dy)
                    
                    # If either adjacent orthogonal node is an obstacle, block the diagonal
                    if (adj1 and adj1.is_obstacle) or (adj2 and adj2.is_obstacle):
                        continue 

                neighbors.append(neighbor)
                
        return neighbors

    def add_obstacle(self, x, y):
        node = self.get_node(x, y)
        if node:
            node.is_obstacle = True

    def lock_path(self, net):
        """
        Turns a successfully routed net's path into permanent obstacles.
        This ensures subsequent nets cannot short-circuit across it.
        """
        if not net.path:
            return
            
        for node in net.path:
            # By setting this to True, get_neighbors() will automatically 
            # prevent future nets from stepping on these coordinates.
            node.is_obstacle = True
            
        print(f"[GRID] Locked path for net from ({net.start_node.x}, {net.start_node.y}) to ({net.end_node.x}, {net.end_node.y}).")

    def reset_search_states(self):
        """
        Loops through the entire matrix and clears the 'visited' and 'parent' 
        flags so the A* router starts with a fresh mathematical canvas.
        """
        for x in range(self.width):
            for y in range(self.height):
                self.matrix[x][y].reset_search_state()


    def clear_all_routes(self, nets):
        """
        Removes all routed traces from the grid, freeing up obstacles.
        This allows Simulated Annealing to try a fresh routing sequence.
        """
        for net in nets:
            if net.path:
                for node in net.path:
                    # Unmark as obstacle so future runs can use these cells
                    node.is_obstacle = False
            net.path = [] # Clear the stored path in the net
            
        # Clear the visited and parent flags for the next A* run
        self.reset_search_states()                