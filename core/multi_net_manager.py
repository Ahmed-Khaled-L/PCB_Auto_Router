# core/multi_net_manager.py
class MultiNetManager:
    def __init__(self, nets):
        self.nets = nets
        self.optimizer = None # Will be injected by the App
        self.current_index = 0

    def _assign_net_groups(self):
        """Auto-detects shared nets and groups them into electrical highways."""
        # 1. Give every net a unique group ID initially
        for i, net in enumerate(self.nets):
            net.group_id = i

        # 2. Merge groups if they share a pad (Poor-man's Union Find)
        changed = True
        while changed:
            changed = False
            for n1 in self.nets:
                for n2 in self.nets:
                    if n1.group_id != n2.group_id:
                        # If they touch the same physical pin, they are electrically identical
                        if (n1.start_node in (n2.start_node, n2.end_node) or 
                            n1.end_node in (n2.start_node, n2.end_node)):
                            n2.group_id = n1.group_id
                            changed = True

    def prepare_queue(self):
        """Delegates the heavy lifting to the injected strategy."""
        if self.optimizer:
            self.nets = self.optimizer.optimize(self.nets)
        else:
            print("[MANAGER] No optimizer provided. Nets will route in default order.")
