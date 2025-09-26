import pygame
import sys

# Import modules - using your existing structure
import gl
from BMP_Writer import GenerateBMP
from figures import Sphere, Plane, Disk, Triangle, Cube  # Updated figures with new shapes
from lights import AmbientLight, DirectionalLight
from material import Material

# Get Renderer class
Renderer = gl.Renderer

width = 800
height = 600

print("Setting up Room Scene Ray Tracer...")
pygame.init()
screen = pygame.display.set_mode((width, height), pygame.HIDDEN)

rend = Renderer(screen)

# Set camera position to be clearly inside the room
rend.camera.translation = [0, 0, 2]

# Black background so the bright white room stands out
rend.glClearColor(0.0, 0.0, 0.0)

print("Creating materials for the room...")

# Simple materials WITHOUT advanced reflections to avoid recursion
white_wall = Material(
    diffuse=[1.0, 1.0, 1.0],     # Pure white diffuse
    specular=[0.3, 0.3, 0.3],    # Some specular
    shininess=20,
    ambient=[0.7, 0.7, 0.7],     # High ambient
    reflectivity=0.1,            # Small reflectivity using the fixed system
    transparency=0.0
)

# Bright white floor - Small reflections
floor_material = Material(
    diffuse=[0.95, 0.95, 0.95], 
    specular=[0.4, 0.4, 0.4], 
    shininess=30,
    ambient=[0.6, 0.6, 0.6],
    reflectivity=0.05,           # Very small reflectivity
    transparency=0.0
)

# Bright ceiling - NO reflections (lights come from here)
ceiling_material = Material(
    diffuse=[1.0, 1.0, 1.0], 
    specular=[0.2, 0.2, 0.2], 
    shininess=10,
    ambient=[0.8, 0.8, 0.8],    # Very bright
    reflectivity=0.0,           # NO reflectivity for ceiling
    transparency=0.0
)

# Ceiling material that glows like fluorescent panels
ceiling_material = Material(
    diffuse=[1.0, 1.0, 1.0], 
    specular=[0.1, 0.1, 0.1], 
    shininess=5,
    ambient=[0.95, 0.95, 0.95]  # Almost pure ambient - like it's glowing
)

# Materials for objects - WITH safe reflectivity levels
red_cube = Material(
    diffuse=[0.8, 0.2, 0.2], 
    specular=[0.3, 0.3, 0.3], 
    shininess=50,
    ambient=[0.1, 0.02, 0.02],
    reflectivity=0.0,          # No reflectivity for cubes to keep simple
    transparency=0.0
)

blue_cube = Material(
    diffuse=[0.2, 0.2, 0.8], 
    specular=[0.3, 0.3, 0.3], 
    shininess=50,
    ambient=[0.02, 0.02, 0.1],
    reflectivity=0.0,          # No reflectivity for cubes
    transparency=0.0
)

green_triangle = Material(
    diffuse=[0.2, 0.8, 0.2], 
    specular=[0.4, 0.4, 0.4], 
    shininess=60,
    ambient=[0.02, 0.1, 0.02],
    reflectivity=0.0,          # No reflectivity for triangle
    transparency=0.0
)

# Metallic disk with MODERATE reflectivity using the fixed system
metallic_disk = Material(
    diffuse=[0.1, 0.1, 0.1],   # Dark base color
    specular=[0.9, 0.9, 0.9],  # High specular for metallic look
    shininess=200,
    ambient=[0.02, 0.02, 0.02],
    reflectivity=0.6,          # Moderate reflectivity - SAFE with new system
    transparency=0.0
)

print("Building the room with 5+ planes...")

# Create the room (6 planes total - more than the required 5)
room_size = 10

# Floor
rend.scene.append(Plane(
    position=[0, -3, 0], 
    normal=[0, 1, 0], 
    material=floor_material
))

# Ceiling  
rend.scene.append(Plane(
    position=[0, 3, 0], 
    normal=[0, -1, 0], 
    material=ceiling_material
))

# Back wall
rend.scene.append(Plane(
    position=[0, 0, -8], 
    normal=[0, 0, 1], 
    material=white_wall
))

# Left wall
rend.scene.append(Plane(
    position=[-5, 0, 0], 
    normal=[1, 0, 0], 
    material=white_wall
))

# Right wall
rend.scene.append(Plane(
    position=[5, 0, 0], 
    normal=[-1, 0, 0], 
    material=white_wall
))

# Front wall (behind camera, but visible in reflections)
rend.scene.append(Plane(
    position=[0, 0, 8], 
    normal=[0, 0, -1], 
    material=white_wall
))

print("Adding objects to the room...")

# Add two cubes as required
rend.scene.append(Cube(
    position=[-2, -1.5, -3], 
    size=1.0, 
    material=red_cube
))

rend.scene.append(Cube(
    position=[2, -1.5, -5], 
    size=1.2, 
    material=blue_cube
))

# Add a triangle as required
rend.scene.append(Triangle(
    v0=[-1, -2, -2],
    v1=[0, 1, -2], 
    v2=[1, -2, -2],
    material=green_triangle
))

# Add a disk as required - positioned on the floor to reflect other objects
rend.scene.append(Disk(
    position=[0, -2.95, -3.5],  # Almost touching the floor
    normal=[0, 1, 0],  # Completely horizontal to act as mirror
    radius=1.5,  # Larger radius to catch more reflections
    material=metallic_disk
))

# Add some extra spheres for visual interest - WITH small reflections
glossy_sphere = Material(
    diffuse=[0.7, 0.5, 0.8], 
    specular=[0.5, 0.5, 0.5], 
    shininess=80,
    ambient=[0.1, 0.05, 0.1],
    reflectivity=0.2,          # Small reflectivity for glossy look
    transparency=0.0
)

rend.scene.append(Sphere(
    position=[3, 0, -3], 
    radius=0.6, 
    material=glossy_sphere
))

print("Setting up MAXIMUM interior lighting...")

# EXTREMELY strong ambient light - like being inside a light box
rend.lights.append(AmbientLight(
    intensity=1.0,  # Maximum ambient light
    color=[1.0, 1.0, 1.0]
))

# Very strong ceiling lights pointing down
rend.lights.append(DirectionalLight(
    direction=[0, -1, 0],  # Straight down
    intensity=1.5,  # Much stronger
    color=[1.0, 1.0, 1.0]
))

rend.lights.append(DirectionalLight(
    direction=[0.3, -1, 0.2], 
    intensity=1.0, 
    color=[1.0, 1.0, 1.0]
))

rend.lights.append(DirectionalLight(
    direction=[-0.3, -1, -0.2], 
    intensity=1.0, 
    color=[1.0, 1.0, 1.0]
))

# Add some side lighting to fill shadows
rend.lights.append(DirectionalLight(
    direction=[1, -0.5, 0], 
    intensity=0.8, 
    color=[1.0, 1.0, 1.0]
))

rend.lights.append(DirectionalLight(
    direction=[-1, -0.5, 0], 
    intensity=0.8, 
    color=[1.0, 1.0, 1.0]
))

print(f"\nRoom setup complete!")
print(f"Resolution: {width}x{height}")
print(f"Objects in scene:")
print(f"  - 6 planes (room walls, floor, ceiling)")
print(f"  - 2 cubes (red and blue)")
print(f"  - 1 triangle (green)")
print(f"  - 1 disk (metallic)")
print(f"  - 1 sphere (glossy purple)")
print(f"  - {len(rend.lights)} lights")

print("\nStarting room render with safe reflections...")

# Initialize reflection system properly
rend.reflection_depth = 0

# Use your existing render method
rend.glRender()

# Generate output
output_filename = "room_scene.bmp"
print(f"\nGenerating {output_filename}...")
GenerateBMP(output_filename, width, height, 3, rend.frameBuffer)

print(f"\nRoom scene ray tracer complete!")
print(f"Image saved as '{output_filename}'")
print("\nScene contains all required elements:")
print("  ✓ Minimum 5 planes (6 total - full room)")
print("  ✓ 2 cubes in different positions")  
print("  ✓ 1 triangle")
print("  ✓ 1 disk")
print("  ✓ Custom materials for all objects")
print("  ✓ Proper lighting setup")

pygame.quit()