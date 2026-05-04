import pygame

class Renderer:
    def __init__(self, grid, cell_size=20):
        self.grid = grid
        self.cell_size = cell_size
        self.width = grid.width * cell_size
        self.height = grid.height * cell_size
        
        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("PCB Auto-Router - EDA Interface")
        
        pygame.font.init()
        self.font = pygame.font.SysFont('Consolas', 14, bold=True)
        # Base Colors
        self.BG_COLOR = (30, 30, 30)
        self.GRID_COLOR = (50, 50, 50)
        self.OBSTACLE_COLOR = (200, 50, 50)   # Static chips
        self.VISITED_COLOR = (70, 70, 90)     # Search space
        self.PAD_BORDER = (255, 255, 255)     # White border to make pads pop

    def draw(self, nets):
        """Now accepts a LIST of nets to draw them all simultaneously."""
        self.screen.fill(self.BG_COLOR)

        # 1. Draw Grid, Obstacles, and Visited Nodes
        for x in range(self.grid.width):
            for y in range(self.grid.height):
                node = self.grid.get_node(x, y)
                rect = pygame.Rect(x * self.cell_size, y * self.cell_size, self.cell_size, self.cell_size)
                
                if node.is_obstacle:
                    pygame.draw.rect(self.screen, self.OBSTACLE_COLOR, rect)
                elif node.visited:
                    pygame.draw.rect(self.screen, self.VISITED_COLOR, rect)
                    
                # Draw the faint grid lines
                pygame.draw.rect(self.screen, self.GRID_COLOR, rect, 1)

        # 2. Draw all Nets as Continuous Lines
        for net in nets:
            if net.path and len(net.path) > 1:
                # Calculate the center pixel of each node in the path
                points = []
                for node in net.path:
                    center_x = (node.x * self.cell_size) + (self.cell_size // 2)
                    center_y = (node.y * self.cell_size) + (self.cell_size // 2)
                    points.append((center_x, center_y))
                
                # Determine trace thickness (e.g., 35% of the cell size)
                trace_thickness = max(2, int(self.cell_size * 0.35))
                
                # Draw the continuous line connecting all centers
                pygame.draw.lines(self.screen, net.color, False, points, trace_thickness)
                
                # Draw circles at the joints to make the 45-degree bends look smooth
                for pt in points:
                    pygame.draw.circle(self.screen, net.color, pt, trace_thickness // 2)

            # 3. Draw Start and End Pads (kept as blocks)
            start_rect = pygame.Rect(net.start_node.x * self.cell_size, net.start_node.y * self.cell_size, self.cell_size, self.cell_size)
            end_rect = pygame.Rect(net.end_node.x * self.cell_size, net.end_node.y * self.cell_size, self.cell_size, self.cell_size)
            
            pygame.draw.rect(self.screen, net.color, start_rect)
            pygame.draw.rect(self.screen, net.color, end_rect)
            
            # Add a white border so the pads are visually distinct from the trace
            pygame.draw.rect(self.screen, self.PAD_BORDER, start_rect, 2)
            pygame.draw.rect(self.screen, self.PAD_BORDER, end_rect, 2)

    def draw_components(self, components):
        """Renders physical chips with silkscreen labels and Pin 1 indicators."""
        CHIP_BORDER_COLOR = (100, 100, 110)
        PIN_COLOR = (192, 192, 192)       
        PIN_1_COLOR = (255, 200, 50)      # Gold marker for orientation
        TEXT_COLOR = (220, 220, 220)      # White silkscreen
        
        for comp in components:
            # 1. Draw the component body
            body_rect = pygame.Rect(
                comp.start_x * self.cell_size, 
                comp.start_y * self.cell_size, 
                comp.width * self.cell_size, 
                comp.height * self.cell_size
            )
            pygame.draw.rect(self.screen, comp.body_color, body_rect)
            pygame.draw.rect(self.screen, CHIP_BORDER_COLOR, body_rect, 2)

            # 2. Draw the Silkscreen Reference Designator (U1, R1) in the center
            text_surface = self.font.render(comp.ref_des, True, TEXT_COLOR)
            text_rect = text_surface.get_rect(center=body_rect.center)
            self.screen.blit(text_surface, text_rect)

            # 3. Draw the pins
            for pin_name, node in comp.pins.items():
                pin_rect = pygame.Rect(
                    node.x * self.cell_size, 
                    node.y * self.cell_size, 
                    self.cell_size, 
                    self.cell_size
                )
                
                # Highlight Pin 1
                color = PIN_1_COLOR if pin_name == comp.pin_1_name else PIN_COLOR
                
                pygame.draw.rect(self.screen, color, pin_rect)
                pygame.draw.rect(self.screen, (0,0,0), pin_rect, 1)