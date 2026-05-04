import math
import random
import copy

class SimulatedAnnealingManager:
    def __init__(self, grid, nets, astar_router):
        self.grid = grid
        self.nets = nets
        self.router = astar_router
        
    def _route_sync(self, net):
        """Wraps the stepper-based A* router into a synchronous background function."""
        self.router.initialize_search(net)
        while True:
            result = self.router.step()
            if result is not None:
                return result # True if path found, False if failed
                
    def evaluate_sequence(self, net_sequence):
        """Runs A* on a specific order of nets and returns the 'Energy' (Cost)."""
        # Wipe the board clean using the new Grid method
        self.grid.clear_all_routes(self.nets) 
        
        unrouted_count = 0
        total_wirelength = 0
        
        for net in net_sequence:
            # 1. Route the net instantly
            success = self._route_sync(net)
            
            # 2. Process the result
            if not success:
                unrouted_count += 1
            else:
                total_wirelength += len(net.path)
                # 3. CRITICAL: Lock the successful path so the next net routes around it
                self.grid.lock_path(net)
                
        energy = (unrouted_count * 10000) + total_wirelength
        return energy, unrouted_count
        
    def get_neighbor(self, current_sequence):
        """Swaps two random nets to create a new sequence to test."""
        new_sequence = current_sequence.copy()
        idx1, idx2 = random.sample(range(len(new_sequence)), 2)
        new_sequence[idx1], new_sequence[idx2] = new_sequence[idx2], new_sequence[idx1]
        
        return new_sequence 

    def optimize_and_route(self, initial_temp=100.0, cooling_rate=0.95, min_temp=0.1):
        """The main Simulated Annealing algorithm."""
        current_sequence = self.nets.copy()
        current_energy, current_unrouted = self.evaluate_sequence(current_sequence)
        
        best_sequence = current_sequence.copy()
        best_energy = current_energy
        
        temp = initial_temp
        
        while temp > min_temp and best_energy >= 10000:
            neighbor_seq = self.get_neighbor(current_sequence)
            neighbor_energy, neighbor_unrouted = self.evaluate_sequence(neighbor_seq)
            
            delta_energy = neighbor_energy - current_energy
            
            if delta_energy < 0 or math.exp(-delta_energy / temp) > random.random():
                current_sequence = neighbor_seq
                current_energy = neighbor_energy
                
                if current_energy < best_energy:
                    best_sequence = current_sequence.copy()
                    best_energy = neighbor_energy
            
            temp *= cooling_rate 
            
        self.grid.clear_all_routes(self.nets)
             
        return best_sequence # Return the best order to the App