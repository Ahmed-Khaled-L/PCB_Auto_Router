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
        map_filepath = "boards/level99_titan_mcu.json"  # <-- NEW: Data-Driven JSON Map Loader
        
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
        self._save_run_summary(
            f"run_summaries/{self.benchmark_name}_summary.txt",  # Save summary with benchmark-specific filename
            self.benchmark_name,
            self.grid,
            router_name,
            optimizer_name,
            len(self.manager.nets),
            successful_routes,
            failed_routes,
            total_wirelength,
            global_time_ms
        )
        
        # ---------------------------------------------------------
        # 4. PLAYBACK PHASE SETUP
        # ---------------------------------------------------------
        self.renderer = Renderer(self.grid, cell_size=20, theme="dark")


        self.running = True
        self.clock = pygame.time.Clock()
        self.steps_per_frame = 5  # Adjusted for smoother animation viewing
        
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
            elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_c:
                        print("[APP] Manual center triggered.")
                        self.renderer.center_view()
                
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

            # --- NEW: Toggle Visited Nodes ('V' Key) ---
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_v:
                    self.renderer.show_visited = not self.renderer.show_visited
                    print(f"Search space visibility: {self.renderer.show_visited}")

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

            if self.playback_net_index >= len(self.manager.nets):
                for completed_net in self.manager.nets:
                    for node in completed_net.search_history:
                        node.visited = True
                print("GUI Playback Complete! Press 'V' to toggle the global search space view.")

    def render(self):
        completed_nets = self.manager.nets[:self.playback_net_index]
        
        # Pass BOTH completed_nets and ALL nets to the renderer so it can draw Ratsnests
        self.renderer.draw(completed_nets, self.manager.nets)
        
        if hasattr(self, 'components') and self.components:
            self.renderer.draw_components(self.components)
            
        pygame.display.flip()


    def _save_run_summary(self,filepath, benchmark_name, grid, router_name, optimizer_name, total_nets, routed, failed, total_length, total_time_ms):
        """Dumps the terminal summary to a text file."""        
        summary_text = (
            f"Benchmark: {benchmark_name}\n"
            f"Router:    {router_name}\n"
            f"Optimizer: {optimizer_name}\n"
            f"Board:     {grid.width}x{grid.height} cells\n"
            f"Nets:      {routed}/{total_nets} Successfully Routed ({failed} Deadlocks)\n"
            f"Length:    {total_length} Total Grid Units (Copper Wirelength)\n"
            f"Time:      {total_time_ms:.2f} ms (Including Optimization)\n"
            f"\n\n"
        )
        
        with open(filepath, 'a') as f:
            f.write(summary_text)
            
        print(f"[APP] Run summary saved to: {filepath}")

    def run(self):
        while self.running:
            self.process_events()
            self.update()
            self.render()
            self.clock.tick(60)
        pygame.quit()
        sys.exit()