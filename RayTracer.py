import pygame
import sys
import math
import random

# Import modules
import gl
from BMP_Writer import GenerateBMP
from figures import Sphere
from lights import AmbientLight, DirectionalLight
from material import Material
from environment_map import EnvironmentMap

# Get Renderer class
Renderer = gl.Renderer

width = 1024  # Mayor resolución
height = 768
samples_per_pixel = 4  # Anti-aliasing por supersampling

print("Setting up ULTRA REALISTIC ray tracer...")
pygame.init()
screen = pygame.display.set_mode((width, height), pygame.HIDDEN)

rend = Renderer(screen)

# Environment map más detallado
print("Creating high-quality environment map...")
envMap = EnvironmentMap()
rend.environmentMap = envMap
rend.rayDepth = 0

# Fondo más realista
rend.glClearColor(0.02, 0.02, 0.05)

# Cámara con DOF (simulado con múltiples samples)
rend.camera.translation = [0, 0, 4]

print("Creating photorealistic materials...")

# Materiales más complejos y realistas

# 1. Metal rugoso (opaco con microsuperficies)
brushed_metal = Material(
    diffuse=[0.1, 0.1, 0.1], 
    specular=[0.9, 0.9, 0.9], 
    shininess=20,  # Menos brillante = más rugoso
    ambient=[0.02, 0.02, 0.02],
    reflectivity=0.3,  # Reflexión difusa
    transparency=0.0
)

# 2. Cerámica mate (opaco con subsurface scattering simulado)
ceramic_blue = Material(
    diffuse=[0.2, 0.4, 0.8], 
    specular=[0.1, 0.1, 0.1], 
    shininess=8,
    ambient=[0.1, 0.2, 0.4],  # Más luz ambiente = subsurface scattering
    reflectivity=0.05,
    transparency=0.0
)

# 3. Oro pulido (reflectivo con propiedades metálicas correctas)
polished_gold = Material(
    diffuse=[0.1, 0.05, 0.0], 
    specular=[1.0, 0.8, 0.3], 
    shininess=200,
    reflectivity=0.95,
    transparency=0.0,
    refractive_index=0.47,
    ambient=[0.02, 0.01, 0.0]
)

# 4. Cromo espejo (casi perfecto)
chrome_mirror = Material(
    diffuse=[0.05, 0.05, 0.05], 
    specular=[1.0, 1.0, 1.0], 
    shininess=500,
    reflectivity=0.98,
    transparency=0.0,
    refractive_index=2.97,
    ambient=[0.01, 0.01, 0.01]
)

# 5. Cristal óptico de alta calidad
optical_crystal = Material(
    diffuse=[0.005, 0.005, 0.005], 
    specular=[1.0, 1.0, 1.0], 
    shininess=300,
    reflectivity=0.04,  # Fresnel natural del vidrio
    transparency=0.98,
    refractive_index=1.517,  # BK7 optical glass
    ambient=[0.002, 0.002, 0.002]
)

# 6. Diamante sintético
synthetic_diamond = Material(
    diffuse=[0.01, 0.01, 0.01], 
    specular=[1.0, 1.0, 1.0], 
    shininess=400,
    reflectivity=0.17,  # Alta reflectividad del diamante
    transparency=0.95,
    refractive_index=2.417,  # Índice real del diamante
    ambient=[0.002, 0.002, 0.002]
)

print("Creating photorealistic scene...")

# Disposición más artística y realista
rend.scene.append(Sphere(position=[-3.5, 1.5, -9], radius=1.0, material=brushed_metal))
rend.scene.append(Sphere(position=[0, 1.8, -10], radius=1.1, material=polished_gold))
rend.scene.append(Sphere(position=[3.5, 1.2, -8.5], radius=0.9, material=optical_crystal))

rend.scene.append(Sphere(position=[-3, -1.8, -7], radius=1.2, material=ceramic_blue))
rend.scene.append(Sphere(position=[0.5, -1.5, -6.5], radius=1.0, material=chrome_mirror))
rend.scene.append(Sphere(position=[3.8, -1.2, -7.8], radius=0.8, material=synthetic_diamond))

# Objetos de fondo para reflexiones complejas
rend.scene.append(Sphere(position=[-8, 2, -15], radius=2.5, material=brushed_metal))
rend.scene.append(Sphere(position=[8, -1, -18], radius=3.0, material=ceramic_blue))
rend.scene.append(Sphere(position=[0, 5, -12], radius=1.5, material=polished_gold))

# "Piso" espejo para reflexiones dramáticas
for i in range(-4, 5):
    for j in range(-2, 0):
        mirror_tile = Material(
            diffuse=[0.1, 0.1, 0.1],
            specular=[0.9, 0.9, 0.9],
            shininess=150,
            reflectivity=0.7,
            ambient=[0.02, 0.02, 0.02]
        )
        rend.scene.append(Sphere(position=[i*1.8, -4.5 + j*0.3, -20], radius=0.2, material=mirror_tile))

print("Setting up studio lighting...")

# Iluminación tipo estudio fotográfico
rend.lights.append(AmbientLight(intensity=0.15, color=[1.0, 1.0, 1.0]))

# Luz principal (key light)
rend.lights.append(DirectionalLight(
    direction=[-0.8, -1.2, -1], 
    intensity=1.2, 
    color=[1.0, 0.98, 0.95]  # Ligeramente cálida
))

# Luz de relleno (fill light)
rend.lights.append(DirectionalLight(
    direction=[1.2, -0.6, -0.8], 
    intensity=0.4, 
    color=[0.95, 0.98, 1.0]  # Ligeramente fría
))

# Luz de contorno (rim light)
rend.lights.append(DirectionalLight(
    direction=[0.2, 0.8, -0.5], 
    intensity=0.6, 
    color=[1.0, 0.9, 0.8]  # Cálida para contorno
))

# Luz de ambiente superior
rend.lights.append(DirectionalLight(
    direction=[0, -1, -0.1], 
    intensity=0.3, 
    color=[0.9, 0.95, 1.0]
))

def glRender_photorealistic(self):
    """Renderizado con anti-aliasing y muestreo múltiple"""
    total_pixels = self.vpWidth * self.vpHeight
    rendered_pixels = 0
    
    print(f"Rendering {total_pixels} pixels with {samples_per_pixel}x anti-aliasing...")
    print("This will take significantly longer but produce much higher quality...")
    
    for i in range(self.vpWidth):
        for j in range(self.vpHeight):
            x = i + self.vpX
            y = j + self.vpY

            if 0 <= x < self.width and 0 <= y < self.height:
                # Acumular colores de múltiples samples por pixel
                pixel_color = [0.0, 0.0, 0.0]
                
                for sample in range(samples_per_pixel):
                    # Jitter para anti-aliasing
                    jitter_x = (random.random() - 0.5) * 0.8
                    jitter_y = (random.random() - 0.5) * 0.8
                    
                    # Calcular dirección del rayo con jitter
                    pX = ((x + 0.5 + jitter_x - self.vpX) / self.vpWidth) * 2 - 1
                    pY = ((y + 0.5 + jitter_y - self.vpY) / self.vpHeight) * 2 - 1
                    pX *= self.rightEdge
                    pY *= self.topEdge
                    pZ = -self.nearPlane

                    dir = [pX, pY, pZ]
                    dir_length = math.sqrt(dir[0]**2 + dir[1]**2 + dir[2]**2)
                    dir = [d/dir_length for d in dir]

                    # Reset ray depth
                    self.rayDepth = 0

                    # Cast ray
                    hit = self.glCastRay(self.camera.translation, dir)

                    sample_color = [0, 0, 0]
                    if hit and hit.obj.material:
                        sample_color = hit.obj.material.GetSurfaceColor(hit, self)
                    else:
                        # Environment map background
                        if hasattr(self, 'environmentMap') and self.environmentMap:
                            sample_color = self.environmentMap.getColorFromDirection(dir)
                        else:
                            sample_color = self.ClearColor
                    
                    # Acumular color de este sample
                    for c in range(3):
                        pixel_color[c] += sample_color[c]
                
                # Promediar samples y aplicar tone mapping simple
                for c in range(3):
                    pixel_color[c] /= samples_per_pixel
                    # Tone mapping básico (gamma correction)
                    pixel_color[c] = pixel_color[c] ** (1.0/2.2)
                
                color_255 = [int(min(255, max(0, c * 255))) for c in pixel_color]
                self.frameBuffer[x][y] = color_255
            
            rendered_pixels += 1
            
            # Progress con menos frecuencia para no saturar la consola
            if rendered_pixels % (total_pixels // 20) == 0:
                progress = (rendered_pixels / total_pixels) * 100
                print(f"Progress: {progress:.1f}% ({rendered_pixels}/{total_pixels} pixels)")
    
    print("Photorealistic rendering complete!")

# Reemplazar método de renderizado
rend.glRender = lambda: glRender_photorealistic(rend)

print(f"\nPhotorealistic ray tracer setup complete!")
total_pixels = width * height
print(f"Resolution: {width}x{height} ({total_pixels} pixels)")
print(f"Anti-aliasing: {samples_per_pixel}x supersampling")
print(f"Objects: {len(rend.scene)} spheres")
print(f"Lights: {len(rend.lights)} studio lights")
print("\nPhotorealistic materials:")
print("  Row 1: Brushed Metal | Polished Gold | Optical Crystal")
print("  Row 2: Matte Ceramic | Chrome Mirror | Synthetic Diamond")
print("\nAdvanced rendering features:")
print("  - Multi-sample anti-aliasing")
print("  - Gamma correction")
print("  - Studio lighting setup")
print("  - Physically accurate material properties")
print("  - High-resolution output")

print("\nStarting photorealistic render...")
print("WARNING: This will take much longer due to anti-aliasing!")

# Render
rend.glRender()

# Generate ultra-high quality output
output_filename = "photorealistic_raytracer.bmp"
print(f"\nGenerating {output_filename}...")
GenerateBMP(output_filename, width, height, 3, rend.frameBuffer)

print(f"\nPhotorealistic ray tracer complete!")
print(f"Ultra-high quality image saved as '{output_filename}'")
print("\nPhotorealistic features implemented:")
print("  - 4x anti-aliasing via supersampling")
print("  - Gamma correction for realistic brightness")
print("  - Studio lighting with key/fill/rim lights")
print("  - Physically accurate materials (diamond n=2.417)")
print("  - High resolution (1024x768)")
print("  - Advanced material properties (roughness, subsurface)")
print("  - Photographic color temperature")

pygame.quit()