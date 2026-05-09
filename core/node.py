class Node:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.is_obstacle = False
        self.net_group = None  
        self.parent = None     
        self.visited = False   

    def reset_search_state(self):
        """Clears routing data for subsequent runs."""
        self.parent = None
        self.visited = False