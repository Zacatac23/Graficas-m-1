import pygame
import sys
import numpy as np
import math

# Import modules
import gl
from BMP_Writer import GenerateBMP
from figures import Sphere, Plane, Triangle, Cube, Cylinder, Ellipsoid, Disk, Cone, Rectangle, Torus
from lights import AmbientLight, DirectionalLight
from material import Material

# Get Renderer class
Renderer = gl.Renderer 

width = 1200
height = 900

print("="*70)
print("BARREL EXPLOSION RAYTRACER - FINAL VERSION")
print("="*70)

pygame.init()
screen = pygame.display.set_mode((width, height), pygame.HIDDEN)

rend = Renderer(screen)
rend.camera.translation = [2, 2, 11]
rend.glClearColor(0.05, 0.05, 0.08)  # FONDO MÁS OSCURO

print("\n[1/6] Creating materials...")

# ========== MATERIALES ==========

wood_material = Material(
    diffuse=[0.52, 0.38, 0.26], 
    specular=[0.2, 0.18, 0.15], 
    shininess=25,
    ambient=[0.35, 0.25, 0.18],
    reflectivity=0.08
)

dark_wood_material = Material(
    diffuse=[0.40, 0.28, 0.20], 
    specular=[0.15, 0.12, 0.10], 
    shininess=18,
    ambient=[0.28, 0.20, 0.14],
    reflectivity=0.05
)

metal_material = Material(
    diffuse=[0.5, 0.55, 0.6], 
    specular=[0.9, 0.9, 0.9], 
    shininess=100,
    ambient=[0.3, 0.33, 0.36],
    reflectivity=0.4
)

rusty_metal = Material(
    diffuse=[0.35, 0.35, 0.4], 
    specular=[0.5, 0.5, 0.5], 
    shininess=60,
    ambient=[0.2, 0.2, 0.25],
    reflectivity=0.2
)

skull_material = Material(
    diffuse=[0.9, 0.88, 0.85], 
    specular=[0.4, 0.4, 0.4], 
    shininess=30,
    ambient=[0.5, 0.48, 0.45],
    reflectivity=0.1
)

eye_material = Material(
    diffuse=[0.05, 0.05, 0.05],
    specular=[0.1, 0.1, 0.1],
    shininess=10,
    ambient=[0.02, 0.02, 0.02]
)

flame_core = Material(
    diffuse=[1.0, 1.0, 0.4], 
    specular=[1.0, 1.0, 0.9], 
    shininess=60,
    ambient=[1.0, 0.95, 0.35],
    transparency=0.25
)

flame_mid = Material(
    diffuse=[1.0, 0.65, 0.15], 
    specular=[1.0, 0.85, 0.6], 
    shininess=45,
    ambient=[0.95, 0.55, 0.12],
    transparency=0.35
)

flame_outer = Material(
    diffuse=[0.95, 0.35, 0.12], 
    specular=[0.9, 0.6, 0.4], 
    shininess=35,
    ambient=[0.85, 0.28, 0.10],
    transparency=0.45
)

flame_dark = Material(
    diffuse=[0.75, 0.25, 0.08], 
    specular=[0.7, 0.4, 0.25], 
    shininess=25,
    ambient=[0.65, 0.18, 0.06],
    transparency=0.55
)

cone_material = Material(
    diffuse=[0.3, 0.3, 0.35], 
    specular=[0.6, 0.6, 0.6], 
    shininess=80,
    ambient=[0.2, 0.2, 0.25],
    reflectivity=0.3
)

support_material = Material(
    diffuse=[0.25, 0.25, 0.28], 
    specular=[0.4, 0.4, 0.4], 
    shininess=50,
    ambient=[0.15, 0.15, 0.18],
    reflectivity=0.2
)

print("[2/6] Building barrel structure...")

# ========== BARRIL ==========
barrel_center = [0, 0, -5]
barrel_radius = 2.2
barrel_height = 4.0

# Cuerpo principal
rend.scene.append(Cylinder(
    position=barrel_center,
    radius=barrel_radius,
    height=barrel_height,
    material=wood_material
))

# Tapa superior
rend.scene.append(Disk(
    position=[barrel_center[0], barrel_center[1] + barrel_height/2, barrel_center[2]],
    radius=barrel_radius - 0.1,
    normal=[0, 1, 0],
    material=dark_wood_material
))

# Tapa inferior
rend.scene.append(Disk(
    position=[barrel_center[0], barrel_center[1] - barrel_height/2, barrel_center[2]],
    radius=barrel_radius - 0.1,
    normal=[0, -1, 0],
    material=dark_wood_material
))

# ========== CONO SUPERIOR CON CONECTOR ==========
print("[3/6] Adding cone on top with connector inside main cone...")

# Disco metálico en la parte superior del barril
rend.scene.append(Disk(
    position=[barrel_center[0], barrel_center[1] + barrel_height/2 + 0.05, barrel_center[2]],
    radius=barrel_radius,
    normal=[0, 1, 0],
    material=metal_material
))

# CONO CONECTOR - Base ABAJO (en barril), Punta ARRIBA (se mete en cono principal)
connector_cone_height = 1.5
connector_base_y = barrel_center[1] + barrel_height/2  # Base en el barril
connector_center_y = connector_base_y + connector_cone_height/2

rend.scene.append(Cone(
    position=[barrel_center[0], connector_center_y, barrel_center[2]],
    radius=barrel_radius,  # Base ancha (igual al barril)
    height=connector_cone_height,
    material=rusty_metal
))



overlap = 1.1  
cone_height = 2.8
cone_base_y = connector_base_y + connector_cone_height - overlap  # AÚN MÁS ABAJO
cone_center_y = cone_base_y + cone_height/2


cone_base_radius = barrel_radius * 0.85  # 85% del barril (MÁS GRANDE)

print(f"  Connector base radius: {barrel_radius:.2f}")
print(f"  Main cone base radius: {cone_base_radius:.2f} (smaller)")
print(f"  Connector tip inside main cone by: {overlap} units")

rend.scene.append(Cone(
    position=[barrel_center[0], cone_center_y, barrel_center[2]],
    radius=cone_base_radius,  # MÁS PEQUEÑO que el conector
    height=cone_height,
    material=cone_material
))

# ========== BANDAS METÁLICAS GRUESAS (inicio y final del barril) ==========
# Posicionar al inicio y final del barril (barrel_height = 4.0, entonces ±1.8 para estar cerca de los extremos)
band_positions = [-1.8, 1.8]  # Cerca del inicio y final del barril
for i, y_offset in enumerate(band_positions):
    mat = metal_material if i % 2 == 0 else rusty_metal
    rend.scene.append(Cylinder(  
        position=[barrel_center[0], barrel_center[1] + y_offset, barrel_center[2]],
        radius=barrel_radius + 0.08,  # Más gruesas (antes 0.03, ahora 0.08)
        height=0.6,  # Más altas (antes 0.25, ahora 0.6)
        material=mat
    ))

# ========== ESFERAS EN BANDA INFERIOR ==========
print("[4.5/6] Adding spheres on lower band...")
# Agregar esferas pequeñas alrededor de la banda inferior
sphere_count = 8
lower_band_y = barrel_center[1] + band_positions[0]  # band_positions[0] es -1.8 (banda inferior)
for i in range(sphere_count):
    angle = (i / sphere_count) * 2 * 3.14159
    sphere_radius = 0.15
    sphere_distance = barrel_radius + 0.2
    sphere_x = barrel_center[0] + sphere_distance * np.cos(angle)
    sphere_z = barrel_center[2] + sphere_distance * np.sin(angle)
    
    rend.scene.append(Sphere(
        position=[sphere_x, lower_band_y, sphere_z],
        radius=sphere_radius,
        material=metal_material
    ))

# ========== SOPORTES 3D SALIENDO DEL BARRIL ==========
print("[4/6] Adding 3D support structures coming out of barrel...")

support_width = 0.5
support_height = 0.5  # ALTURA MÍNIMA - patas súper cortas
support_depth = 0.5

for i in range(3):
    angle = (i * 120) * math.pi / 180
    
    # Posición pegada al barril (punto de conexión)
    x_start = barrel_center[0] + (barrel_radius - 0.05) * math.cos(angle)
    z_start = barrel_center[2] + (barrel_radius - 0.05) * math.sin(angle)
    
    # Posición en el suelo (punto final) - MINÚSCULO
    x_end = barrel_center[0] + (barrel_radius + 0.15) * math.cos(angle)  # Minúsculo
    z_end = barrel_center[2] + (barrel_radius + 0.15) * math.sin(angle)  # Minúsculo
    
    # Calcular punto inicial (pegado a la mitad del barril)
    y_start = barrel_center[1] - 0.5
    y_end = barrel_center[1] - barrel_height/2 - support_height
    
    # Paralelepípedo inclinado - PEGADO AL BARRIL
    # Soporte que va desde el barril (x_start, z_start) hasta el suelo (x_end, z_end)
    rend.scene.append(Rectangle(
        corner=[x_start - support_width/2, y_start, z_start - support_depth/2],  # Empieza PEGADO al barril
        width_vec=[support_width, 0, 0],  # Ancho horizontal
        height_vec=[x_end - x_start, y_end - y_start, z_end - z_start],  # Vector inclinado hacia afuera
        depth_vec=[0, 0, support_depth],  # Profundidad
        material=support_material
    ))

# ========== CALAVERA ==========
print("[5/6] Adding skull symbol...")

skull_center = [barrel_center[0], barrel_center[1] + 0.3, barrel_center[2] + barrel_radius + 0.02]

# Cráneo
rend.scene.append(Ellipsoid(
    position=skull_center,
    radii=[0.7, 0.8, 0.35],
    material=skull_material
))

# Ojo izquierdo
rend.scene.append(Ellipsoid(
    position=[skull_center[0] - 0.28, skull_center[1] + 0.15, skull_center[2] + 0.28],
    radii=[0.12, 0.18, 0.12],
    material=eye_material
))

# Ojo derecho
rend.scene.append(Ellipsoid(
    position=[skull_center[0] + 0.28, skull_center[1] + 0.15, skull_center[2] + 0.28],
    radii=[0.12, 0.18, 0.12],
    material=eye_material
))

# Nariz (triángulo invertido)
nose_center = [skull_center[0], skull_center[1] - 0.125, skull_center[2] + 0.35]
rend.scene.append(Triangle(
    vertices=[
        [nose_center[0], nose_center[1] + 0.075, nose_center[2] + 0.05],
        [nose_center[0] - 0.15, nose_center[1] - 0.075, nose_center[2] - 0.05],
        [nose_center[0] + 0.15, nose_center[1] - 0.075, nose_center[2] - 0.05]
    ],
    material=eye_material
))

# ========== EXPLOSIÓN DE FUEGO CON TOROIDES ==========
print("[6/6] Creating fire explosion with toruses...")

flame_base = [barrel_center[0], barrel_center[1] - barrel_height/2 - 2.5, barrel_center[2]]

# Núcleo central con toroides amarillos (2 toroides)
core_positions = [
    [0, 0, 0], [0, -0.4, 0]
]
for offset in core_positions:
    rend.scene.append(Torus(
        position=[flame_base[0] + offset[0], flame_base[1] + offset[1], flame_base[2] + offset[2]],
        major_radius=0.8,
        minor_radius=0.3,
        material=flame_core
    ))

# Capa naranja intermedia (3 toroides)
positions_mid = [
    [1.0, -0.6, 0.3], [-1.0, -0.5, -0.3], [0, -0.8, 0.6]
]
for offset in positions_mid:
    rend.scene.append(Torus(
        position=[flame_base[0] + offset[0], flame_base[1] + offset[1], flame_base[2] + offset[2]],
        major_radius=0.6,
        minor_radius=0.25,
        material=flame_mid
    ))

# Capa exterior con toroides rojos (4 toroides)
positions_outer = [
    [1.4, -0.9, 0.5], [-1.4, -0.8, -0.5], [0.5, -1.2, 0.8], [-0.5, -1.1, -0.8]
]
for offset in positions_outer:
    rend.scene.append(Torus(
        position=[flame_base[0] + offset[0], flame_base[1] + offset[1], flame_base[2] + offset[2]],
        major_radius=0.5,
        minor_radius=0.2,
        material=flame_outer
    ))

# Capa más externa con toroides rojos oscuros (3 toroides)
positions_dark = [
    [1.7, -1.2, 0.7], [-1.7, -1.1, -0.7], [0, -1.5, 0]
]
for offset in positions_dark:
    rend.scene.append(Torus(
        position=[flame_base[0] + offset[0], flame_base[1] + offset[1], flame_base[2] + offset[2]],
        major_radius=0.4,
        minor_radius=0.15,
        material=flame_dark
    ))

# Llamas superiores cerca del barril con toroides pequeños (2 toroides)
upper_flame_base = [barrel_center[0], barrel_center[1] - barrel_height/2 - 0.2, barrel_center[2]]
upper_positions = [
    [0, 0.8, 0], [0, 1.0, 0.2]
]
for offset in upper_positions:
    rend.scene.append(Torus(
        position=[upper_flame_base[0] + offset[0], upper_flame_base[1] + offset[1], upper_flame_base[2] + offset[2]],
        major_radius=0.3,
        minor_radius=0.12,
        material=flame_mid
    ))

# ========== ILUMINACIÓN ==========
print("\nConfiguring lighting...")

rend.lights.append(AmbientLight(
    intensity=0.5, 
    color=[1.0, 1.0, 1.0]
))

rend.lights.append(DirectionalLight(
    direction=[-0.4, -1, -0.6], 
    intensity=1.0, 
    color=[1.0, 1.0, 0.98]
))

rend.lights.append(DirectionalLight(
    direction=[1.2, -0.4, -0.5], 
    intensity=0.6, 
    color=[0.98, 0.98, 1.0]
))

# Luces de fuego
rend.lights.append(DirectionalLight(
    direction=[0, 1, -0.1], 
    intensity=1.2, 
    color=[1.0, 0.65, 0.25]
))

rend.lights.append(DirectionalLight(
    direction=[0.5, 0.8, 0.3], 
    intensity=0.9, 
    color=[1.0, 0.7, 0.3]
))

rend.lights.append(DirectionalLight(
    direction=[-0.5, 0.8, 0.3], 
    intensity=0.9, 
    color=[1.0, 0.6, 0.2]
))

print("\n" + "="*70)
print("SCENE STATISTICS")
print("="*70)
print(f"Total objects: {len(rend.scene)}")
print(f"  - Barrel: 1 cylinder + 2 disks")
print(f"  - Cone top: 1 cone + 1 disk")
print(f"  - Metal bands: 2 cylinders")
print(f"  - Support legs (3D boxes): 6 parallelepipeds (coming out of barrel)")
print(f"  - Skull: 1 ellipsoid + 2 eyes + 1 nose")
print(f"  - Fire particles: DISABLED (commented for faster render)")
print(f"\nTotal lights: {len(rend.lights)}")
print("="*70)

print("\nStarting render... Should be fast without fire!")
print("Progress will be shown every 10%\n")

rend.reflection_depth = 0
rend.glRender()

output_filename = "barrel_explosion.bmp"
print(f"\nGenerating BMP file: {output_filename}")
GenerateBMP(output_filename, width, height, 3, rend.frameBuffer)

print("\n" + "="*70)
print("✓ RENDER COMPLETE!")
print("="*70)
print(f"Output file: {output_filename}")
print(f"Resolution: {width}x{height} pixels")
print(f"Total objects rendered: {len(rend.scene)}")
print("="*70 + "\n")

pygame.quit()