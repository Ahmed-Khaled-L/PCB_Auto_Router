from core.grid import Grid
from core.net import Net
from core.component import Component
from core.multi_net_manager import MultiNetManager

class MapLoader:
    
    @staticmethod
    def load_deadlock_test():
        """Your exact Level 3 deadlock test, abstracted."""
        grid = Grid(30, 20)
        manager = MultiNetManager()
        
        # Abstracted Obstacle
        for x in range(10, 15):
            for y in range(5, 15):
                grid.add_obstacle(x, y)

        net1 = Net(grid.get_node(15, 0), grid.get_node(15, 19), color=(50, 200, 50))
        net2 = Net(grid.get_node(2, 10), grid.get_node(27, 10), color=(255, 200, 50))
        
        manager.add_net(net1)
        manager.add_net(net2)
        return grid, manager, [] # Empty component list for this basic map

    @staticmethod
    def load_microcontroller_board():
        """A realistic EDA view using standardized footprints."""
        grid = Grid(40, 30)
        manager = MultiNetManager()
        components = []

        from core.component import DIP_IC, Resistor, Header # Import the library

        # Place components using standard packages
        u1 = DIP_IC(grid, "U1", start_x=15, start_y=10, pin_pairs=6) # 12-pin IC
        r1 = Resistor(grid, "R1", start_x=5, start_y=8)
        r2 = Resistor(grid, "R2", start_x=5, start_y=15)
        j1 = Header(grid, "J1", start_x=34, start_y=12, num_pins=8)
        
        components.extend([u1, r1, r2, j1])

        # Connect the Nets
        manager.add_net(Net(r1.get_pin("2"), u1.get_pin("L1"), color=(50, 255, 255)))
        manager.add_net(Net(r2.get_pin("2"), u1.get_pin("L5"), color=(50, 255, 50)))
        manager.add_net(Net(u1.get_pin("R2"), j1.get_pin("P3"), color=(255, 100, 255)))
        manager.add_net(Net(u1.get_pin("R5"), j1.get_pin("P7"), color=(255, 200, 50)))

        return grid, manager, components

    @staticmethod
    def load_pocket_trap_test():
        """A trivial but undeniable proof of Simulated Annealing over Greedy A*."""
        grid = Grid(20, 12)
        manager = MultiNetManager()

        # 1. Build the "Pocket" (A room open only on the right side)
        for x in range(2, 7):
            grid.add_obstacle(x, 3) # Top wall
            grid.add_obstacle(x, 7) # Bottom wall
        for y in range(3, 8):
            grid.add_obstacle(2, y) # Back wall

        # 2. Net A: The Prisoner (Long Euclidean Distance)
        # Starts inside the pocket at (4, 5), wants to go to (18, 5)
        net_a = Net(grid.get_node(4, 5), grid.get_node(18, 5), color=(50, 255, 50))
        
        # 3. Net B: The Guard (Short Euclidean Distance)
        # Starts just outside the top mouth at (7, 2), ends at bottom mouth (7, 8)
        net_b = Net(grid.get_node(7, 2), grid.get_node(7, 8), color=(255, 50, 50))

        # Add them to the manager
        manager.add_net(net_a)
        manager.add_net(net_b)

        return grid, manager, []