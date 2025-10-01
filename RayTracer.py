import pygame
import sys

# Import modules
import gl
from BMP_Writer import GenerateBMP
from figures import  Plane, Triangle, Cube, Cylinder, Ellipsoid
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
rend.camera.translation = [0, 2, 18]  # Cámara más atrás para ver todo
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

# Material ROJO para estrella Y cubo
red_material = Material(
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

# ========== 3 CILINDROS (LADO IZQUIERDO - MUY SEPARADOS) ==========
print("\nAdding 3 CYLINDERS (LEFT SIDE):")
print("  1. Opaque Cylinder (orange) - Back left")
rend.scene.append(Cylinder(
    position=[-8, 0, -12],  # Muy atrás a la izquierda
    radius=1.2, 
    height=5.0, 
    material=cylinder_opaque
))

print("  2. Reflective Cylinder (silver) - Middle left")
rend.scene.append(Cylinder(
    position=[-6, -0.5, -7],  # Centro izquierda
    radius=0.8, 
    height=3.5, 
    material=cylinder_reflective
))

print("  3. Transparent Cylinder (blue glass) - Front left")
rend.scene.append(Cylinder(
    position=[-8, 0.5, -3],  # Adelante a la izquierda
    radius=0.6, 
    height=2.5, 
    material=cylinder_transparent
))

# ========== 3 ELIPSOIDES (LADO DERECHO - MUY SEPARADOS) ==========
print("\nAdding 3 ELLIPSOIDS (RIGHT SIDE):")
print("  1. Opaque Ellipsoid (green) - Back right")
rend.scene.append(Ellipsoid(
    position=[8, -1, -12],  # Muy atrás a la derecha
    radii=[2.0, 1.0, 1.0],
    material=ellipsoid_opaque
))

print("  2. Reflective Ellipsoid (gold) - Middle right")
rend.scene.append(Ellipsoid(
    position=[6, 1, -7],  # Centro derecha
    radii=[0.8, 1.8, 0.8],
    material=ellipsoid_reflective
))

print("  3. Transparent Ellipsoid (pink glass) - Front right")
rend.scene.append(Ellipsoid(
    position=[8, -0.5, -3],  # Adelante a la derecha
    radii=[1.2, 0.5, 1.0],
    material=ellipsoid_transparent
))

# ========== CUBO EN EL CENTRO ==========
print("\nAdding CUBE at CENTER (RED)")
star_center = [0, 1.5, -7]  # Centro de la escena
cube_size = 1.5

rend.scene.append(Cube(
    position=star_center,
    size=cube_size,
    material=red_material
))

# ========== ESTRELLA: 4 TRIÁNGULOS ==========
print("Adding STAR (4 triangles with base = cube face):")

triangle_base = cube_size
triangle_height = 2.0

# Triángulo ARRIBA
rend.scene.append(Triangle(
    vertices=[
        [star_center[0], star_center[1] + cube_size/2 + triangle_height, star_center[2]],
        [star_center[0] - triangle_base/2, star_center[1] + cube_size/2, star_center[2]],
        [star_center[0] + triangle_base/2, star_center[1] + cube_size/2, star_center[2]]
    ],
    material=red_material
))

# Triángulo ABAJO
rend.scene.append(Triangle(
    vertices=[
        [star_center[0], star_center[1] - cube_size/2 - triangle_height, star_center[2]],
        [star_center[0] + triangle_base/2, star_center[1] - cube_size/2, star_center[2]],
        [star_center[0] - triangle_base/2, star_center[1] - cube_size/2, star_center[2]]
    ],
    material=red_material
))

# Triángulo IZQUIERDA
rend.scene.append(Triangle(
    vertices=[
        [star_center[0] - cube_size/2 - triangle_height, star_center[1], star_center[2]],
        [star_center[0] - cube_size/2, star_center[1] + triangle_base/2, star_center[2]],
        [star_center[0] - cube_size/2, star_center[1] - triangle_base/2, star_center[2]]
    ],
    material=red_material
))

# Triángulo DERECHA
rend.scene.append(Triangle(
    vertices=[
        [star_center[0] + cube_size/2 + triangle_height, star_center[1], star_center[2]],
        [star_center[0] + cube_size/2, star_center[1] - triangle_base/2, star_center[2]],
        [star_center[0] + cube_size/2, star_center[1] + triangle_base/2, star_center[2]]
    ],
    material=red_material
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
print("SCENE LAYOUT:")
print("="*60)
print("LEFT SIDE - 3 CYLINDERS:")
print("  Back:   Opaque orange cylinder")
print("  Middle: Reflective silver cylinder")
print("  Front:  Transparent blue cylinder")
print("\nCENTER - RED STAR:")
print("  - Red cube")
print("  - 4 red triangles forming star")
print("\nRIGHT SIDE - 3 ELLIPSOIDS:")
print("  Back:   Opaque green ellipsoid")
print("  Middle: Reflective gold ellipsoid")
print("  Front:  Transparent pink ellipsoid")
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
print(f"{'='*60}\n")

pygame.quit()