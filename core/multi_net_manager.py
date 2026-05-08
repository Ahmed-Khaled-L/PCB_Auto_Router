class MultiNetManager:
    def __init__(self, nets):
        self.nets = nets
        self.optimizer = None 
        self.current_index = 0

        self._assign_net_groups()

    def _assign_net_groups(self):
        """Auto-detects shared nets and groups them into electrical highways."""
        # 1. Give every net a unique group ID initially
        for i, net in enumerate(self.nets):
            net.group_id = i

        # 2. Merge groups if they share a pad (Coordinate-based Union Find)
        changed = True
        while changed:
            changed = False
            for n1 in self.nets:
                for n2 in self.nets:
                    if n1.group_id != n2.group_id:
                        # FIX: Compare via immutable coordinate tuples, NOT object identity!
                        n1_start = (n1.start_node.x, n1.start_node.y)
                        n1_end = (n1.end_node.x, n1.end_node.y)
                        n2_start = (n2.start_node.x, n2.start_node.y)
                        n2_end = (n2.end_node.x, n2.end_node.y)
                        
                        # If any physical pin locations overlap, they belong together
                        if n1_start in (n2_start, n2_end) or n1_end in (n2_start, n2_end):
                            n2.group_id = n1.group_id
                            changed = True

    def prepare_queue(self):
        """Delegates the heavy lifting to the injected strategy."""
        if self.optimizer:
            self.nets = self.optimizer.optimize(self.nets)
        else:
            print("[MANAGER] No optimizer provided. Nets will route in default order.")