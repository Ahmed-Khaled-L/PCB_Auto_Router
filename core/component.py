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
        
        if not self.pins:
            self.pin_1_name = pin_name
            
        node = self.grid.get_node(global_x, global_y)
        if node:
            node.is_obstacle = False 
            self.pins[pin_name] = node

    def get_pin(self, pin_name):
        return self.pins.get(pin_name)


# ==========================================
# --- STANDARD THROUGH-HOLE COMPONENTS ---
# ==========================================

class DIP_IC(Component):
    """
    Standard Dual In-line Package (0.1" pin pitch).
    Default row spacing is 4 units (0.3" standard narrow DIP) or 7 units (0.6" wide DIP).
    """
    def __init__(self, grid, ref_des, start_x, start_y, pin_pairs, row_spacing=4):
        # Height perfectly matches pin count, no wasted vertical margin
        super().__init__(grid, ref_des, start_x, start_y, width=row_spacing + 1, height=pin_pairs, body_color=(30, 30, 35))
        
        for i in range(pin_pairs):
            self.add_pin(f"L{i+1}", local_x=0, local_y=i)             # Left side
            self.add_pin(f"R{i+1}", local_x=row_spacing, local_y=i)   # Right side

class Header(Component):
    """Standard 1xN 0.1" pitch vertical pin header."""
    def __init__(self, grid, ref_des, start_x, start_y, num_pins):
        # 1 cell wide, perfectly flush
        super().__init__(grid, ref_des, start_x, start_y, width=1, height=num_pins, body_color=(20, 20, 20))
        for i in range(num_pins):
            self.add_pin(f"P{i+1}", local_x=0, local_y=i)

class Resistor(Component):
    """Standard 1/4W Axial Resistor. Spans 4 cells (0.4" bend pitch)."""
    def __init__(self, grid, ref_des, start_x, start_y):
        # 1 cell tall, horizontal layout
        super().__init__(grid, ref_des, start_x, start_y, width=5, height=1, body_color=(120, 150, 180)) 
        self.add_pin("1", local_x=0, local_y=0)
        self.add_pin("2", local_x=4, local_y=0)

class Diode(Component):
    """Directional Axial diode (e.g. 1N4148) with Anode (A) and Cathode (K)."""
    def __init__(self, grid, ref_des, start_x, start_y):
        super().__init__(grid, ref_des, start_x, start_y, width=4, height=1, body_color=(200, 60, 60))
        self.add_pin("A", local_x=0, local_y=0) # Anode
        self.add_pin("K", local_x=3, local_y=0) # Cathode

class Capacitor(Component):
    """Standard Radial Electrolytic/Ceramic Capacitor (0.1" or 0.2" pitch)."""
    def __init__(self, grid, ref_des, start_x, start_y):
        super().__init__(grid, ref_des, start_x, start_y, width=2, height=1, body_color=(180, 140, 80))
        self.add_pin("1", local_x=0, local_y=0)
        self.add_pin("2", local_x=1, local_y=0)

class LED(Component):
    """Standard 5mm Through-Hole LED."""
    def __init__(self, grid, ref_des, start_x, start_y, color_rgb=(50, 255, 50)):
        # 2x2 footprint to represent the round plastic dome
        super().__init__(grid, ref_des, start_x, start_y, width=2, height=2, body_color=color_rgb)
        self.add_pin("A", local_x=0, local_y=1) # Anode (Longer leg)
        self.add_pin("K", local_x=1, local_y=1) # Cathode (Flat side)

class Transistor_TO92(Component):
    """Standard TO-92 3-pin Transistor (e.g., 2N3904) laid flat."""
    def __init__(self, grid, ref_des, start_x, start_y):
        # 3 pins in a single consecutive row
        super().__init__(grid, ref_des, start_x, start_y, width=3, height=1, body_color=(40, 40, 40))
        self.add_pin("1", local_x=0, local_y=0) # Emitter / Collector
        self.add_pin("2", local_x=1, local_y=0) # Base
        self.add_pin("3", local_x=2, local_y=0) # Collector / Emitter

class Battery(Component):
    """Standard Power source footprint."""
    def __init__(self, grid, ref_des, start_x, start_y):
        # A 4x5 block, dark green body
        super().__init__(grid, ref_des, start_x, start_y, width=4, height=5, body_color=(40, 100, 50))
        self.add_pin("+", local_x=0, local_y=0)
        self.add_pin("-", local_x=0, local_y=4)


# ==========================================
# --- ELECTROMECHANICAL & CONNECTORS ---
# ==========================================

class PushButton(Component):
    """Standard 6x6mm 4-pin Tactile Switch."""
    def __init__(self, grid, ref_des, start_x, start_y):
        super().__init__(grid, ref_des, start_x, start_y, width=3, height=3, body_color=(100, 100, 100))
        # Pins are on the corners
        self.add_pin("1A", local_x=0, local_y=0)
        self.add_pin("1B", local_x=2, local_y=0)
        self.add_pin("2A", local_x=0, local_y=2)
        self.add_pin("2B", local_x=2, local_y=2)

class Potentiometer(Component):
    """Standard 3-pin Rotary Potentiometer (Trimpot)."""
    def __init__(self, grid, ref_des, start_x, start_y):
        # Triangular pin layout
        super().__init__(grid, ref_des, start_x, start_y, width=3, height=2, body_color=(30, 80, 150))
        self.add_pin("1", local_x=0, local_y=1)  # CCW
        self.add_pin("W", local_x=1, local_y=0)  # Wiper
        self.add_pin("3", local_x=2, local_y=1)  # CW


# ==========================================
# --- SURFACE MOUNT (SMD) COMPONENTS ---
# ==========================================

class SMD_Passive(Component):
    """Generic 1206/0805 SMD Resistor or Capacitor."""
    def __init__(self, grid, ref_des, start_x, start_y):
        # Very small 2x1 footprint
        super().__init__(grid, ref_des, start_x, start_y, width=2, height=1, body_color=(200, 200, 200))
        self.add_pin("1", local_x=0, local_y=0)
        self.add_pin("2", local_x=1, local_y=0)

class QFP_IC(Component):
    """Quad Flat Package: A square chip with pins on all four sides."""
    def __init__(self, grid, ref_des, start_x, start_y, pins_per_side):
        size = pins_per_side + 1
        super().__init__(grid, ref_des, start_x, start_y, width=size + 1, height=size + 1, body_color=(35, 35, 40))
        
        for i in range(pins_per_side):
            self.add_pin(f"T{i+1}", local_x=i+1, local_y=0)          # Top edge
            self.add_pin(f"B{i+1}", local_x=i+1, local_y=size)       # Bottom edge
            self.add_pin(f"L{i+1}", local_x=0, local_y=i+1)          # Left edge
            self.add_pin(f"R{i+1}", local_x=size, local_y=i+1)       # Right edge