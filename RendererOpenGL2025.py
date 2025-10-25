import pygame
import pygame.display
from pygame.locals import *

import glm

from gl import Renderer
from buffer import Buffer
from model import Model
from nuevos_vertex_shaders import *
from nuevos_fragment_shaders import *

# Importamos los nuevos shaders
from nuevos_vertex_shaders import pulse_vertex_shader, twist_vertex_shader, noise_displacement_vertex_shader
from nuevos_fragment_shaders import hologram_shader, thermal_shader, cartoon_shader, pixel_shader

width = 960
height = 540

deltaTime = 0.0

pygame.init()
screen = pygame.display.set_mode((width, height), pygame.DOUBLEBUF | pygame.OPENGL)
pygame.display.set_caption("Laboratorio de Shaders OpenGL")
clock = pygame.time.Clock()

# Inicializamos el renderer
rend = Renderer(screen)
rend.pointLight = glm.vec3(1, 1, 1)
rend.ambientLight = 0.2

# Configuración inicial de shaders
currVertexShader = pulse_vertex_shader  # Shader vertex por defecto
currFragmentShader = cartoon_shader  # Shader fragment por defecto

rend.SetShaders(currVertexShader, currFragmentShader)

# Cargamos las texturas para el skybox
skyboxTextures = ["skybox/right.jpg",
                  "skybox/left.jpg",
                  "skybox/top.jpg",
                  "skybox/bottom.jpg",
                  "skybox/front.jpg",
                  "skybox/back.jpg"]

rend.CreateSkybox(skyboxTextures)

# Cargamos el modelo para el laboratorio
# Puedes usar cualquier modelo OBJ de tu elección
modelo = Model("models/model.obj")
modelo.AddTexture("textures/model.bmp")
modelo.position.z = -5

rend.scene.append(modelo)

# Variables para controlar la configuración de shaders
shader_name = "Default Shader"
isRunning = True

while isRunning:

    deltaTime = clock.tick(60) / 1000
    rend.elapsedTime += deltaTime

    keys = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            isRunning = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_f:
                rend.ToggleFilledMode()

            # ================ CONFIGURACIÓN DE FRAGMENT SHADERS ================
            
            
            # Nuevos fragment shaders
            if event.key == pygame.K_5:
                currFragmentShader = hologram_shader
                shader_name = "Hologram Shader"
                rend.SetShaders(currVertexShader, currFragmentShader)
                
            if event.key == pygame.K_6:
                currFragmentShader = thermal_shader
                shader_name = "Thermal Vision Shader"
                rend.SetShaders(currVertexShader, currFragmentShader)
                
            if event.key == pygame.K_7:
                currFragmentShader = cartoon_shader
                shader_name = "Cartoon Shader"
                rend.SetShaders(currVertexShader, currFragmentShader)
                
            if event.key == pygame.K_8:
                currFragmentShader = pixel_shader
                shader_name = "Pixel Art Shader"
                rend.SetShaders(currVertexShader, currFragmentShader)

            # ================ CONFIGURACIÓN DE VERTEX SHADERS ================
            
            # Vertex shaders originales
            
            # Nuevos vertex shaders
            if event.key == pygame.K_KP4:
                currVertexShader = pulse_vertex_shader
                shader_name = "Pulse Vertex Shader + " + shader_name.split("+")[0]
                rend.SetShaders(currVertexShader, currFragmentShader)
                
            if event.key == pygame.K_KP5:
                currVertexShader = twist_vertex_shader
                shader_name = "Twist Vertex Shader + " + shader_name.split("+")[0]
                rend.SetShaders(currVertexShader, currFragmentShader)
                
            if event.key == pygame.K_KP6:
                currVertexShader = noise_displacement_vertex_shader
                shader_name = "Noise Displacement Vertex Shader + " + shader_name.split("+")[0]
                rend.SetShaders(currVertexShader, currFragmentShader)

    # Control de cámara
    if keys[K_UP]:
        rend.camera.position.z += 1 * deltaTime

    if keys[K_DOWN]:
        rend.camera.position.z -= 1 * deltaTime

    if keys[K_RIGHT]:
        rend.camera.position.x += 1 * deltaTime

    if keys[K_LEFT]:
        rend.camera.position.x -= 1 * deltaTime

    # Control de luz
    if keys[K_w]:
        rend.pointLight.z -= 10 * deltaTime

    if keys[K_s]:
        rend.pointLight.z += 10 * deltaTime

    if keys[K_a]:
        rend.pointLight.x -= 10 * deltaTime

    if keys[K_d]:
        rend.pointLight.x += 10 * deltaTime

    if keys[K_q]:
        rend.pointLight.y -= 10 * deltaTime

    if keys[K_e]:
        rend.pointLight.y += 10 * deltaTime

    # Control del parámetro value (para shaders que lo utilizan)
    if keys[K_z]:
        if rend.value > 0.0:
            rend.value -= 1 * deltaTime

    if keys[K_x]:
        if rend.value < 1.0:
            rend.value += 1 * deltaTime

    # Rotación del modelo
    modelo.rotation.y += 15 * deltaTime  # Velocidad de rotación reducida para mejor visualización

    # Render de la escena
    rend.Render()
    
    # Mostrar nombre del shader activo
    pygame.display.set_caption(f"Laboratorio de Shaders - {shader_name} - Value: {rend.value:.2f}")
    
    pygame.display.flip()

pygame.quit()