import pygame
import sys
from core.astar_router import AStarRouter
from gui.renderer import Renderer
from utils.map_loader import MapLoader
from utils.metrics_logger import MetricsLogger

class App:
    def __init__(self):
        # 1. Load the Map (using pocket_trap for testing)
        self.grid, self.manager, self.components = MapLoader.load_pocket_trap_test()
        
        # 2. Setup Router
        self.router = AStarRouter(self.grid)
        self.renderer = Renderer(self.grid, cell_size=20)
        
        # ---------------------------------------------------------
        # 3. COMPUTE PHASE (Instant Background Calculation)
        # ---------------------------------------------------------
        print("Calculating entire board routing in the background...")
        self.logger = MetricsLogger()
        self.logger.start_timer()
        
        for net in self.manager.nets:
            success = self.router.route(net)
            if success:
                self.grid.lock_path(net)
            # Clear the mathematical search space for the next net's calculation
            self.grid.reset_search_states() 
            
        total_time = self.logger.stop_timer()
        print(f"Routing complete in {total_time:.4f} ms! Launching GUI Playback...")
        
        # ---------------------------------------------------------
        # 4. PLAYBACK PHASE SETUP
        # ---------------------------------------------------------
        self.running = True
        self.clock = pygame.time.Clock()
        self.steps_per_frame = 15  # Adjust this to change animation speed
        
        # Playback tracking variables
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