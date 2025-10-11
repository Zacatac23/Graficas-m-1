import pygame
import sys
import numpy as np

# Import modules
import gl
from BMP_Writer import GenerateBMP
from figures import Sphere, Plane, Triangle, Cube, Cylinder, Ellipsoid, Disk, Cone, Rectangle
from lights import AmbientLight, DirectionalLight
from material import Material

# Get Renderer class
Renderer = gl.Renderer 

width = 1200
height = 900

print("Setting up Ray Tracer - BARREL WITH EXPLOSION SCENE")
pygame.init()
screen = pygame.display.set_mode((width, height), pygame.HIDDEN)

rend = Renderer(screen)
rend.camera.translation = [0, 3, 15]  
rend.glClearColor(0.95, 0.95, 0.97)  # Fondo blanco/gris claro

print("Creating materials...")

# ========== MATERIALES ==========

# Madera del barril (texturizada con colores variados)
wood_material = Material(
    diffuse=[0.45, 0.35, 0.25], 
    specular=[0.15, 0.15, 0.15], 
    shininess=20,
    ambient=[0.25, 0.20, 0.15],
    reflectivity=0.05,
    transparency=0.0
)

# Madera más oscura para variación
dark_wood_material = Material(
    diffuse=[0.35, 0.25, 0.18], 
    specular=[0.1, 0.1, 0.1], 
    shininess=15,
    ambient=[0.2, 0.15, 0.1],
    reflectivity=0.03,
    transparency=0.0
)

# Metal para las bandas
metal_material = Material(
    diffuse=[0.5, 0.55, 0.6], 
    specular=[0.9, 0.9, 0.9], 
    shininess=100,
    ambient=[0.3, 0.33, 0.36],
    reflectivity=0.4,
    transparency=0.0
)

# Metal oscuro/herrumbroso
rusty_metal = Material(
    diffuse=[0.35, 0.35, 0.4], 
    specular=[0.5, 0.5, 0.5], 
    shininess=60,
    ambient=[0.2, 0.2, 0.25],
    reflectivity=0.2,
    transparency=0.0
)

# Calavera - color hueso/blanco
skull_material = Material(
    diffuse=[0.9, 0.88, 0.85], 
    specular=[0.4, 0.4, 0.4], 
    shininess=30,
    ambient=[0.5, 0.48, 0.45],
    reflectivity=0.1,
    transparency=0.0
)

# Llamas - amarillo brillante (núcleo)
flame_core = Material(
    diffuse=[1.0, 0.95, 0.3], 
    specular=[1.0, 1.0, 0.8], 
    shininess=50,
    ambient=[0.9, 0.85, 0.25],
    reflectivity=0.0,
    transparency=0.3
)

# Llamas - naranja medio
flame_mid = Material(
    diffuse=[1.0, 0.6, 0.1], 
    specular=[1.0, 0.8, 0.5], 
    shininess=40,
    ambient=[0.9, 0.5, 0.08],
    reflectivity=0.0,
    transparency=0.4
)

# Llamas - rojo exterior
flame_outer = Material(
    diffuse=[0.9, 0.3, 0.1], 
    specular=[0.8, 0.5, 0.3], 
    shininess=30,
    ambient=[0.8, 0.25, 0.08],
    reflectivity=0.0,
    transparency=0.5
)

# Llamas - rojo oscuro
flame_dark = Material(
    diffuse=[0.7, 0.2, 0.05], 
    specular=[0.6, 0.3, 0.2], 
    shininess=20,
    ambient=[0.6, 0.15, 0.04],
    reflectivity=0.0,
    transparency=0.6
)

# Ground plane
ground_material = Material(
    diffuse=[0.7, 0.7, 0.7], 
    specular=[0.1, 0.1, 0.1], 
    shininess=10,
    ambient=[0.5, 0.5, 0.5],
    reflectivity=0.15
)

# Material para el cono (tapa superior)
cone_material = Material(
    diffuse=[0.3, 0.3, 0.35], 
    specular=[0.6, 0.6, 0.6], 
    shininess=80,
    ambient=[0.2, 0.2, 0.25],
    reflectivity=0.3,
    transparency=0.0
)

# Material para patas/soportes
support_material = Material(
    diffuse=[0.25, 0.25, 0.28], 
    specular=[0.4, 0.4, 0.4], 
    shininess=50,
    ambient=[0.15, 0.15, 0.18],
    reflectivity=0.2,
    transparency=0.0
)

print("Building scene...")

# ========== BARRIL - CENTRO DE LA ESCENA ==========
barrel_center = [0, 0, -5]
barrel_radius = 2.0
barrel_height = 4.5

print("\n========== BUILDING BARREL ==========")

# Cuerpo principal del barril (cilindro grande)
print("Adding main barrel body...")
rend.scene.append(Cylinder(
    position=barrel_center,
    radius=barrel_radius,
    height=barrel_height,
    material=wood_material
))

# Tapas del barril (discos arriba y abajo)
print("Adding barrel lids...")
rend.scene.append(Disk(
    position=[barrel_center[0], barrel_center[1] + barrel_height/2, barrel_center[2]],
    radius=barrel_radius - 0.1,
    normal=[0, 1, 0],
    material=dark_wood_material
))

rend.scene.append(Disk(
    position=[barrel_center[0], barrel_center[1] - barrel_height/2, barrel_center[2]],
    radius=barrel_radius - 0.1,
    normal=[0, -1, 0],
    material=dark_wood_material
))

# ========== CONO EN LA PARTE SUPERIOR ==========
print("Adding cone on top...")
cone_height = 1.5
cone_position = [barrel_center[0], barrel_center[1] + barrel_height/2 + cone_height/2, barrel_center[2]]

rend.scene.append(Cone(
    position=cone_position,
    radius=barrel_radius * 0.8,
    height=cone_height,
    material=cone_material
))

# Bandas metálicas (3 bandas alrededor del barril)
print("Adding metal bands...")
band_positions = [-1.5, 0, 1.5]  # Posiciones Y relativas
for i, y_offset in enumerate(band_positions):
    mat = metal_material if i % 2 == 0 else rusty_metal
    rend.scene.append(Cylinder(
        position=[barrel_center[0], barrel_center[1] + y_offset, barrel_center[2]],
        radius=barrel_radius + 0.05,
        height=0.3,
        material=mat
    ))

# ========== 3 RECTÁNGULOS (PATAS/SOPORTES) EN LA PARTE INFERIOR ==========
print("Adding 3 support rectangles at the bottom...")

support_width = 0.3
support_height = 1.5
support_depth = 1.2
base_y = barrel_center[1] - barrel_height/2

# Los rectángulos están distribuidos en ángulos de 120 grados alrededor del barril
import math

for i in range(3):
    angle = (i * 120) * math.pi / 180  # 0°, 120°, 240°
    
    # Posición del rectángulo (alejado del centro del barril)
    x_pos = barrel_center[0] + (barrel_radius + 0.1) * math.cos(angle)
    z_pos = barrel_center[2] + (barrel_radius + 0.1) * math.sin(angle)
    
    # Crear rectángulo vertical
    corner = [x_pos - support_width/2, base_y, z_pos - support_depth/2]
    width_vec = [support_width, 0, 0]
    height_vec = [0, support_height, 0]
    
    rend.scene.append(Rectangle(
        corner=corner,
        width_vec=width_vec,
        height_vec=height_vec,
        material=support_material
    ))
    
    # Agregar también la cara trasera para que se vea desde ambos lados
    corner_back = [x_pos - support_width/2, base_y, z_pos + support_depth/2]
    width_vec_back = [support_width, 0, 0]
    height_vec_back = [0, support_height, 0]
    
    rend.scene.append(Rectangle(
        corner=corner_back,
        width_vec=width_vec_back,
        height_vec=height_vec_back,
        material=support_material
    ))

# ========== CALAVERA EN EL BARRIL ==========
print("\n========== ADDING SKULL SYMBOL ==========")
skull_center = [barrel_center[0], barrel_center[1] + 0.5, barrel_center[2] + barrel_radius + 0.02]

# Cráneo (elipsoide)
print("Adding skull...")
rend.scene.append(Ellipsoid(
    position=skull_center,
    radii=[0.6, 0.7, 0.3],
    material=skull_material
))

# Ojos (dos esferas negras)
eye_material = Material(
    diffuse=[0.05, 0.05, 0.05],
    specular=[0.1, 0.1, 0.1],
    shininess=10,
    ambient=[0.02, 0.02, 0.02]
)

# Ojo izquierdo
rend.scene.append(Sphere(
    position=[skull_center[0] - 0.25, skull_center[1] + 0.15, skull_center[2] + 0.25],
    radius=0.15,
    material=eye_material
))

# Ojo derecho
rend.scene.append(Sphere(
    position=[skull_center[0] + 0.25, skull_center[1] + 0.15, skull_center[2] + 0.25],
    radius=0.15,
    material=eye_material
))

# Nariz (triángulo)
print("Adding nose...")
nose_tip = [skull_center[0], skull_center[1] - 0.1, skull_center[2] + 0.35]
rend.scene.append(Triangle(
    vertices=[
        nose_tip,
        [skull_center[0] - 0.12, skull_center[1] + 0.05, skull_center[2] + 0.25],
        [skull_center[0] + 0.12, skull_center[1] + 0.05, skull_center[2] + 0.25]
    ],
    material=eye_material
))

# ========== LLAMAS/EXPLOSIÓN DEBAJO DEL BARRIL ==========
print("\n========== ADDING FLAMES/EXPLOSION ==========")

flame_base = [barrel_center[0], barrel_center[1] - barrel_height/2 - 1.5, barrel_center[2]]

# Núcleo brillante (amarillo-blanco)
print("Adding flame cores...")
for offset in [[0, 0, 0], [0.3, -0.2, 0.2], [-0.3, -0.1, -0.2]]:
    rend.scene.append(Sphere(
        position=[flame_base[0] + offset[0], flame_base[1] + offset[1], flame_base[2] + offset[2]],
        radius=0.6,
        material=flame_core
    ))

# Capa intermedia (naranja brillante)
print("Adding mid flames...")
positions_mid = [
    [0.5, -0.5, 0.3], [-0.5, -0.4, 0.2], [0.2, -0.6, -0.3], 
    [-0.2, -0.5, -0.4], [0.6, -0.3, 0], [-0.6, -0.3, 0.1]
]
for offset in positions_mid:
    rend.scene.append(Sphere(
        position=[flame_base[0] + offset[0], flame_base[1] + offset[1], flame_base[2] + offset[2]],
        radius=0.5,
        material=flame_mid
    ))

# Capa exterior (rojo-naranja)
print("Adding outer flames...")
positions_outer = [
    [0.8, -0.8, 0.4], [-0.8, -0.7, 0.3], [0.4, -0.9, -0.5], 
    [-0.4, -0.8, -0.6], [0.9, -0.6, 0.2], [-0.9, -0.6, 0.1],
    [0.3, -1.0, 0.3], [-0.3, -0.9, 0.2], [0, -1.1, 0]
]
for offset in positions_outer:
    rend.scene.append(Sphere(
        position=[flame_base[0] + offset[0], flame_base[1] + offset[1], flame_base[2] + offset[2]],
        radius=0.45,
        material=flame_outer
    ))

# Capa más externa (rojo oscuro)
print("Adding dark outer flames...")
positions_dark = [
    [1.0, -1.0, 0.5], [-1.0, -0.9, 0.4], [0.6, -1.2, -0.6], 
    [-0.6, -1.1, -0.7], [1.1, -0.8, 0.3], [-1.1, -0.8, 0.2],
    [0.5, -1.3, 0.4], [-0.5, -1.2, 0.3], [0, -1.4, 0.1]
]
for offset in positions_dark:
    rend.scene.append(Sphere(
        position=[flame_base[0] + offset[0], flame_base[1] + offset[1], flame_base[2] + offset[2]],
        radius=0.4,
        material=flame_dark
    ))

# Llamas superiores (pequeñas, encima de la explosión principal)
print("Adding upper flames...")
upper_flame_base = [barrel_center[0], barrel_center[1] - barrel_height/2 - 0.5, barrel_center[2]]
for offset in [[0, 0.5, 0], [0.3, 0.6, 0.2], [-0.3, 0.7, -0.2]]:
    rend.scene.append(Sphere(
        position=[upper_flame_base[0] + offset[0], upper_flame_base[1] + offset[1], upper_flame_base[2] + offset[2]],
        radius=0.35,
        material=flame_mid
    ))

print("\n========== SETTING UP LIGHTING ==========")

# Luz ambiental suave
rend.lights.append(AmbientLight(
    intensity=0.7, 
    color=[1.0, 1.0, 1.0]
))

# Luz principal desde arriba-frente
rend.lights.append(DirectionalLight(
    direction=[-0.3, -1, -0.5], 
    intensity=0.9, 
    color=[1.0, 1.0, 0.95]
))

# Luz lateral para resaltar el barril
rend.lights.append(DirectionalLight(
    direction=[1, -0.5, -0.3], 
    intensity=0.5, 
    color=[0.95, 0.95, 1.0]
))

# Luz desde abajo (simulando el brillo del fuego)
rend.lights.append(DirectionalLight(
    direction=[0, 1, -0.2], 
    intensity=0.8, 
    color=[1.0, 0.7, 0.3]
))

print("\n" + "="*60)
print("SCENE SUMMARY:")
print("="*60)
print(f"Total objects: {len(rend.scene)}")
print("- 1 Barrel body (Cylinder)")
print("- 2 Barrel lids (Disks)")
print("- 1 Cone on top")
print("- 3 Metal bands (Cylinders)")
print("- 6 Support rectangles (3x2 faces)")
print("- 1 Skull (Ellipsoid)")
print("- 2 Eyes (Spheres)")
print("- 1 Nose (Triangle)")
print(f"- {3 + 6 + 9 + 9 + 3} Flame particles (Spheres)")
print(f"\nTotal lights: {len(rend.lights)}")
print("="*60)

print("\nStarting render...")

rend.reflection_depth = 0
rend.glRender()

output_filename = "barrel_explosion.bmp"
print(f"\nGenerating {output_filename}...")
GenerateBMP(output_filename, width, height, 3, rend.frameBuffer)

print(f"\n{'='*60}")
print("RENDER COMPLETE!")
print(f"{'='*60}")
print(f"Output: {output_filename}")
print(f"Resolution: {width}x{height}")
print(f"{'='*60}\n")

pygame.quit()