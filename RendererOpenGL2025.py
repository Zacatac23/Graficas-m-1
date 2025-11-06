import pygame
import pygame.display
from pygame.locals import *

import glm

from gl import Renderer
from buffer import Buffer
from model import Model
from nuevos_vertex_shaders import *
from nuevos_fragment_shaders import *
from envmap import EnvMap

# Importamos los nuevos shaders
from nuevos_vertex_shaders import pulse_vertex_shader, twist_vertex_shader, noise_displacement_vertex_shader
from nuevos_fragment_shaders import hologram_shader, thermal_shader, cartoon_shader, pixel_shader

width = 960
height = 540

deltaTime = 0.0

pygame.init()
screen = pygame.display.set_mode((width, height), pygame.DOUBLEBUF | pygame.OPENGL)
pygame.display.set_caption("Laboratorio de Shaders OpenGL - Interactivo")
clock = pygame.time.Clock()

# Inicializamos el renderer
rend = Renderer(screen)
rend.pointLight = glm.vec3(1, 1, 1)
rend.ambientLight = 0.2

# Configuración inicial de shaders
currVertexShader = pulse_vertex_shader  # Shader vertex por defecto
currFragmentShader = cartoon_shader  # Shader fragment por defecto

rend.SetShaders(currVertexShader, currFragmentShader)

# Cargamos un envmap (implementación distinta a la del skybox de clase)
env = EnvMap("textures/lava_cracks.jpg")
env.cameraRef = rend.camera

# Cargamos tres modelos (solo uno visible a la vez)
model_files = ["models/model.obj", "models/sphere.obj", "models/plane.obj"]
model_textures = ["textures/model.bmp", "textures/model.bmp", "textures/model.bmp"]
models = []
for idx, f in enumerate(model_files):
    m = Model(f)
    # try to add a texture if exists
    try:
        m.AddTexture(model_textures[idx])
    except Exception:
        pass
    
    # Ajustamos posición y escala según cada modelo
    if "model.obj" in f:  # Modelo 1
        # Ajuste del centro
        m.position = -m.bounds_center
        
        # SOLUCIÓN EMERGENCIA: Reducir escala para modelo 1
        m.scale = glm.vec3(0.3, 0.3, 0.3)  # Reducir a 30% del tamaño original
        
        # SOLUCIÓN EMERGENCIA: Mover hacia adelante (eje Z negativo) para mejor visualización
        m.position.z -= 5.0
        
        print(f"Modelo 1: Centro original: {m.bounds_center}, Posición ajustada: {m.position}, Escala: {m.scale}")
    
    elif "sphere.obj" in f:  # Modelo 2
        # Ajuste del centro
        m.position = -m.bounds_center
        # Escalar DRÁSTICAMENTE debido a su enorme tamaño (radio > 350)
        m.scale = glm.vec3(0.01, 0.01, 0.01)  # Reducir a 1/100 del tamaño original
        print(f"Modelo 2: Centro original: {m.bounds_center}, Posición ajustada: {m.position}, Escala: {m.scale}")
    
    elif "plane.obj" in f:  # Modelo 3
        # Ajuste del centro
        m.position = -m.bounds_center
        # Aumentar escala para hacerlo más visible
        m.scale = glm.vec3(5.0, 5.0, 5.0)  # Aumentar 5x para mejor visibilidad
        # Elevar un poco para mejor visualización
        m.position.y += 1.0
        print(f"Modelo 3: Centro original: {m.bounds_center}, Posición ajustada: {m.position}, Escala: {m.scale}")
    
    models.append(m)

# Mostrar información detallada de los modelos para depuración
print("\n=== INFORMACIÓN DE MODELOS ===")
for idx, model in enumerate(models):
    print(f"Modelo #{idx+1}: {model_files[idx]}")
    print(f"  Posición: {model.position}")
    print(f"  Centro Geométrico: {model.bounds_center}")
    print(f"  Tamaño (min): {model.bounds_min}")
    print(f"  Tamaño (max): {model.bounds_max}")
    print(f"  Radio: {model.bounds_radius}")
    print(f"  Escala: {model.scale}")
    print(f"  Centro Mundial: {model.position + model.bounds_center}")
    print()

# SOLUCIÓN EMERGENCIA: Configurar posición inicial de cámara manualmente
# En vez de usar cálculos basados en el modelo
manual_camera_position = glm.vec3(0, 0, 15)  # Posición fija, lejos en el eje Z

# Camera orbit parameters (around target = current model position)
orbit_radius = 15.0  # SOLUCIÓN EMERGENCIA: Radio fijo grande
orbit_theta = 0.0  # azimuth
orbit_phi = glm.radians(30.0)  # elevation (radians)
min_radius = 10.0  # SOLUCIÓN EMERGENCIA: Radio mínimo fijo grande
max_radius = 50.0  # Radio máximo
min_phi = glm.radians(5.0)
max_phi = glm.radians(85.0)
camera_sensitivity = 0.005
zoom_sensitivity = 0.4  # Reducido para control más fino

active_index = 0
rend.scene = []
rend.scene.append(env)
rend.scene.append(models[active_index])

env.cameraRef = rend.camera

shader_name = "Default Shader"

# FUNCIÓN COMPLETAMENTE REESCRITA para modelo 1
def init_camera_for_model(idx):
    global orbit_radius, min_radius, max_radius, orbit_phi
    m = models[idx]
    
    if idx == 0:  # Modelo 1 (model.obj) - configuración especial
        # Posición fija garantizada para estar fuera
        center = m.position + m.GetCenter()
        
        # SOLUCIÓN EMERGENCIA: Forzar valores grandes
        orbit_radius = 15.0
        min_radius = 10.0
        max_radius = 50.0
        
        # SOLUCIÓN EMERGENCIA: Posicionar cámara en Z+ mirando hacia Z-
        rend.camera.position = glm.vec3(0, 0, 15)
        rend.camera.LookAt(center)
        print(f"Modelo 1: Cámara forzada en posición Z+")
    else:
        # Para los otros modelos, usar la lógica normal
        center = m.position + m.GetCenter()
        
        # Calcular radio efectivo considerando la escala
        effective_radius = m.GetBoundingRadius() * max(m.scale.x, max(m.scale.y, m.scale.z))
        
        # Valores grandes para asegurar que la cámara esté lejos
        r = max(5.0, effective_radius * 8.0)
        orbit_radius = r
        
        min_radius = max(3.0, effective_radius * 4.0)
        max_radius = max(50.0, effective_radius * 20.0)
        
        if orbit_phi is None:
            orbit_phi = glm.radians(30.0)
        
        # Posicionar cámara
        horiz = orbit_radius * glm.cos(orbit_phi)
        cam_x = center.x + horiz * glm.sin(orbit_theta)
        cam_y = center.y + orbit_radius * glm.sin(orbit_phi)
        cam_z = center.z + horiz * glm.cos(orbit_theta)
        rend.camera.position = glm.vec3(cam_x, cam_y, cam_z)
        rend.camera.LookAt(center)
    
    print(f"Cámara posicionada en: {rend.camera.position}, mirando a: {center}, con radio orbital: {orbit_radius}")

init_camera_for_model(active_index)

# Mouse state
mouse_down = False
last_mouse_pos = (0, 0)

running = True
try:
    while running:
        deltaTime = clock.tick(60) / 1000.0
        rend.elapsedTime += deltaTime

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

                # switch models 1-3
                if event.key == pygame.K_1:
                    # set active model
                    rend.scene = [env, models[0]]
                    active_index = 0
                    init_camera_for_model(active_index)
                    print(f"Cambiado a modelo 1: {model_files[active_index]}")

                if event.key == pygame.K_2:
                    rend.scene = [env, models[1]]
                    active_index = 1
                    init_camera_for_model(active_index)
                    print(f"Cambiado a modelo 2: {model_files[active_index]}")

                if event.key == pygame.K_3:
                    rend.scene = [env, models[2]]
                    active_index = 2
                    init_camera_for_model(active_index)
                    print(f"Cambiado a modelo 3: {model_files[active_index]}")

                # shader controls (existing keys)
                if event.key == pygame.K_f:
                    rend.ToggleFilledMode()

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

                # vertex shader switches (numpad keys remain)
                if event.key == pygame.K_KP4:
                    currVertexShader = pulse_vertex_shader
                    rend.SetShaders(currVertexShader, currFragmentShader)

                if event.key == pygame.K_KP5:
                    currVertexShader = twist_vertex_shader
                    rend.SetShaders(currVertexShader, currFragmentShader)

                if event.key == pygame.K_KP6:
                    currVertexShader = noise_displacement_vertex_shader
                    rend.SetShaders(currVertexShader, currFragmentShader)
                
                # SOLUCIÓN EMERGENCIA: Mejor tecla de emergencia
                if event.key == pygame.K_r:
                    if active_index == 0:  # Modelo 1
                        # Resetear a posición Z+ fija
                        center = models[active_index].position + models[active_index].GetCenter()
                        rend.camera.position = glm.vec3(0, 0, 15)
                        rend.camera.LookAt(center)
                        orbit_radius = 15.0
                    else:
                        # Valores extremos para otros modelos
                        orbit_radius = max(20.0, models[active_index].GetBoundingRadius() * 10.0)
                        orbit_phi = glm.radians(45.0)  # Ángulo más pronunciado
                        init_camera_for_model(active_index)
                    print("¡CÁMARA RESTABLECIDA A POSICIÓN DE EMERGENCIA!")

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_down = True
                    last_mouse_pos = event.pos
                # wheel up/down for zoom
                if event.button == 4:
                    orbit_radius -= zoom_sensitivity * 2.0
                    orbit_radius = max(min_radius, orbit_radius)
                    print(f"Zoom in: {orbit_radius:.2f}")
                if event.button == 5:
                    orbit_radius += zoom_sensitivity * 2.0
                    orbit_radius = min(max_radius, orbit_radius)
                    print(f"Zoom out: {orbit_radius:.2f}")

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    mouse_down = False

            elif event.type == pygame.MOUSEMOTION:
                if mouse_down:
                    dx, dy = event.rel
                    orbit_theta -= dx * camera_sensitivity
                    orbit_phi += dy * camera_sensitivity
                    orbit_phi = max(min_phi, min(max_phi, orbit_phi))

            elif event.type == pygame.MOUSEWHEEL:
                orbit_radius -= event.y * zoom_sensitivity * 2.0
                orbit_radius = max(min_radius, min(max_radius, orbit_radius))
                print(f"Zoom: {orbit_radius:.2f}")

        # SOLUCIÓN EMERGENCIA: Control de teclado específico para modelo 1
        keys = pygame.key.get_pressed()
        if active_index == 0:  # Modelo 1
            # Controles personalizados para mover la cámara en el modelo 1
            if keys[K_LEFT] or keys[K_a]:
                rend.camera.position.x -= 0.1
            if keys[K_RIGHT] or keys[K_d]:
                rend.camera.position.x += 0.1
            if keys[K_UP] or keys[K_w]:
                rend.camera.position.y += 0.1
            if keys[K_DOWN] or keys[K_s]:
                rend.camera.position.y -= 0.1
            if keys[K_z]:
                # Acercar (pero nunca menos de min_radius)
                rend.camera.position.z -= 0.2
                if rend.camera.position.z < min_radius:
                    rend.camera.position.z = min_radius
            if keys[K_x]:
                # Alejar
                rend.camera.position.z += 0.2
            
            # Siempre mirar al centro del modelo
            center = models[active_index].position + models[active_index].GetCenter()
            rend.camera.LookAt(center)
        else:
            # Controles normales para los otros modelos
            if keys[K_LEFT] or keys[K_a]:
                orbit_theta -= 1.2 * deltaTime
            if keys[K_RIGHT] or keys[K_d]:
                orbit_theta += 1.2 * deltaTime
            if keys[K_UP] or keys[K_w]:
                orbit_phi -= 0.8 * deltaTime
                orbit_phi = max(min_phi, orbit_phi)
            if keys[K_DOWN] or keys[K_s]:
                orbit_phi += 0.8 * deltaTime
                orbit_phi = min(max_phi, orbit_phi)
            if keys[K_z]:
                orbit_radius -= 5.0 * deltaTime
                orbit_radius = max(min_radius, orbit_radius)
            if keys[K_x]:
                orbit_radius += 5.0 * deltaTime
                orbit_radius = min(max_radius, orbit_radius)

            # Calcular posición orbital para modelos 2-3
            target = models[active_index].position + models[active_index].GetCenter()
            r = orbit_radius
            elev = orbit_phi
            az = orbit_theta
            horiz = r * glm.cos(elev)
            cam_x = target.x + horiz * glm.sin(az)
            cam_y = target.y + r * glm.sin(elev)
            cam_z = target.z + horiz * glm.cos(az)
            rend.camera.position = glm.vec3(cam_x, cam_y, cam_z)
            rend.camera.LookAt(target)

        # small automatic rotation of the model for nicer view
        models[active_index].rotation.y += 15.0 * deltaTime

        # Render
        rend.Render()

        # SOLUCIÓN EMERGENCIA: Mostrar distancia real al centro para modelo 1
        if active_index == 0:
            center = models[active_index].position + models[active_index].GetCenter()
            dist = glm.distance(rend.camera.position, center)
            pygame.display.set_caption(f"Model {active_index+1} - {shader_name} - Distancia: {dist:.2f}")
        else:
            pygame.display.set_caption(f"Model {active_index+1} - {shader_name} - Radius: {orbit_radius:.2f}")
        
        pygame.display.flip()
except KeyboardInterrupt:
    print('\nInterrupted by user (KeyboardInterrupt)')
finally:
    pygame.quit()