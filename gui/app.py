import time
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
        # 1. Define and Load the Map
        map_filepath = "boards/level1_2_maze.json"  # <-- NEW: Data-Driven JSON Map Loader
        
        # Extract just the benchmark name (e.g., "test2_mega_mcu")
        self.benchmark_name = map_filepath.split('/')[-1].replace('.json', '')
        # 1. Load the Map using the new JSON Data-Driven Loader
        self.grid, self.manager, self.components = MapLoader.load_from_json(map_filepath)
        
        # 2. Setup the Strategy Pattern (Router + Optimizer)
        self.router = AStarRouter(self.grid)
        self.optimizer = GreedyOptimizer(self.grid, self.router)
        
        # Inject the optimizer into the manager
        self.manager.optimizer = self.optimizer
        
        # Setup the new high-performance renderer
        
        # ---------------------------------------------------------
        # 3. COMPUTE PHASE (Instant Background Calculation)
        # ---------------------------------------------------------
        self.logger = MetricsLogger()
        
        print("Optimizing sequence to prevent deadlocks...")
        # Start the global timer to include Optimizer time!
        global_start_time = time.perf_counter() 
        
        self.manager.prepare_queue()

        print("Calculating final board routing...")
        
        # Track global stats
        successful_routes = 0
        failed_routes = 0
        total_wirelength = 0
        
        # Dynamically get algorithm names
        router_name = self.router.__class__.__name__
        optimizer_name = self.optimizer.__class__.__name__ if self.optimizer else "None"
        
        for net in self.manager.nets:
            self.logger.start_timer()
            
            # Route the net
            success = self.router.route(net)
            
            elapsed_time = self.logger.stop_timer()
            
            if success:
                self.grid.lock_path(net)
                successful_routes += 1
                total_wirelength += len(net.path)
            else:
                failed_routes += 1
                
            # Log the O(1) performance metrics PER NET
            net_id = getattr(net, 'id', f"Net_Fallback")
            self.logger.log_net_metrics(router_name, self.grid, net, net_id, elapsed_time)
            
            # Clear the mathematical search space for the next net's calculation
            self.grid.reset_search_states()
        
        # Stop global timer
        global_time_ms = (time.perf_counter() - global_start_time) * 1000
        
        # Log the global summary!
        self.logger.log_run_summary(
            self.benchmark_name,    # <-- Pass the benchmark name here!
            self.grid, 
            router_name, 
            optimizer_name, 
            len(self.manager.nets), 
            successful_routes, 
            failed_routes, 
            total_wirelength, 
            global_time_ms
        )

        print("Routing complete! Launching GUI Playback...")
        
        # ---------------------------------------------------------
        # 4. PLAYBACK PHASE SETUP
        # ---------------------------------------------------------
        self.renderer = Renderer(self.grid, cell_size=20, theme="dark")


        self.running = True
        self.clock = pygame.time.Clock()
        self.steps_per_frame = 100  # Adjusted for smoother animation viewing
        
        self.playback_net_index = 0
        self.playback_history_index = 0
        self.animating_search = True

        # Add these two variables to the bottom of __init__ to track panning
        self.dragging = False
        self.last_mouse_pos = (0, 0)



    def process_events(self):
        """Handles PyGame inputs for closing the app and camera navigation."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                
            # --- NEW: Camera Pan (Click and Drag) ---
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Trigger pan on Left click (1), Middle click (2), or Right click (3)
                if event.button in (1, 2, 3): 
                    self.dragging = True
                    self.last_mouse_pos = event.pos
                    
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button in (1, 2, 3):
                    self.dragging = False
                    
            elif event.type == pygame.MOUSEMOTION:
                if self.dragging:
                    dx = event.pos[0] - self.last_mouse_pos[0]
                    dy = event.pos[1] - self.last_mouse_pos[1]
                    self.renderer.pan_camera(dx, dy)
                    self.last_mouse_pos = event.pos
                    
            # --- NEW: Camera Zoom (Mouse Wheel) ---
            elif event.type == pygame.MOUSEWHEEL:
                # event.y is positive for scrolling up (zoom in), negative for down
                mouse_x, mouse_y = pygame.mouse.get_pos()
                zoom_speed = 0.15 # Adjust this to make zooming faster or slower
                self.renderer.zoom_camera(event.y * zoom_speed, mouse_x, mouse_y)

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
        completed_nets = self.manager.nets[:self.playback_net_index]
        
        # Pass BOTH completed_nets and ALL nets to the renderer so it can draw Ratsnests
        self.renderer.draw(completed_nets, self.manager.nets)
        
        if hasattr(self, 'components') and self.components:
            self.renderer.draw_components(self.components)
            
        pygame.display.flip()

    def run(self):
        while self.running:
            self.process_events()
            self.update()
            self.render()
            self.clock.tick(0)
            
        pygame.quit()
        sys.exit()