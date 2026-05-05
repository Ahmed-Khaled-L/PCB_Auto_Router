import pygame
import sys
from core.astar_router import AStarRouter
from core.bfs_router import BFSRouter
from core.sa_optimizer import SimulatedAnnealingOptimizer # Import the Optimizer
from core.greedy_optimizer import GreedyOptimizer # Import the Optimizer
from gui.renderer import Renderer
from utils.map_loader import MapLoader
from utils.metrics_logger import MetricsLogger

class App:
    def __init__(self):
        # 1. Load the Map using the new JSON Data-Driven Loader
        self.grid, self.manager, self.components = MapLoader.load_from_json("boards/test1_weaver.json")
        
        # 2. Setup the Strategy Pattern (Router + Optimizer)
        self.router = AStarRouter(self.grid)
        self.optimizer = SimulatedAnnealingOptimizer(self.grid, self.router)
        
        # Inject the optimizer into the manager
        self.manager.optimizer = self.optimizer
        
        # Setup the new high-performance renderer
        self.renderer = Renderer(self.grid, cell_size=20, theme="dark")
        
        # ---------------------------------------------------------
        # 3. COMPUTE PHASE (Instant Background Calculation)
        # ---------------------------------------------------------
        print("Optimizing sequence to prevent deadlocks...")
        # This triggers the SA Optimizer you built!
        self.manager.prepare_queue() 

        print("Calculating final board routing...")
        self.logger = MetricsLogger()
        
        for net in self.manager.nets:
            self.logger.start_timer()
            
            # Route the net
            success = self.router.route(net)
            
            elapsed_time = self.logger.stop_timer()
            
            if success:
                self.grid.lock_path(net)
                
            # Log the O(1) performance metrics PER NET
            net_id = getattr(net, 'id', f"Net_Fallback") 
            self.logger.log_net_metrics("AStar_SA", self.grid, net, net_id, elapsed_time)
                
            # Clear the mathematical search space for the next net's calculation
            self.grid.reset_search_states() 
            
        print("Routing complete! Launching GUI Playback...")
        
        # ---------------------------------------------------------
        # 4. PLAYBACK PHASE SETUP
        # ---------------------------------------------------------
        self.running = True
        self.clock = pygame.time.Clock()
        self.steps_per_frame = 5  # Adjusted for smoother animation viewing
        
        self.playback_net_index = 0
        self.playback_history_index = 0
        self.animating_search = True

    def process_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def update(self):
        """Plays back the 'tape' recorded in net.search_history frame by frame."""
        # Stop updating if all nets are fully animated
        if self.playback_net_index >= len(self.manager.nets):
            return 

        current_net = self.manager.nets[self.playback_net_index]

        # Stage A: Animate the purple search space expanding
        if self.animating_search:
            for _ in range(self.steps_per_frame): 
                if self.playback_history_index < len(current_net.search_history):
                    # Pull the next node from the history tape and tell the grid to render it
                    node = current_net.search_history[self.playback_history_index]
                    node.visited = True 
                    self.playback_history_index += 1
                else:
                    # History exhausted! Move to Stage B.
                    self.animating_search = False
                    break
                    
        # Stage B: Lock in the solid path and cue up the next net
        else:
            self.playback_net_index += 1
            self.playback_history_index = 0
            self.animating_search = True
            
            # Wipe the purple visited cells off the screen so the next net starts fresh
            self.grid.reset_search_states()

    def render(self):
        # CRITICAL TRICK: We only pass nets to the renderer that have FINISHED animating.
        # This prevents the renderer from drawing traces before the search animation finishes.
        completed_nets = self.manager.nets[:self.playback_net_index]
        self.renderer.draw(completed_nets)
        
        if hasattr(self, 'components') and self.components:
            self.renderer.draw_components(self.components)
            
        pygame.display.flip()

    def run(self):
        while self.running:
            self.process_events()
            self.update()
            self.render()
            self.clock.tick(60)
            
        pygame.quit()
        sys.exit()