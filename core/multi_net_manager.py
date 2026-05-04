from core.heuristics import euclidean_distance

class MultiNetManager:
    def __init__(self):
        self.nets = []
        self.current_index = 0

    def add_net(self, net):
        """Adds a net to the pending list."""
        self.nets.append(net)

    def sort_nets_shortest_first(self):
        """
        Sorts the nets in-place from shortest to longest 
        using the straight-line Euclidean distance.
        """
        self.nets.sort(key=lambda net: euclidean_distance(net.start_node, net.end_node))
        print("[MANAGER] Nets sorted by Euclidean distance.")

    def get_next_net(self):
        """Returns the next net to route, or None if all are completed."""
        if self.current_index < len(self.nets):
            next_net = self.nets[self.current_index]
            self.current_index += 1
            return next_net
        return None

    def has_pending_nets(self):
        """Checks if there are more nets waiting to be routed."""
        return self.current_index < len(self.nets)

    def get_all_nets(self):
        """Returns all nets for rendering purposes."""
        return self.nets