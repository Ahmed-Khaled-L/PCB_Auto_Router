import pygame
import sys
from core.net import Net # Needed for the dummy net in metrics
from core.astar_router import AStarRouter
from gui.renderer import Renderer
from utils.map_loader import MapLoader
from utils.metrics_logger import MetricsLogger

from maps.map1 import load_map

# Import your new SA Manager
from core.SimulatedAnnealingManager import SimulatedAnnealingManager

class App:
    def __init__(self):
        # 1. Load the original MultiNetManager (which HAS get_next_net)
        # self.grid, self.manager, self.components = MapLoader.load_deadlock_test()
        self.grid, self.manager, self.components = MapLoader.load_pocket_trap_test()
        
        self.router = AStarRouter(self.grid)
        self.current_net = None
        self.renderer = Renderer(self.grid, cell_size=20) 
        self.running = True
        self.clock = pygame.time.Clock()
        self.steps_per_frame = 10
        
        self.logger = MetricsLogger()
        self.total_compute_time = 0.0
        self.metrics_saved = False
        
 



        

        self.manager.sort_nets_shortest_first() 
        
       
        

        # sa_manager = SimulatedAnnealingManager(self.grid, self.manager.nets, self.router)
        # self.manager.nets = sa_manager.optimize_and_route(initial_temp=100.0, cooling_rate=0.90)
        # # self.manager.nets = best_sequence
        # self.manager.current_index = 0 

        
        self._load_next_net()

    def _load_next_net(self):
        """Pulls the next net from the queue and resets the search canvas."""
        self.current_net = self.manager.get_next_net()
        
        if self.current_net:
            print(f"--- Starting Route for Net from ({self.current_net.start_node.x}, {self.current_net.start_node.y}) ---")
            self.router.initialize_search(self.current_net)
        else:
            print("--- All nets processed ---")

    def process_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def update(self):
        # 3. Route processing with performance tracking
        if self.current_net and not self.router.is_finished:
            self.logger.start_timer()
            
            for _ in range(self.steps_per_frame):
                result = self.router.step()
                
                # NET ROUTED SUCCESSFULLY
                if result is True:
                    print("Path found! Locking trace into grid.")
                    self.grid.lock_path(self.current_net)    
                    self.grid.reset_search_states()          
                    self._load_next_net()                    
                    break 
                    
                # DEADLOCK DETECTED
                elif result is False:
                    print("DEADLOCK DETECTED! Net blocked by existing traces.")
                    self.grid.reset_search_states()
                    self._load_next_net()
                    break

            elapsed = self.logger.stop_timer()
            self.total_compute_time += elapsed

        # 4. Save metrics once all routing is finished
        elif not self.current_net and not self.metrics_saved:
            # Passing a dummy net just to log total board time and visited nodes
            dummy_net = Net(self.grid.get_node(0,0), self.grid.get_node(0,0))
            self.logger.log_metrics("AStar_MultiNet", self.grid, dummy_net, self.total_compute_time)
            self.metrics_saved = True

    def render(self):
        # 5. Corrected single render loop
        self.renderer.draw(self.manager.get_all_nets())
        
        if hasattr(self, 'components') and self.components:
            self.renderer.draw_components(self.components)
            
        pygame.display.flip() # Push the final frame to the monitor

    def run(self):
        while self.running:
            self.process_events()
            self.update()
            self.render()
            self.clock.tick(60)
            
        pygame.quit()
        sys.exit()