# main.py
import pygame
from gl import Renderer

# Initialize pygame
pygame.init()

width = int(1900 / 2)
height = int(1080 / 2)

screen = pygame.display.set_mode((width, height), pygame.SCALED)
pygame.display.set_caption("Polygon Fill Algorithm")
clock = pygame.time.Clock()

rend = Renderer(screen)
rend.glClearColor(0.1, 0.1, 0.1)  # Dark gray background

# Define polygons
polygon1 = [(165, 380), (185, 360), (180, 330), (207, 345), (233, 330), (230, 360), (250, 380), (220, 385), (205, 410), (193, 383)]
polygon2 = [(321, 335), (288, 286), (339, 251), (374, 302)]
polygon3 = [(377, 249), (411, 197), (436, 249)]
polygon4 = [(413, 177), (448, 159), (502, 88), (553, 53), (535, 36), (676, 37), (660, 52), (750, 145), (761, 179), (672, 192), (659, 214), (615, 214), (632, 230), (580, 230), (597, 215), (552, 214), (517, 144), (466, 180)]
polygon5 = [(682, 175), (708, 120), (735, 148), (739, 170)]  # Hole in polygon4

show_wireframe = True
show_filled = True

print("Controls:")
print("W - Toggle wireframe")
print("F - Toggle fill")

isRunning = True
while isRunning:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            isRunning = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                show_wireframe = not show_wireframe
                print(f"Wireframe: {'ON' if show_wireframe else 'OFF'}")
            elif event.key == pygame.K_f:
                show_filled = not show_filled
                print(f"Fill: {'ON' if show_filled else 'OFF'}")

    rend.glClear()
    
    if show_filled:
        
        rend.glColor(1, 0, 0)  
        rend.fillPolygon(polygon1)
        
        rend.glColor(1, 0, 0)  
        rend.fillPolygon(polygon2)
        
        rend.glColor(1, 0, 0)  
        rend.fillPolygon(polygon3)
        
        rend.glColor(1, 0, 0)  
        rend.fillPolygon(polygon4)
        
        
        rend.glColor(0.1, 0.1, 0.1)  
        rend.fillPolygon(polygon5)
    
    if show_wireframe:
        # Draw wireframes in white
        rend.glColor(1, 1, 1)
        rend.drawPolygon(polygon1)
        rend.drawPolygon(polygon2)
        rend.drawPolygon(polygon3)
        rend.drawPolygon(polygon4)
        rend.drawPolygon(polygon5)
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()