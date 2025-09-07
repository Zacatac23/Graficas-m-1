import struct
import numpy as np
import math

class EnvironmentMap(object):
    def __init__(self, filename=None):
        self.pixels = None
        self.width = 0
        self.height = 0
        
        if filename:
            self.loadFromBMP(filename)
        else:
            # Create a procedural sky environment map
            self.createProceduralSky()
    
    def loadFromBMP(self, filename):
        """Load environment map from BMP file"""
        try:
            with open(filename, "rb") as image:
                image.seek(10)
                headerSize = struct.unpack('=l', image.read(4))[0]
                image.seek(18)
                self.width = struct.unpack('=l', image.read(4))[0]
                self.height = struct.unpack('=l', image.read(4))[0]
                image.seek(headerSize)
                
                self.pixels = []
                for y in range(self.height):
                    pixelRow = []
                    for x in range(self.width):
                        b = ord(image.read(1)) / 255.0
                        g = ord(image.read(1)) / 255.0
                        r = ord(image.read(1)) / 255.0
                        pixelRow.append([r, g, b])
                    self.pixels.append(pixelRow)
        except FileNotFoundError:
            print(f"Environment map file {filename} not found. Creating procedural sky.")
            self.createProceduralSky()
    
    def createProceduralSky(self):
        """Create a simple procedural sky environment map"""
        self.width = 256
        self.height = 128
        self.pixels = []
        
        for y in range(self.height):
            pixelRow = []
            for x in range(self.width):
                # Create a gradient from blue (top) to light blue/white (horizon)
                v = y / (self.height - 1)  # 0 at top, 1 at bottom
                
                # Sky gradient
                if v < 0.7:  # Upper sky
                    # Deep blue to light blue
                    r = 0.4 + v * 0.3
                    g = 0.6 + v * 0.3
                    b = 0.8 + v * 0.2
                else:  # Horizon
                    # Light blue to white
                    horizon_factor = (v - 0.7) / 0.3
                    r = 0.7 + horizon_factor * 0.3
                    g = 0.9 + horizon_factor * 0.1
                    b = 1.0
                
                # Add some clouds (simple noise)
                cloud_x = x * 0.02
                cloud_y = y * 0.04
                cloud_noise = (math.sin(cloud_x) * math.cos(cloud_y) + 
                              math.sin(cloud_x * 2.3) * math.cos(cloud_y * 1.7)) * 0.5 + 0.5
                
                if cloud_noise > 0.6 and v > 0.3 and v < 0.8:
                    # Add white clouds
                    cloud_intensity = (cloud_noise - 0.6) * 2.5
                    r = min(1.0, r + cloud_intensity * 0.4)
                    g = min(1.0, g + cloud_intensity * 0.4)
                    b = min(1.0, b + cloud_intensity * 0.2)
                
                pixelRow.append([r, g, b])
            self.pixels.append(pixelRow)
    
    def getColorFromDirection(self, direction):
        """Get color from environment map based on 3D direction vector"""
        # Convert 3D direction to spherical coordinates
        dir_norm = direction / np.linalg.norm(direction)
        
        # Convert to spherical coordinates (latitude/longitude)
        phi = math.atan2(dir_norm[2], dir_norm[0])  # longitude
        theta = math.asin(max(-1, min(1, dir_norm[1])))  # latitude
        
        # Convert to UV coordinates
        u = (phi + math.pi) / (2 * math.pi)  # 0 to 1
        v = (theta + math.pi/2) / math.pi     # 0 to 1
        
        # Map to pixel coordinates
        x = int(u * (self.width - 1))
        y = int(v * (self.height - 1))
        
        # Clamp to bounds
        x = max(0, min(self.width - 1, x))
        y = max(0, min(self.height - 1, y))
        
        return self.pixels[y][x]