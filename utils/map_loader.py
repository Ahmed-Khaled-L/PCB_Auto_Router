import json
from core.grid import Grid
from core.net import Net
from core.multi_net_manager import MultiNetManager
import core.component as comps

class MapLoader:
    # String-to-Class Registry for the Factory Pattern
    COMPONENT_REGISTRY = {
        "DIP_IC": comps.DIP_IC,
        "Resistor": comps.Resistor,
        "Header": comps.Header,
        "Capacitor": comps.Capacitor,
        "Diode": comps.Diode,
        "Battery": comps.Battery,
        "Transistor": comps.Transistor,
        "QFP_IC": comps.QFP_IC
    }

    @staticmethod
    def load_from_json(filepath):
        """Dynamically loads a map, components, and nets from a JSON file."""
        with open(filepath, 'r') as f:
            data = json.load(f)
            
        grid = Grid(data["grid"]["width"], data["grid"]["height"])
        manager = MultiNetManager([])
        components = []
        
        # 1. Instantiate Components dynamically
        for comp_data in data["components"]:
            comp_type = comp_data["type"]
            if comp_type not in MapLoader.COMPONENT_REGISTRY:
                raise ValueError(f"Unknown component type: {comp_type}")
                
            CompClass = MapLoader.COMPONENT_REGISTRY[comp_type]
            kwargs = comp_data.get("args", {})
            
            instance = CompClass(
                grid=grid, 
                ref_des=comp_data["ref"], 
                start_x=comp_data["x"], 
                start_y=comp_data["y"], 
                **kwargs
            )
            components.append(instance)
            
        # Helper function to find a specific pin by "REF:PIN" string (e.g. "U1:L1")
        def get_pin_by_address(address):
            ref, pin_name = address.split(":")
            for comp in components:
                if comp.ref_des == ref:
                    return comp.get_pin(pin_name)
            raise ValueError(f"Could not find pin {address}")

        # 2. Wire the Nets
        for i, net_data in enumerate(data["nets"]):
            start_node = get_pin_by_address(net_data["start"])
            end_node = get_pin_by_address(net_data["end"])
            color = tuple(net_data.get("color", [50, 150, 255]))
            
            net = Net(start_node, end_node, color=color)
            net.id = f"Net_{i+1}" # Set an ID for the metrics logger
            manager.add_net(net)

        return grid, manager, components