# gl.py
import pygame

class Renderer(object):
    def __init__(self, screen):
        self.screen = screen
        _, _, self.width, self.height = self.screen.get_rect()
        self.currColor = [1, 1, 1]
        self.clearColor = [0, 0, 0]

    def glClearColor(self, r, g, b):
        r = min(1, max(0, r))
        g = min(1, max(0, g))
        b = min(1, max(0, b))
        self.clearColor = [r, g, b]

    def glColor(self, r, g, b):
        r = min(1, max(0, r))
        g = min(1, max(0, g))
        b = min(1, max(0, b))
        self.currColor = [r, g, b]

    def glClear(self):
        color = [int(i * 255) for i in self.clearColor]
        self.screen.fill(color)

    def glPoint(self, x, y, color=None):
        x = round(x)
        y = round(y)
        
        if (0 <= x < self.width and 0 <= y < self.height):
            point_color = color if color else self.currColor
            color_255 = [int(i * 255) for i in point_color]
            pygame_y = self.height - 1 - y
            self.screen.set_at((x, pygame_y), color_255)

    def glLine(self, x1, y1, x2, y2):
        """Draw a line using Bresenham's algorithm"""
        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
        
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        
        err = dx - dy
        
        while True:
            self.glPoint(x1, y1)
            
            if x1 == x2 and y1 == y2:
                break
                
            e2 = 2 * err
            
            if e2 > -dy:
                err -= dy
                x1 += sx
                
            if e2 < dx:
                err += dx
                y1 += sy

    def drawPolygon(self, vertices):
        """Draw polygon wireframe"""
        if len(vertices) < 3:
            return
        
        # Draw edges
        for i in range(len(vertices)):
            x1, y1 = vertices[i]
            x2, y2 = vertices[(i + 1) % len(vertices)]
            self.glLine(x1, y1, x2, y2)

    def fillPolygon(self, vertices):
        """Fill polygon using scanline algorithm"""
        if len(vertices) < 3:
            return
        
        # Find bounding box
        min_y = min(vertex[1] for vertex in vertices)
        max_y = max(vertex[1] for vertex in vertices)
        
        # For each scanline
        for y in range(min_y, max_y + 1):
            intersections = []
            
            # Find intersections with polygon edges
            for i in range(len(vertices)):
                x1, y1 = vertices[i]
                x2, y2 = vertices[(i + 1) % len(vertices)]
                
                # Check if scanline intersects this edge
                if y1 != y2:  # Skip horizontal edges
                    if (y1 <= y < y2) or (y2 <= y < y1):
                        # Calculate intersection x-coordinate
                        x_intersect = x1 + (y - y1) * (x2 - x1) / (y2 - y1)
                        intersections.append(x_intersect)
            
            # Sort intersections by x-coordinate
            intersections.sort()
            
            # Fill between pairs of intersections
            for i in range(0, len(intersections), 2):
                if i + 1 < len(intersections):
                    x_start = int(intersections[i])
                    x_end = int(intersections[i + 1])
                    
                    # Draw horizontal line
                    for x in range(x_start, x_end + 1):
                        self.glPoint(x, y)

    def fillPolygonAdvanced(self, vertices):
        """Advanced polygon fill with proper edge handling"""
        if len(vertices) < 3:
            return
        
        # Find bounding box
        min_y = min(vertex[1] for vertex in vertices)
        max_y = max(vertex[1] for vertex in vertices)
        
        # Create edge table
        edges = []
        for i in range(len(vertices)):
            x1, y1 = vertices[i]
            x2, y2 = vertices[(i + 1) % len(vertices)]
            
            if y1 != y2:  # Skip horizontal edges
                if y1 > y2:
                    x1, y1, x2, y2 = x2, y2, x1, y1
                
                # Calculate edge parameters
                dx = x2 - x1
                dy = y2 - y1
                slope = dx / dy if dy != 0 else 0
                
                edges.append({
                    'y_min': y1,
                    'y_max': y2,
                    'x_min': x1,
                    'slope': slope
                })
        
        # Scanline fill
        for y in range(min_y, max_y + 1):
            active_edges = []
            
            # Find active edges for this scanline
            for edge in edges:
                if edge['y_min'] <= y < edge['y_max']:
                    x_intersect = edge['x_min'] + (y - edge['y_min']) * edge['slope']
                    active_edges.append(x_intersect)
            
            # Sort intersections
            active_edges.sort()
            
            # Fill between pairs
            for i in range(0, len(active_edges), 2):
                if i + 1 < len(active_edges):
                    x_start = int(active_edges[i])
                    x_end = int(active_edges[i + 1])
                    
                    for x in range(x_start, x_end + 1):
                        self.glPoint(x, y)