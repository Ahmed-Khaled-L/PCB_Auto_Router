class Node:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.is_obstacle = False
        self.is_trace = False # <-- NEW: Distinguishes traces from static keep-outs
        self.parent = None  # Used to reconstruct the path
        self.visited = False # Used by the router

    def reset_search_state(self):
        """Clears routing data for subsequent runs."""
        self.parent = None
        self.visited = False