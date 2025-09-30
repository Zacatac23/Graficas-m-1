import pygame
import sys

# Import modules
import gl
from BMP_Writer import GenerateBMP
from figures import  Plane,  Triangle, Cube, Cylinder, Ellipsoid
from lights import AmbientLight, DirectionalLight
from material import Material

# Get Renderer class
Renderer = gl.Renderer

width = 800
height = 600

print("Setting up Ray Tracer - LABORATORIO COMPLETO")
print("3 Cilindros + 3 Elipsoides + Estrella de triángulos + Cubo central")
pygame.init()
screen = pygame.display.set_mode((width, height), pygame.HIDDEN)

rend = Renderer(screen)
rend.camera.translation = [0, 1, 12]
rend.glClearColor(0.15, 0.2, 0.35)  # Fondo azul oscuro

print("Creating materials...")

# ========== MATERIALES PARA CILINDROS ==========
cylinder_opaque = Material(
    diffuse=[0.9, 0.4, 0.1], 
    specular=[0.5, 0.5, 0.5], 
    shininess=50,
    ambient=[0.1, 0.04, 0.01],
    reflectivity=0.0,
    transparency=0.0
)

cylinder_reflective = Material(
    diffuse=[0.3, 0.3, 0.3], 
    specular=[0.9, 0.9, 0.9], 
    shininess=150,
    ambient=[0.05, 0.05, 0.05],
    reflectivity=0.7,
    transparency=0.0
)

cylinder_transparent = Material(
    diffuse=[0.1, 0.3, 0.6], 
    specular=[0.9, 0.9, 0.9], 
    shininess=200,
    ambient=[0.02, 0.05, 0.1],
    reflectivity=0.1,
    transparency=0.8,
    refractive_index=1.5
)

# ========== MATERIALES PARA ELIPSOIDES ==========
ellipsoid_opaque = Material(
    diffuse=[0.2, 0.8, 0.3], 
    specular=[0.4, 0.4, 0.4], 
    shininess=60,
    ambient=[0.02, 0.08, 0.03],
    reflectivity=0.0,
    transparency=0.0
)

ellipsoid_reflective = Material(
    diffuse=[0.8, 0.6, 0.2], 
    specular=[1.0, 0.9, 0.7], 
    shininess=180,
    ambient=[0.1, 0.08, 0.03],
    reflectivity=0.6,
    transparency=0.0
)

ellipsoid_transparent = Material(
    diffuse=[0.9, 0.2, 0.5], 
    specular=[1.0, 1.0, 1.0], 
    shininess=220,
    ambient=[0.09, 0.02, 0.05],
    reflectivity=0.15,
    transparency=0.75,
    refractive_index=1.4
)

# Material para estrella (triángulos)
star_material = Material(
    diffuse=[1.0, 0.9, 0.2], 
    specular=[1.0, 1.0, 0.8], 
    shininess=100,
    ambient=[0.2, 0.18, 0.04],
    reflectivity=0.3
)

# Material para cubo central
cube_material = Material(
    diffuse=[0.9, 0.1, 0.1], 
    specular=[0.7, 0.7, 0.7], 
    shininess=80,
    ambient=[0.09, 0.01, 0.01],
    reflectivity=0.2
)

# Ground plane
ground_material = Material(
    diffuse=[0.4, 0.4, 0.4], 
    specular=[0.1, 0.1, 0.1], 
    shininess=10,
    ambient=[0.08, 0.08, 0.08],
    reflectivity=0.2
)

print("Building scene...")

# Ground plane
rend.scene.append(Plane(
    position=[0, -3, 0], 
    normal=[0, 1, 0], 
    material=ground_material
))

# ========== 3 CILINDROS (diferentes tamaños, posiciones y materiales) ==========
print("\nAdding 3 CYLINDERS:")
print("  1. Opaque Cylinder (orange) - Large, back-left")
rend.scene.append(Cylinder(
    position=[-5, 0, -8], 
    radius=1.2, 
    height=5.0, 
    material=cylinder_opaque
))

print("  2. Reflective Cylinder (silver) - Medium, center")
rend.scene.append(Cylinder(
    position=[-2, -0.5, -5], 
    radius=0.8, 
    height=3.5, 
    material=cylinder_reflective
))

print("  3. Transparent Cylinder (blue glass) - Small, front")
rend.scene.append(Cylinder(
    position=[-3.5, 0.5, -3], 
    radius=0.6, 
    height=2.5, 
    material=cylinder_transparent
))

# ========== 3 ELIPSOIDES (diferentes tamaños, proporciones y materiales) ==========
print("\nAdding 3 ELLIPSOIDS:")
print("  1. Opaque Ellipsoid (green) - Stretched horizontally")
rend.scene.append(Ellipsoid(
    position=[5, -1, -7], 
    radii=[2.0, 1.0, 1.0],  # Ancho en X
    material=ellipsoid_opaque
))

print("  2. Reflective Ellipsoid (gold) - Tall")
rend.scene.append(Ellipsoid(
    position=[3, 1, -5], 
    radii=[0.8, 1.8, 0.8],  # Alto en Y
    material=ellipsoid_reflective
))

print("  3. Transparent Ellipsoid (pink glass) - Small, flat")
rend.scene.append(Ellipsoid(
    position=[4.5, -0.5, -3], 
    radii=[1.2, 0.5, 1.0],  # Achatado en Y
    material=ellipsoid_transparent
))

# ========== ESTRELLA: 4 TRIÁNGULOS ==========
print("\nAdding STAR (4 triangles):")
star_center = [0, 2, -5]
star_size = 1.8

# Triángulo 1: Punta ARRIBA
rend.scene.append(Triangle(
    vertices=[
        [star_center[0], star_center[1] + star_size, star_center[2]],  # Punta arriba
        [star_center[0] - star_size*0.3, star_center[1], star_center[2]],  # Izquierda
        [star_center[0] + star_size*0.3, star_center[1], star_center[2]]   # Derecha
    ],
    material=star_material
))

# Triángulo 2: Punta ABAJO
rend.scene.append(Triangle(
    vertices=[
        [star_center[0], star_center[1] - star_size, star_center[2]],  # Punta abajo
        [star_center[0] + star_size*0.3, star_center[1], star_center[2]],  # Derecha
        [star_center[0] - star_size*0.3, star_center[1], star_center[2]]   # Izquierda
    ],
    material=star_material
))

# Triángulo 3: Punta IZQUIERDA
rend.scene.append(Triangle(
    vertices=[
        [star_center[0] - star_size, star_center[1], star_center[2]],  # Punta izquierda
        [star_center[0], star_center[1] + star_size*0.3, star_center[2]],  # Arriba
        [star_center[0], star_center[1] - star_size*0.3, star_center[2]]   # Abajo
    ],
    material=star_material
))

# Triángulo 4: Punta DERECHA
rend.scene.append(Triangle(
    vertices=[
        [star_center[0] + star_size, star_center[1], star_center[2]],  # Punta derecha
        [star_center[0], star_center[1] - star_size*0.3, star_center[2]],  # Abajo
        [star_center[0], star_center[1] + star_size*0.3, star_center[2]]   # Arriba
    ],
    material=star_material
))

# ========== CUBO EN EL CENTRO DE LA ESTRELLA ==========
print("  Adding CUBE at star center (red)")
rend.scene.append(Cube(
    position=star_center,  # Mismo centro que la estrella
    size=0.8,  # Tamaño pequeño para no tapar toda la estrella
    material=cube_material
))

print("\nSetting up lighting...")

rend.lights.append(AmbientLight(
    intensity=0.4, 
    color=[1.0, 1.0, 1.0]
))

rend.lights.append(DirectionalLight(
    direction=[-0.5, -1, -0.8], 
    intensity=0.8, 
    color=[1.0, 1.0, 0.9]
))

rend.lights.append(DirectionalLight(
    direction=[0.8, -0.6, -0.2], 
    intensity=0.5, 
    color=[0.9, 0.9, 1.0]
))

rend.lights.append(DirectionalLight(
    direction=[0, -0.7, 0.7], 
    intensity=0.3, 
    color=[1.0, 0.95, 0.9]
))

print("\n" + "="*60)
print("SCENE SUMMARY:")
print("="*60)
print("CYLINDERS (3):")
print("  - Opaque (orange): Large cylinder")
print("  - Reflective (silver): Medium cylinder")
print("  - Transparent (blue): Small cylinder")
print("\nELLIPSOIDS (3):")
print("  - Opaque (green): Horizontally stretched")
print("  - Reflective (gold): Vertically tall")
print("  - Transparent (pink): Flat/squashed")
print("\nSTAR:")
print("  - 4 triangles forming a star (yellow/gold)")
print("  - 1 cube at the center (red)")
print("="*60)

print("\nStarting render...")

rend.reflection_depth = 0
rend.glRender()

output_filename = "raytracer_lab_final.bmp"
print(f"\nGenerating {output_filename}...")
GenerateBMP(output_filename, width, height, 3, rend.frameBuffer)

print(f"\n{'='*60}")
print("RENDER COMPLETE!")
print(f"{'='*60}")
print(f"Output: {output_filename}")
print("\nLAB REQUIREMENTS COMPLETED:")
print("  ✓ 2 NEW FIGURES implemented:")
print("    - Cylinder (ray intersect algorithm)")
print("    - Ellipsoid (ray intersect algorithm)")
print("  ✓ Each figure rendered 3 times:")
print("    - With different sizes")
print("    - With different positions")
print("    - With different materials (opaque, reflective, transparent)")
print("  ✓ Star made from 4 triangles")
print("  ✓ Cube at star center")
print("  ✓ Custom background color")
print(f"{'='*60}\n")

pygame.quit()