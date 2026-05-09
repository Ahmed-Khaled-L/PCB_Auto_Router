class MultiNetManager:
    def __init__(self, nets):
        self.nets = nets
        self.optimizer = None 
        self.current_index = 0

        self._assign_net_groups()

    def _assign_net_groups(self):
        """Assigns shared nets using a clean, Pythonic Coordinate-based Union-Find."""
        parent = {}
        def find(i):
            
            if parent[i] == i: return i
            parent[i] = find(parent[i])
            return parent[i]
        
        def union(i, j):
            root_i, root_j = find(i), find(j)
            if root_i != root_j:
                parent[root_i] = root_j

        # Initialize each net to its own set
        pin_map = {}
        for i, net in enumerate(self.nets):
            parent[i] = i
            
            # If a pin coordinate was already mapped, union the sets together
            coords = [(net.start_node.x, net.start_node.y), (net.end_node.x, net.end_node.y)]
            for coord in coords:
                if coord in pin_map:
                    union(i, pin_map[coord])
                else:
                    pin_map[coord] = i
                    
        # Apply the resolved group IDs to the nets
        for i, net in enumerate(self.nets):
            net.group_id = find(i)

    def prepare_queue(self):
        """Delegates the heavy lifting to the injected strategy."""
        if self.optimizer:
            self.nets = self.optimizer.optimize(self.nets)
        else:
            print("[MANAGER] No optimizer provided. Nets will route in default order.")