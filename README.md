Here is the complete, professional-grade documentation for the PCB Auto-Router simulation as it currently stands. You can drop this directly into a `README.md` file in your project repository or use it as the technical manual for your final report.

---

# PCB Auto-Router: User & Developer Guide

## Overview
This Python-based Electronic Design Automation (EDA) simulation engine utilizes an A* search algorithm with an Octile Distance heuristic to route multiple electrical nets sequentially. It features a custom Model-View-Controller (MVC) architecture, abstracting the mathematical graph (Grid) from the physical representation (Components) and the visual output (Pygame Renderer).

---

## 1. Running the Program

The application is designed to be lightweight and run directly from the command line.

**Prerequisites:**
Ensure you have Python 3 installed along with the Pygame library:
```bash
pip install pygame
```

**Execution:**
From the root directory of the project, run the main entry point:
```bash
python3 main.py
```
*Note: The application window will remain open until you close it. Execution metrics (time, visited nodes, path length) are automatically saved to `routing_metrics.log` in the root directory.*

---

## 2. The Component Library
The engine uses a dynamic footprint generator located in `core/component.py`. Components automatically block out physical space on the grid and provide routable connection pins. 

Currently available standard components:

* **`DIP_IC` (Integrated Circuit):** * *Visuals:* Dark grey body, dynamic size based on pin count. Pin 1 is marked with gold.
    * *Usage:* `DIP_IC(grid, ref_des, start_x, start_y, pin_pairs)`
    * *Pins:* Addressed as `"L1"`, `"L2"` (Left side) and `"R1"`, `"R2"` (Right side).
* **`Header`:** * *Visuals:* Black body, vertical alignment.
    * *Usage:* `Header(grid, ref_des, start_x, start_y, num_pins)`
    * *Pins:* Addressed as `"P1"`, `"P2"`, etc.
* **`Resistor`:** * *Visuals:* Blue body, horizontal alignment (6x2 cells).
    * *Usage:* `Resistor(grid, ref_des, start_x, start_y)`
    * *Pins:* Addressed as `"1"` and `"2"`.
* **`Capacitor`:** * *Visuals:* Tan body, small square footprint (3x3 cells).
    * *Usage:* `Capacitor(grid, ref_des, start_x, start_y)`
    * *Pins:* Addressed as `"1"` and `"2"`.
* **`Diode`:** * *Visuals:* Red body, directional alignment.
    * *Usage:* `Diode(grid, ref_des, start_x, start_y)`
    * *Pins:* Addressed as `"A"` (Anode) and `"K"` (Cathode).
* **`Battery`:** * *Visuals:* Dark green body, larger rectangular block.
    * *Usage:* `Battery(grid, ref_des, start_x, start_y)`
    * *Pins:* Addressed as `"+"` and `"-"`.

---

## 3. Creating Custom Maps

To design a new layout or test a specific circuit, you create a new Python script inside the `maps/` directory. 

### Step 1: Create the Map File
Create a file such as `maps/map2_motor_driver.py` and define a `load_map()` function. 

### Step 2: Define the Environment Template
Use the following boilerplate to set up the grid, place components, and wire the nets:

```python
from core.grid import Grid
from core.net import Net
from core.multi_net_manager import MultiNetManager
from core.component import DIP_IC, Resistor, Diode, Header, Battery, Capacitor

def load_map():
    # 1. Initialize Grid (Width, Height) and Manager
    grid = Grid(45, 30)
    manager = MultiNetManager()
    components = []

    # 2. Instantiate Components (X, Y are top-left coordinates)
    pwr = Header(grid, "J1", start_x=5, start_y=5, num_pins=2)
    u1 = DIP_IC(grid, "U1", start_x=20, start_y=10, pin_pairs=4)
    r1 = Resistor(grid, "R1", start_x=35, start_y=10)
    
    # Register components to the render list
    components.extend([pwr, u1, r1])

    # 3. Wire the Circuit (Point-to-Point Nets)
    # Syntax: Net(Start_Pin, End_Pin, color=(R, G, B))
    manager.add_net(Net(pwr.get_pin("P1"), u1.get_pin("L1"), color=(255, 50, 50)))
    manager.add_net(Net(u1.get_pin("R1"), r1.get_pin("1"), color=(50, 255, 50)))

    return grid, manager, components
```

### Step 3: Activate the Map
To render your newly created map, open `gui/app.py` and change the import statement at the top of the file:

```python
# In gui/app.py
from maps.map2_motor_driver import load_map # <-- Point this to your new file

class App:
    def __init__(self):
        # The app automatically unpacks your map here:
        self.grid, self.manager, self.components = load_map()
        # ...
```

---

## 4. Visual Interface Guide

When the Pygame window opens, it visually represents the state of the A* routing engine:
* **Faint Purple Cells:** These represent the "Search Space" (nodes visited by the A* algorithm).
* **Silkscreen Text:** White text dynamically labels components with their Reference Designators (e.g., U1, R1).
* **Gold Pins:** A gold marker always indicates "Pin 1" or the primary orientation pin (e.g., Anode on a Diode) for physical chips.
* **Solid Traces:** The routed wires are drawn as continuous lines connecting the centers of the grid cells, mirroring professional PCB copper traces. 
* **Animations:** The application processes a configurable number of nodes per frame (controlled by `self.steps_per_frame` in `app.py`), allowing you to watch the AI navigate around components in real-time.