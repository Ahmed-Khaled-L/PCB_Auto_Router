# core/optimizers/sa_optimizer.py
import math
import random
from core.interfaces.base_optimizer import BaseOptimizer

class SimulatedAnnealingOptimizer(BaseOptimizer):
    
    def evaluate_sequence(self, net_sequence):
        """Runs the injected router on a sequence of nets and returns the cost."""
        self.grid.clear_all_routes(net_sequence)
        
        unrouted_count = 0
        total_wirelength = 0
        
        for net in net_sequence:
            # HUGE CLEANUP: The _route_sync() wrapper is gone.
            # We just fire the synchronous route method of whatever router was injected.
            success = self.router.route(net)
            
            if not success:
                unrouted_count += 1
            else:
                total_wirelength += len(net.path)
                self.grid.lock_path(net)
                
        energy = (unrouted_count * 10000) + total_wirelength
        return energy, unrouted_count

    def get_neighbor(self, current_sequence):
        new_sequence = current_sequence.copy()
        idx1, idx2 = random.sample(range(len(new_sequence)), 2)
        new_sequence[idx1], new_sequence[idx2] = new_sequence[idx2], new_sequence[idx1]
        return new_sequence

    def optimize(self, nets, initial_temp=100.0, cooling_rate=0.95, min_temp=0.1):
        """The core Simulated Annealing algorithm."""
        print(f"[OPTIMIZER] Running Simulated Annealing with {self.router.__class__.__name__}...")
        
        current_sequence = nets.copy()
        current_energy, _ = self.evaluate_sequence(current_sequence)
        
        best_sequence = current_sequence.copy()
        best_energy = current_energy
        temp = initial_temp
        
        while temp > min_temp and best_energy >= 10000:
            neighbor_seq = self.get_neighbor(current_sequence)
            neighbor_energy, _ = self.evaluate_sequence(neighbor_seq)
            
            delta_energy = neighbor_energy - current_energy
            
            if delta_energy < 0 or math.exp(-delta_energy / temp) > random.random():
                current_sequence = neighbor_seq
                current_energy = neighbor_energy
                
                if current_energy < best_energy:
                    best_sequence = current_sequence.copy()
                    best_energy = neighbor_energy
                    
            temp *= cooling_rate
            
        # Clean the grid up so the GUI can start fresh with the best sequence
        self.grid.clear_all_routes(nets)
        return best_sequence