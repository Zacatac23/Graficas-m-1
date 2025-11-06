import pygame
import pygame.display
from pygame.locals import *

import glm

from gl import Renderer
from buffer import Buffer
from model import Model
from nuevos_vertex_shaders import *
from nuevos_fragment_shaders import *
from PIL import Image

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

# Modo: en vez de mostrar render en vivo, renderizamos un solo frame y guardamos una imagen.
# Si quieres volver al modo interactivo, reemplaza este bloque por el bucle original.

# Renderizamos un frame
deltaTime = clock.tick(60) / 1000
rend.elapsedTime += deltaTime

# Aplicamos una rotación final al modelo para la captura
modelo.rotation.y += 15 * deltaTime

rend.Render()

# Leemos el framebuffer y guardamos la imagen usando Pillow
from OpenGL.GL import glReadPixels, GL_RGB, GL_UNSIGNED_BYTE

data = glReadPixels(0, 0, width, height, GL_RGB, GL_UNSIGNED_BYTE)
image = Image.frombytes("RGB", (width, height), data)
image = image.transpose(Image.FLIP_TOP_BOTTOM)
output_path = "render_output.png"
image.save(output_path)
print(f"Imagen guardada en: {output_path}")

pygame.quit()