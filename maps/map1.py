from core.grid import Grid
from core.net import Net
from core.multi_net_manager import MultiNetManager
from core.component import DIP_IC, Resistor, Diode, Header

def load_map():
    """Real-life Simple Circuit: ESP32 with Power Header and Status LED."""
    grid = Grid(45, 30)
    manager = MultiNetManager()
    components = []

    # 1. Place Components
    # Power Input Header
    pwr = Header(grid, "J_PWR", start_x=2, start_y=12, num_pins=2)
    
    # ESP32 Microcontroller (Represented as a 16-pin IC)
    esp32 = DIP_IC(grid, "U1_ESP32", start_x=16, start_y=8, pin_pairs=8)
    
    # Status LED & Resistor
    r1 = Resistor(grid, "R1", start_x=32, start_y=8)
    led = Diode(grid, "D1_LED", start_x=32, start_y=15)
    
    components.extend([pwr, esp32, r1, led])

    # 2. Wire the Circuit
    # Net 1: 3.3V Power (Header P1 -> ESP32 Pin L1)
    manager.add_net(Net(pwr.get_pin("P1"), esp32.get_pin("L1"), color=(255, 50, 50)))
    
    # Net 2: Ground Return (Header P2 -> ESP32 Pin L8)
    manager.add_net(Net(pwr.get_pin("P2"), esp32.get_pin("L8"), color=(100, 100, 100)))
    
    # Net 3: GPIO Signal (ESP32 Pin R1 -> Resistor Pin 1)
    manager.add_net(Net(esp32.get_pin("R1"), r1.get_pin("1"), color=(50, 255, 50)))
    
    # Net 4: Resistor to LED Anode
    manager.add_net(Net(r1.get_pin("2"), led.get_pin("A"), color=(255, 200, 50)))
    
    # Net 5: LED Cathode back to Ground (ESP32 Pin R8)
    manager.add_net(Net(led.get_pin("K"), esp32.get_pin("R8"), color=(100, 100, 100)))

    return grid, manager, components