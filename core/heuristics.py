import math


def manhattan_distance(node_a, node_b):
    """
    Calculates the Manhattan distance between two nodes.
    This is the optimal heuristic for a 4-way orthogonal grid.
    
    Formula: h(n) = |x1 - x2| + |y1 - y2|
    """
    return abs(node_a.x - node_b.x) + abs(node_a.y - node_b.y)

def euclidean_distance(node_a, node_b):
    """
    Provided for future-proofing. 
    Use this instead if you ever upgrade to an 8-way (diagonal) grid.
    """
    return math.sqrt((node_a.x - node_b.x)**2 + (node_a.y - node_b.y)**2)


def octile_distance(node_a, node_b):
    """
    Optimal heuristic for an 8-way grid.
    Orthogonal cost = 1, Diagonal cost = 1.414
    """
    dx = abs(node_a.x - node_b.x)
    dy = abs(node_a.y - node_b.y)
    
    D = 1       # Cost of moving orthogonally
    D2 = 1.414  # Cost of moving diagonally
    
    return D * (dx + dy) + (D2 - 2 * D) * min(dx, dy)