import pygame

class Renderer:
    def __init__(self, grid, theme="dark", cell_size=20):
        self.grid = grid
        self.cell_size = cell_size
        self.show_visited = True  # <-- NEW: Toggle flag for visited nodes
        
        # Camera & Navigation Support (Ready for panning/zooming)
        self.camera_x = 0
        self.camera_y = 0
        self.zoom = 1.0 
        
        # Dynamic Theming Engine
        self.themes = {
            "dark": {
                "bg": (30, 30, 30), "grid": (50, 50, 50), 
                "obstacle": (200, 50, 50), "visited": (70, 70, 90),
                "chip_border": (100, 100, 110), "pin": (192, 192, 192),
                "pin_1": (255, 200, 50), "text": (220, 220, 220),
                "pad_border": (255, 255, 255),
                "trace": (220, 140, 70),
                "ratsnest": (200, 200, 50)  # <-- NEW: Yellow Ratsnest Color  # <-- NEW: Unified Copper Color
            },
            "light": {
                "bg": (240, 240, 240), "grid": (200, 200, 200), 
                "obstacle": (220, 80, 80), "visited": (200, 200, 255),
                "chip_border": (50, 50, 60), "pin": (100, 100, 100),
                "pin_1": (200, 150, 20), "text": (30, 30, 30),
                "pad_border": (0, 0, 0),
                "trace": (200, 100, 40),
                "ratsnest": (150, 150, 0)   # <-- NEW: Dark Yellow Ratsnest  # <-- NEW: Unified Copper Color
            }
        }
        self.colors = self.themes.get(theme, self.themes["dark"])
        
        # Coordinate Cache for extreme O(1) rendering performance
        self._trace_cache = {} 
        
        pygame.init()
        # Set a fixed resolution, letting the camera handle large grids
        self.screen = pygame.display.set_mode((1080, 720)) 
        pygame.display.set_caption("PCB Auto-Router - Professional EDA")
        
        pygame.font.init()
        self.font = pygame.font.SysFont('Consolas', 14, bold=True)

    def _world_to_screen(self, x, y):
        """Applies camera pan and zoom to grid coordinates."""
        screen_x = int((x * self.cell_size * self.zoom) + self.camera_x)
        screen_y = int((y * self.cell_size * self.zoom) + self.camera_y)
        scaled_size = int(self.cell_size * self.zoom)
        return screen_x, screen_y, scaled_size

    def _get_cached_points(self, net):
        """Calculates pixel locations ONCE and caches them."""
        if net not in self._trace_cache:
            points = []
            for node in net.path:
                cx, cy, size = self._world_to_screen(node.x, node.y)
                points.append((cx + size // 2, cy + size // 2))
            self._trace_cache[net] = points
        return self._trace_cache[net]

    def draw(self, completed_nets, all_nets):
        """Draws the grid, ratsnests, and completed traces."""
        self.screen.fill(self.colors["bg"])
        
        # 1. Draw Grid, Obstacles, and Visited Nodes
        for x in range(self.grid.width):
            for y in range(self.grid.height):
                node = self.grid.get_node(x, y)
                screen_x, screen_y, size = self._world_to_screen(x, y)
                
                if screen_x + size < 0 or screen_x > 1080 or screen_y + size < 0 or screen_y > 720:
                    continue
                    
                rect = pygame.Rect(screen_x, screen_y, size, size)
                
                if node.is_obstacle and not node.is_trace:
                    pygame.draw.rect(self.screen, self.colors["obstacle"], rect)
                elif node.visited and self.show_visited:
                    pygame.draw.rect(self.screen, self.colors["visited"], rect)
                    
                pygame.draw.rect(self.screen, self.colors["grid"], rect, 1)

        # 2. Draw Ratsnest (Unrouted Nets)
        for net in all_nets:
            # If the net hasn't been animated yet, OR if it failed to route entirely
            if net not in completed_nets or not net.path:
                sx, sy, size = self._world_to_screen(net.start_node.x, net.start_node.y)
                ex, ey, _ = self._world_to_screen(net.end_node.x, net.end_node.y)
                
                # Center the line inside the pad
                center_offset = size // 2
                start_pos = (sx + center_offset, sy + center_offset)
                end_pos = (ex + center_offset, ey + center_offset)
                
                # Draw a thin, 1-pixel line connecting the pads
                pygame.draw.line(self.screen, self.colors["ratsnest"], start_pos, end_pos, 1)

        # 3. Draw Cached Traces (Finished Routes)
        for net in completed_nets:
            if net.path and len(net.path) > 1:
                points = self._get_cached_points(net)
                trace_thickness = max(2, int(self.cell_size * self.zoom * 0.35))
                trace_color = self.colors["trace"]
                
                pygame.draw.lines(self.screen, trace_color, False, points, trace_thickness)
                for pt in points:
                    pygame.draw.circle(self.screen, trace_color, pt, trace_thickness // 2)
                    
            # Draw Pads 
            sx, sy, size = self._world_to_screen(net.start_node.x, net.start_node.y)
            ex, ey, _ = self._world_to_screen(net.end_node.x, net.end_node.y)
            
            pygame.draw.rect(self.screen, trace_color, (sx, sy, size, size))
            pygame.draw.rect(self.screen, trace_color, (ex, ey, size, size))
            pygame.draw.rect(self.screen, self.colors["pad_border"], (sx, sy, size, size), 2)
            pygame.draw.rect(self.screen, self.colors["pad_border"], (ex, ey, size, size), 2)

    def draw_components(self, components):
        for comp in components:
            screen_x, screen_y, cell_size = self._world_to_screen(comp.start_x, comp.start_y)
            width = int(comp.width * cell_size)
            height = int(comp.height * cell_size)
            
            body_rect = pygame.Rect(screen_x, screen_y, width, height)
            
            pygame.draw.rect(self.screen, comp.body_color, body_rect)
            pygame.draw.rect(self.screen, self.colors["chip_border"], body_rect, 2)
            
            text_surface = self.font.render(comp.ref_des, True, self.colors["text"])
            text_rect = text_surface.get_rect(center=body_rect.center)
            self.screen.blit(text_surface, text_rect)
            
            for pin_name, node in comp.pins.items():
                px, py, p_size = self._world_to_screen(node.x, node.y)
                pin_rect = pygame.Rect(px, py, p_size, p_size)
                color = self.colors["pin_1"] if pin_name == comp.pin_1_name else self.colors["pin"]
                
                pygame.draw.rect(self.screen, color, pin_rect)
                pygame.draw.rect(self.screen, (0,0,0), pin_rect, 1)

    def pan_camera(self, dx, dy):
        """Moves the camera and invalidates the trace cache."""
        self.camera_x += dx
        self.camera_y += dy
        self._trace_cache.clear() # Coordinates changed, must recalculate

    def zoom_camera(self, zoom_factor, mouse_x, mouse_y):
        """Zooms in/out while keeping the board centered on the mouse cursor."""
        # 1. Find where the mouse is in the 'world' right now
        world_x = (mouse_x - self.camera_x) / self.zoom
        world_y = (mouse_y - self.camera_y) / self.zoom
        
        # 2. Apply the zoom (Clamp between 0.2x and 5.0x to prevent breaking)
        self.zoom += zoom_factor
        self.zoom = max(0.2, min(self.zoom, 5.0))
        
        # 3. Adjust the camera so the world point stays perfectly under the mouse
        self.camera_x = mouse_x - (world_x * self.zoom)
        self.camera_y = mouse_y - (world_y * self.zoom)
        
        # 4. Clear cache because all pixel coordinates have changed
        self._trace_cache.clear()