class Component:
    def __init__(self, grid, ref_des, start_x, start_y, width, height, body_color=(40, 40, 45)):
        self.ref_des = ref_des
        self.grid = grid
        self.start_x = start_x
        self.start_y = start_y
        self.width = width
        self.height = height
        self.body_color = body_color
        self.pins = {}
        self.pin_1_name = None # Track Pin 1 for visual marking

        self._place_body_on_grid()

    def _place_body_on_grid(self):
        for x in range(self.start_x, self.start_x + self.width):
            for y in range(self.start_y, self.start_y + self.height):
                self.grid.add_obstacle(x, y)

    def add_pin(self, pin_name, local_x, local_y):
        global_x = self.start_x + local_x
        global_y = self.start_y + local_y
        
        # The first pin added is registered as Pin 1
        if not self.pins:
            self.pin_1_name = pin_name
            
        node = self.grid.get_node(global_x, global_y)
        if node:
            node.is_obstacle = False 
            self.pins[pin_name] = node

    def get_pin(self, pin_name):
        return self.pins.get(pin_name)

# --- STANDARD FOOTPRINT LIBRARY ---

class DIP_IC(Component):
    """Dual In-line Package: Pins on the left and right sides."""
    def __init__(self, grid, ref_des, start_x, start_y, pin_pairs):
        width = 6
        height = pin_pairs + 2
        super().__init__(grid, ref_des, start_x, start_y, width, height, body_color=(30, 30, 35))
        
        # Auto-generate pins
        for i in range(pin_pairs):
            self.add_pin(f"L{i+1}", local_x=0, local_y=i+1)           # Left side
            self.add_pin(f"R{i+1}", local_x=width-1, local_y=i+1)     # Right side

class Resistor(Component):
    """Standard 1206 or Axial Resistor: Horizontal body, pins on ends."""
    def __init__(self, grid, ref_des, start_x, start_y):
        super().__init__(grid, ref_des, start_x, start_y, width=6, height=2, body_color=(70, 100, 150)) # Blue body
        self.add_pin("1", local_x=0, local_y=0)
        self.add_pin("2", local_x=5, local_y=0)

class Header(Component):
    """Vertical pin header for external connections."""
    def __init__(self, grid, ref_des, start_x, start_y, num_pins):
        super().__init__(grid, ref_des, start_x, start_y, width=2, height=num_pins, body_color=(20, 20, 20))
        for i in range(num_pins):
            self.add_pin(f"P{i+1}", local_x=0, local_y=i)


class Capacitor(Component):
    """Standard ceramic or electrolytic capacitor footprint."""
    def __init__(self, grid, ref_des, start_x, start_y):
        # A small 3x3 footprint, tan body color
        super().__init__(grid, ref_des, start_x, start_y, width=3, height=3, body_color=(180, 140, 80))
        self.add_pin("1", local_x=0, local_y=1)
        self.add_pin("2", local_x=2, local_y=1)

class Diode(Component):
    """Directional diode with Anode (A) and Cathode (K)."""
    def __init__(self, grid, ref_des, start_x, start_y):
        # A 4x2 footprint, red/glass body color
        super().__init__(grid, ref_des, start_x, start_y, width=4, height=2, body_color=(200, 60, 60))
        self.add_pin("A", local_x=0, local_y=0) # Anode
        self.add_pin("K", local_x=3, local_y=0) # Cathode

class Battery(Component):
    """Power source footprint."""
    def __init__(self, grid, ref_des, start_x, start_y):
        # A larger 4x5 block, dark green body
        super().__init__(grid, ref_des, start_x, start_y, width=4, height=5, body_color=(40, 100, 50))
        self.add_pin("+", local_x=0, local_y=0)
        self.add_pin("-", local_x=0, local_y=4)


class Transistor(Component):
    """Standard 3-pin Transistor (e.g., TO-92 or SOT-23)."""
    def __init__(self, grid, ref_des, start_x, start_y):
        # A 4x2 body, dark grey
        super().__init__(grid, ref_des, start_x, start_y, width=4, height=2, body_color=(60, 60, 65))
        self.add_pin("E", local_x=0, local_y=0) # Emitter
        self.add_pin("B", local_x=1, local_y=1) # Base (offset)
        self.add_pin("C", local_x=2, local_y=0) # Collector

class QFP_IC(Component):
    """Quad Flat Package: A square chip with pins on all four sides."""
    def __init__(self, grid, ref_des, start_x, start_y, pins_per_side):
        # Size dynamically scales based on pins
        size = pins_per_side + 2
        super().__init__(grid, ref_des, start_x, start_y, width=size, height=size, body_color=(35, 35, 40))
        
        # Auto-generate pins on Top, Bottom, Left, and Right
        for i in range(pins_per_side):
            self.add_pin(f"T{i+1}", local_x=i+1, local_y=0)          # Top edge
            self.add_pin(f"B{i+1}", local_x=i+1, local_y=size-1)     # Bottom edge
            self.add_pin(f"L{i+1}", local_x=0, local_y=i+1)          # Left edge
            self.add_pin(f"R{i+1}", local_x=size-1, local_y=i+1)     # Right edge