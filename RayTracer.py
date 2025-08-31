import pygame
from gl import *
from BMP_Writer import GenerateBMP
from figures import *
from lights import *
from material import Material
import math

width = 512
height = 512

# Inicializar pygame en modo headless (sin ventana visible)
pygame.init()
screen = pygame.display.set_mode((width, height), pygame.HIDDEN)

rend = Renderer(screen)

# Define various materials with different colors
red_brick = Material(diffuse=[0.8, 0.2, 0.2])
green_grass = Material(diffuse=[0.2, 0.8, 0.2])
blue_water = Material(diffuse=[0.2, 0.2, 0.8])
yellow_sun = Material(diffuse=[0.9, 0.9, 0.2])
purple_grape = Material(diffuse=[0.6, 0.2, 0.8])
orange_fire = Material(diffuse=[1.0, 0.5, 0.1])
pink_flower = Material(diffuse=[0.9, 0.4, 0.7])
cyan_ice = Material(diffuse=[0.2, 0.8, 0.8])
white_cloud = Material(diffuse=[0.9, 0.9, 0.9])
dark_shadow = Material(diffuse=[0.3, 0.3, 0.3])

# Create a flower-like figure composed of spheres
print("Setting up scene...")

# Center sphere (flower center)
rend.scene.append(Sphere(position=[0, 0, -8], radius=0.8, material=yellow_sun))

# Petals around the center (6 petals in a circle)
petal_radius = 0.6
center_distance = 1.8

for i in range(6):
    angle = i * (2 * math.pi / 6)  # 60 degrees apart
    x = center_distance * math.cos(angle)
    y = center_distance * math.sin(angle)
    
    # Alternate colors for petals
    if i % 2 == 0:
        material = pink_flower
    else:
        material = purple_grape
    
    rend.scene.append(Sphere(position=[x, y, -8], radius=petal_radius, material=material))

# Add some smaller decorative spheres
# Inner ring
for i in range(3):
    angle = i * (2 * math.pi / 3) + math.pi/6  # Offset by 30 degrees
    x = 0.9 * math.cos(angle)
    y = 0.9 * math.sin(angle)
    rend.scene.append(Sphere(position=[x, y, -7.5], radius=0.2, material=orange_fire))

# Background spheres for depth
rend.scene.append(Sphere(position=[-3, -2, -12], radius=1.0, material=blue_water))
rend.scene.append(Sphere(position=[3, 2, -12], radius=0.8, material=green_grass))
rend.scene.append(Sphere(position=[-2, 3, -10], radius=0.5, material=cyan_ice))
rend.scene.append(Sphere(position=[2, -3, -10], radius=0.7, material=red_brick))

# Ground plane simulation with small spheres
for i in range(-2, 3):
    for j in range(-1, 1):
        rend.scene.append(Sphere(position=[i*1.5, -4 + j*0.3, -15], radius=0.3, material=dark_shadow))

# Lighting setup
rend.lights.append(AmbientLight(intensity=0.2))
rend.lights.append(DirectionalLight(direction=[-1, -1, -1], intensity=0.8))

print(f"Scene setup complete! {len(rend.scene)} spheres, {len(rend.lights)} lights")
print("Starting render...")
print("This may take a few minutes depending on your computer...")

# Render the scene
rend.glRender()

# Generate BMP files
print("Render complete! Generating image files...")
GenerateBMP("flower_raytracer_final.bmp", width, height, 3, rend.frameBuffer)

print("✅ Image saved as 'flower_raytracer_final.bmp'")
print("✅ Ray tracing complete!")

# Close pygame without showing window
pygame.quit()