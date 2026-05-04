
#The Wire Definition

class Net:
    def __init__(self, start_node, end_node, color=(50, 150, 255)):
        self.start_node = start_node
        self.end_node = end_node
        self.path = []
        self.color = color  # RGB Tuple