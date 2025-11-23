"""
implementacion_shaders_final.py — Script final con soporte para activar shaders de índices altos
"""

import pygame
import pygame.display
from pygame.locals import *
import glm
import sys
import os

# Importaciones OpenGL necesarias
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader

# Importar los módulos existentes
from gl import Renderer
from buffer import Buffer
from model import Model, CreateColorTexture
from postProcessingShaders import *

# Importar los shaders fresh originales
from freshShader import fresh_vertex_shader, fresh_fragment_shader

# Importar los nuevos shaders separados
from vertexShaders import *
from fragmentShaders import *

# Configuración inicial
width = 960
height = 540

pygame.init()
screen = pygame.display.set_mode((width, height), pygame.DOUBLEBUF | pygame.OPENGL)
pygame.display.set_caption("Demo Shaders OpenGL - Proyecto Avanzado")
clock = pygame.time.Clock()

# Inicializar fuente para el menú
pygame.font.init()
font = pygame.font.SysFont('Arial', 16)
font_title = pygame.font.SysFont('Arial', 20, bold=True)
font_small = pygame.font.SysFont('Arial', 14)

# Inicializar sistema de audio
pygame.mixer.init()
musicPlaying = False
musicPaused = False

# Cargar efectos de sonido
soundEffects = {}
try:
    # Crear carpeta de sonidos si no existe
    if not os.path.exists("sounds"):
        os.makedirs("sounds")
        print("📁 Carpeta 'sounds/' creada")
    
    # Intentar cargar sonidos específicos para cada modelo
    sound_names = ['cree', 'pick', 'sword', 'buck']
    
    for sound_name in sound_names:
        # Buscar el archivo con extensión .wav, .mp3 o .ogg
        sound_loaded = False
        for ext in ['.mp3', '.wav', '.ogg']:
            sound_path = os.path.join("sounds", sound_name + ext)
            if os.path.exists(sound_path):
                try:
                    soundEffects[sound_name] = pygame.mixer.Sound(sound_path)
                    soundEffects[sound_name].set_volume(0.5)
                    print(f"🔊 Sonido cargado: {sound_name}{ext}")
                    sound_loaded = True
                    break
                except Exception as e:
                    print(f"⚠ Error al cargar {sound_name}{ext}: {e}")
        
        if not sound_loaded:
            print(f"⚠ No se encontró: {sound_name}.mp3/.wav/.ogg")
    
    # Si no hay sonidos, generar sonido sintético simple
    if not soundEffects:
        print("⚠ No se encontraron archivos de sonido en 'sounds/'")
        print("  Coloca archivos: creeper.wav, pickaxe.wav, sword.wav, bucket.wav")
        print("  Generando sonido genérico...")
        
        # Generar sonido genérico (beep corto)
        duration = 0.1
        frequency = 800
        sample_rate = 22050
        n_samples = int(round(duration * sample_rate))
        
        # Crear array de sonido
        import numpy as np
        buf = np.sin(2 * np.pi * frequency * np.linspace(0, duration, n_samples))
        buf = (buf * 32767).astype(np.int16)
        
        # Crear sonido para pygame
        sound = pygame.sndarray.make_sound(buf)
        sound.set_volume(0.3)
        
        # Usar el mismo sonido para todos
        soundEffects['cree'] = sound
        soundEffects['pick'] = sound
        soundEffects['sword'] = sound
        soundEffects['buck'] = sound
        print("✓ Sonido genérico asignado a todos los modelos")

except Exception as e:
    print(f"⚠ Error al cargar efectos de sonido: {e}")
    print("  El programa continuará sin efectos de sonido")

# Intentar cargar música de fondo
try:
    # Buscar archivos de música en la carpeta music/
    music_files = []
    if os.path.exists("music"):
        for file in os.listdir("music"):
            if file.endswith(('.mp3', '.ogg', '.wav')):
                music_files.append(os.path.join("music", file))
    
    if music_files:
        pygame.mixer.music.load(music_files[0])
        pygame.mixer.music.set_volume(0.3)  # Volumen al 30%
        pygame.mixer.music.play(-1)  # -1 = loop infinito
        musicPlaying = True
        print(f"♪ Música cargada: {music_files[0]}")
        print("  Controles: [Y] Pausar/Reanudar | [+/-] Volumen")
    else:
        print("⚠ No se encontró música en la carpeta 'music/'")
        print("  Coloca archivos .mp3, .ogg o .wav en la carpeta 'music/' para reproducir música")
except Exception as e:
    print(f"⚠ No se pudo cargar la música: {e}")
    musicPlaying = False

# Inicializar el renderer
rend = Renderer(screen)
rend.pointLight = glm.vec3(1, 1, 1)

# Lista de pares de shaders disponibles
shader_pairs = [
    # Cada tupla contiene (nombre del shader, vertex shader, fragment shader)
    ("Fresh Shader", fresh_vertex_shader, fresh_fragment_shader),
    
    # Combinaciones con el vertex shader original y fragmentos avanzados
    ("Toon Shader", fresh_vertex_shader, toon_fragment_shader),
    ("Phong Shader", fresh_vertex_shader, phong_fragment_shader),
    ("Color Shift", fresh_vertex_shader, color_shift_fragment_shader),
    ("Neon Effect", fresh_vertex_shader, neon_fragment_shader),
    ("Pulse Alpha", fresh_vertex_shader, pulse_fragment_shader),
    ("Pixelate", fresh_vertex_shader, pixelate_fragment_shader),
    ("X-Ray", fresh_vertex_shader, xray_fragment_shader),
    
    # Combinaciones con vertex shaders avanzados y fragment shader original
    ("Wave Effect", wave_vertex_shader, fresh_fragment_shader),
    ("Rotation", rotation_vertex_shader, fresh_fragment_shader),
    ("Explode Effect", explode_vertex_shader, fresh_fragment_shader),
    ("Pulse Vertex", pulse_vertex_shader, fresh_fragment_shader),
    ("Noise Vertex", noise_vertex_shader, fresh_fragment_shader),
    
    # Combinaciones completas (vertex y fragment avanzados)
    ("Fire Effect", fire_vertex_shader, fire_fragment_shader),
    ("Ice Effect", ice_vertex_shader, ice_fragment_shader),
]

# Variables para el sistema de selección de shaders de dos dígitos
waiting_for_second_digit = False
first_digit = 0

# Shader actual seleccionado
current_shader_index = 0
currVertexShader, currFragmentShader = shader_pairs[current_shader_index][1:3]

# Configurar el shader inicial
rend.SetShaders(currVertexShader, currFragmentShader)
rend.SetPostProcessingShaders(vertex_postProcess, none_postProcess)

# Cargar skybox si existe
try:
    # Buscar archivos con extensión .jpg o .png
    skybox_names = ["right", "left", "top", "bottom", "front", "back"]
    skyboxTextures = []
    
    for name in skybox_names:
        # Buscar primero .png, luego .jpg
        if os.path.exists(f"skybox/{name}.png"):
            skyboxTextures.append(f"skybox/{name}.png")
        elif os.path.exists(f"skybox/{name}.jpg"):
            skyboxTextures.append(f"skybox/{name}.jpg")
        else:
            print(f"⚠ No se encontró: skybox/{name}.png ni skybox/{name}.jpg")
            skyboxTextures = []
            break
    
    if len(skyboxTextures) == 6:
        rend.CreateSkybox(skyboxTextures)
        print(f"✓ Skybox cargado correctamente ({skyboxTextures[0].split('.')[-1]} files)")
    else:
        print("⚠ Skybox no cargado: faltan archivos")
        
except Exception as e:
    print(f"⚠ Error al cargar el skybox: {e}")
    import traceback
    traceback.print_exc()

# Cargar modelos
try:
    # Creeper
    faceModel = Model("models/cree.obj")
    faceModel.AddTexture("textures/creeper.png")
    faceModel.position = glm.vec3(-4, 0, -5)
    faceModel.visible = True
    
    # Pickaxe
    pickModel = Model("models/pick.obj")
    pickModel.position = glm.vec3(-1.5, 0, -5)
    pickModel.scale = glm.vec3(0.05, 0.05, 0.05)
    pickModel.rotation = glm.vec3(90, 0, 0)
    pickModel.visible = True
    pickModel.textures = [CreateColorTexture((0.60, 0.40, 0.20))]
    pickModel.skipDefaultTexture = True
    
    # Espada
    swordModel = Model("models/sword.obj")
    swordModel.position = glm.vec3(0, 0, -5)
    swordModel.scale = glm.vec3(0.05, 0.05, 0.05)
    swordModel.rotation = glm.vec3(90, 0, 0)
    swordModel.visible = True
    try:
        swordModel.AddTexture("textures/Blue6.png")
    except:
        print("No se encontró la textura Blue6.png para la espada")
    
    # Balde
    buckModel = Model("models/buck.obj")
    buckModel.position = glm.vec3(1.5, 0, -5)
    buckModel.scale = glm.vec3(0.03, 0.03, 0.03)
    buckModel.visible = True
    buckModel.textures = [CreateColorTexture((0.45, 0.45, 0.45))]
    buckModel.skipDefaultTexture = True
    
    # Plano base
    planeModel = Model("models/plane.obj")
    planeModel.scale = glm.vec3(8.0, 1.0, 4.0)
    planeModel.position = glm.vec3(0.0, -1.0, -5.0)
    planeModel.visible = True
    planeModel.skipDefaultTexture = True
    planeModel.textures = [CreateColorTexture((0.3, 0.3, 0.3))]
    
    # Añadir modelos a la escena
    rend.scene.append(faceModel)
    rend.scene.append(pickModel)
    rend.scene.append(swordModel)
    rend.scene.append(buckModel)
    rend.scene.append(planeModel)
except Exception as e:
    print(f"Error al cargar los modelos: {e}")

# Asegurar que cada modelo tenga al menos una textura
for m in rend.scene:
    if getattr(m, 'skipDefaultTexture', False):
        continue
    if hasattr(m, 'textures') and len(m.textures) == 0:
        try:
            m.AddTexture("textures/model.bmp")
        except Exception as e:
            print(f"Advertencia: no se pudo añadir textura por defecto al modelo: {e}")

# Compilar el shader actual y asignarlo a todos los modelos
def apply_current_shader_to_all():
    global current_shader_index, shader_pairs
    vs, fs = shader_pairs[current_shader_index][1:3]
    prog = rend.CompileProgram(vs, fs)
    
    if prog is not None:
        for m in rend.scene:
            m.shaderProgram = prog
        print(f"Shader aplicado a todos los modelos: {shader_pairs[current_shader_index][0]}")
    else:
        print("Error al compilar el shader")

# ASIGNAR SHADERS DIFERENTES A CADA MODELO
print("\n=== ASIGNANDO SHADERS ÚNICOS A CADA MODELO ===")
# Definir qué shader usar para cada modelo
model_shader_assignments = [
    0,  # Creeper -> Fresh Shader
    1,  # Pickaxe -> Toon Shader
    8,  # Espada -> Wave Effect
    4,  # Balde -> Neon Effect
    14, # Plano -> Fire Effect
]

for i, model in enumerate(rend.scene):
    if i < len(model_shader_assignments):
        shader_idx = model_shader_assignments[i]
        vs, fs = shader_pairs[shader_idx][1:3]
        prog = rend.CompileProgram(vs, fs)
        
        if prog is not None:
            model.shaderProgram = prog
            print(f"Modelo {i} ({model.__class__.__name__}): {shader_pairs[shader_idx][0]}")
        else:
            print(f"Error al compilar shader para modelo {i}")

print("=== ASIGNACIÓN COMPLETADA ===\n")

# Variables de control
modelIndex = 0
postProcessIndex = 0
showAll = True
camAngle = 0
cameraOrbitDistance = 8.0
showMenu = True  # Variable para mostrar/ocultar el menú
frameCount = 0
lastInfoUpdate = 0

# Parámetros específicos para shaders
waveAmplitude = 0.5
rotationSpeed = 1.0
explosionFactor = 0.5
pulseIntensity = 0.5
noiseIntensity = 0.5
pixelSize = 10.0  # Tamaño de píxel para el shader de pixelado

# Lista de post-procesados
postProcesses = [
    none_postProcess,
    grayScale_postProcess,
    negative_postProcess,
    hurt_postProcess,
    depth_postProcess,
    fog_postProcess,
    dof_postProcess,
    edgeDetection_postProcess,
    outline_postProcess
]

# Función para mostrar ayuda en consola
def show_help():
    print("\n=== AYUDA DE CONTROLES ===")
    print("FLECHAS: Mover cámara")
    print("MOUSE CLICK IZQUIERDO + ARRASTRAR: Mover cámara")
    print("MOUSE CLICK DERECHO + ARRASTRAR: Orbitar cámara")
    print("RUEDA DEL MOUSE: Zoom")
    print("Q/E: Acercar/Alejar cámara")
    print("F: Alternar modo de renderizado (líneas/relleno)")
    print("M: Alternar modo de visualización (todos los modelos/modelo actual)")
    print("P/S/B: Alternar visibilidad de pico/espada/balde")
    print("G/H/J/K: Enfocar cámara en modelo 1/2/3/4")
    print("TAB: Cambiar efecto de post-procesado")
    print("NÚMEROS: Cambiar shader")
    print("  - 1-9: Seleccionar shaders 1-9")
    print("  - SHIFT + NÚMEROS: Seleccionar shaders 10+")
    print("  - Ejemplo: SHIFT+1 y luego 5 para seleccionar shader 15")
    print("0: Reasignar shader actual al modelo seleccionado")
    print("Z/X: Disminuir/Aumentar el valor uniforme")
    print("C/V: Disminuir/Aumentar amplitud de onda (para wave shader)")
    print("B/N: Disminuir/Aumentar velocidad de rotación (para rotation shader)")
    print("U/I: Disminuir/Aumentar factor de explosión (para explode shader)")
    print("O/P: Disminuir/Aumentar intensidad de pulso/ruido")
    print("K/L: Disminuir/Aumentar tamaño de píxel (para shader pixelate)")
    print("I: Mostrar información en tiempo real en consola")
    print("Y: Pausar/Reanudar música")
    print("+/-: Aumentar/Disminuir volumen")
    print("ESC: Salir")
    print("H: Mostrar esta ayuda")
    print("\nShaders disponibles:")
    for i, shader in enumerate(shader_pairs):
        print(f"{i+1}: {shader[0]}")
    print("=========================\n")

# Mostrar ayuda al inicio
show_help()

# Loop principal
isRunning = True
while isRunning:
    deltaTime = clock.tick(60) / 1000
    rend.elapsedTime += deltaTime
    
    # Centro para orbitar (modelo seleccionado actual)
    if len(rend.scene) > 0:
        orbitCenter = rend.scene[modelIndex].position
    else:
        orbitCenter = glm.vec3(0, 0, 0)
    
    keys = pygame.key.get_pressed()
    mouseVel = pygame.mouse.get_rel()
    
    # Manejo de eventos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            isRunning = False
        
        elif event.type == pygame.KEYDOWN:
            # Salir con ESC
            if event.key == pygame.K_ESCAPE:
                isRunning = False
            
            # Mostrar ayuda con H
            if event.key == pygame.K_h:
                show_help()
            
            # Mostrar información en consola con I
            if event.key == pygame.K_i:
                showMenu = not showMenu
                if showMenu:
                    print("\n" + "="*60)
                    print("INFORMACIÓN DEL DIORAMA EN TIEMPO REAL ACTIVADA")
                    print("="*60)
                else:
                    print("\n" + "="*60)
                    print("INFORMACIÓN EN TIEMPO REAL DESACTIVADA")
                    print("="*60 + "\n")
            
            # Pausar/Reanudar música con Y
            if event.key == pygame.K_y and musicPlaying:
                if musicPaused:
                    pygame.mixer.music.unpause()
                    musicPaused = False
                    print("♪ Música reanudada")
                else:
                    pygame.mixer.music.pause()
                    musicPaused = True
                    print("♪ Música pausada")
            
            # Aumentar volumen con +
            if event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                if musicPlaying:
                    current_vol = pygame.mixer.music.get_volume()
                    new_vol = min(1.0, current_vol + 0.1)
                    pygame.mixer.music.set_volume(new_vol)
                    print(f"♪ Volumen: {int(new_vol * 100)}%")
            
            # Disminuir volumen con -
            if event.key == pygame.K_MINUS:
                if musicPlaying:
                    current_vol = pygame.mixer.music.get_volume()
                    new_vol = max(0.0, current_vol - 0.1)
                    pygame.mixer.music.set_volume(new_vol)
                    print(f"♪ Volumen: {int(new_vol * 100)}%")
            
            # Alternar modo de líneas/relleno
            if event.key == pygame.K_f:
                rend.ToggleFilledMode()
            
            # Alternar visualización de todos o solo el modelo seleccionado
            if event.key == pygame.K_m:
                showAll = not showAll
                if showAll:
                    for m in rend.scene:
                        m.visible = True
                else:
                    for i, m in enumerate(rend.scene):
                        m.visible = (i == modelIndex)
            
            # Alternar visibilidad de modelos individuales
            if event.key == pygame.K_p and len(rend.scene) > 1:
                rend.scene[1].visible = not rend.scene[1].visible
            if event.key == pygame.K_s and len(rend.scene) > 2:
                rend.scene[2].visible = not rend.scene[2].visible
            if event.key == pygame.K_b and len(rend.scene) > 3:
                rend.scene[3].visible = not rend.scene[3].visible
            
            # Enfocar cámara en modelos específicos
            if event.key == pygame.K_g and len(rend.scene) > 0:
                modelIndex = 0
                camPos = glm.vec3(orbitCenter.x, orbitCenter.y, orbitCenter.z + cameraOrbitDistance)
                rend.camera.position = camPos
                rend.camera.LookAt(orbitCenter)
                # Reproducir sonido del creeper
                if 'cree' in soundEffects:
                    soundEffects['cree'].play()
            if event.key == pygame.K_j and len(rend.scene) > 1:
                modelIndex = 1
                orbitCenter = rend.scene[modelIndex].position
                camPos = glm.vec3(orbitCenter.x, orbitCenter.y, orbitCenter.z + cameraOrbitDistance)
                rend.camera.position = camPos
                rend.camera.LookAt(orbitCenter)
                # Reproducir sonido del pickaxe
                if 'pick' in soundEffects:
                    soundEffects['pick'].play()
            if event.key == pygame.K_k and len(rend.scene) > 2:
                modelIndex = 2
                orbitCenter = rend.scene[modelIndex].position
                camPos = glm.vec3(orbitCenter.x, orbitCenter.y, orbitCenter.z + cameraOrbitDistance)
                rend.camera.position = camPos
                rend.camera.LookAt(orbitCenter)
                # Reproducir sonido de la espada
                if 'sword' in soundEffects:
                    soundEffects['sword'].play()
            if event.key == pygame.K_l and len(rend.scene) > 3:
                modelIndex = 3
                orbitCenter = rend.scene[modelIndex].position
                camPos = glm.vec3(orbitCenter.x, orbitCenter.y, orbitCenter.z + cameraOrbitDistance)
                rend.camera.position = camPos
                rend.camera.LookAt(orbitCenter)
                # Reproducir sonido del balde
                if 'buck' in soundEffects:
                    soundEffects['buck'].play()
            
            # Cambiar post-procesado
            if event.key == pygame.K_TAB:
                postProcessIndex = (postProcessIndex + 1) % len(postProcesses)
                rend.SetPostProcessingShaders(vertex_postProcess, postProcesses[postProcessIndex])
                print(f"Post-procesado: {postProcessIndex + 1}/{len(postProcesses)}")
            
            # Sistema para seleccionar shaders con índices superiores a 9
            # Si se está esperando el segundo dígito
            if waiting_for_second_digit:
                if pygame.K_0 <= event.key <= pygame.K_9:
                    second_digit = event.key - pygame.K_0
                    shader_num = first_digit * 10 + second_digit - 1  # -1 porque los índices empiezan en 0
                    
                    if shader_num < len(shader_pairs):
                        current_shader_index = shader_num
                        print(f"Shader seleccionado: {shader_pairs[current_shader_index][0]}")
                        apply_current_shader_to_all()
                    else:
                        print(f"No existe shader con índice {shader_num+1}")
                    
                    waiting_for_second_digit = False
                else:
                    waiting_for_second_digit = False
            
            # Detectar teclas SHIFT + número para seleccionar shaders superiores a 9
            elif (keys[K_LSHIFT] or keys[K_RSHIFT]) and pygame.K_1 <= event.key <= pygame.K_9:
                first_digit = event.key - pygame.K_0
                print(f"Primer dígito: {first_digit}. Presione un segundo dígito (0-9)...")
                waiting_for_second_digit = True
                
            # Cambiar shader (teclas 1-9) sin SHIFT
            elif pygame.K_1 <= event.key <= pygame.K_9:
                shader_num = event.key - pygame.K_1
                if shader_num < len(shader_pairs):
                    current_shader_index = shader_num
                    print(f"Shader seleccionado: {shader_pairs[current_shader_index][0]}")
                    apply_current_shader_to_all()
            
            # Reasignar shader actual al modelo seleccionado
            elif event.key == pygame.K_0 and len(rend.scene) > 0:
                vs, fs = shader_pairs[current_shader_index][1:3]
                prog = rend.CompileProgram(vs, fs)
                if prog is not None:
                    rend.scene[modelIndex].shaderProgram = prog
                    print(f"Shader {shader_pairs[current_shader_index][0]} aplicado al modelo {modelIndex}")
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Click derecho cambia el modelo seleccionado
            if pygame.mouse.get_pressed()[2]:
                modelIndex = (modelIndex + 1) % len(rend.scene)
                if not showAll:
                    for i in range(len(rend.scene)):
                        rend.scene[i].visible = (i == modelIndex)
                # Reproducir sonido del modelo seleccionado
                sound_names = ['cree', 'pick', 'sword', 'buck', 'plane']
                if modelIndex < len(sound_names) and sound_names[modelIndex] in soundEffects:
                    soundEffects[sound_names[modelIndex]].play()
        
        elif event.type == pygame.MOUSEWHEEL:
            # Zoom con rueda del mouse
            cameraOrbitDistance -= event.y * 1.0
            if cameraOrbitDistance < 0.5:
                cameraOrbitDistance = 0.5
    
    # Disminuir/Aumentar el valor uniforme
    if keys[K_z]:
        if rend.value > 0.0:
            rend.value -= 1 * deltaTime
    if keys[K_x]:
        if rend.value < 1.0:
            rend.value += 1 * deltaTime
    
    # Controles para parámetros de shader específicos
    
    # Wave amplitude (para wave_vertex_shader)
    if keys[K_c]:
        waveAmplitude = max(0.0, waveAmplitude - 0.5 * deltaTime)
    if keys[K_v]:
        waveAmplitude = min(2.0, waveAmplitude + 0.5 * deltaTime)
    
    # Rotation speed (para rotation_vertex_shader)
    if keys[K_b]:
        rotationSpeed = max(0.0, rotationSpeed - 0.5 * deltaTime)
    if keys[K_n]:
        rotationSpeed = min(5.0, rotationSpeed + 0.5 * deltaTime)
    
    # Explosion factor (para explode_vertex_shader)
    if keys[K_u]:
        explosionFactor = max(0.0, explosionFactor - 0.5 * deltaTime)
    if keys[K_i]:
        explosionFactor = min(3.0, explosionFactor + 0.5 * deltaTime)
    
    # Pulse/Noise intensity
    if keys[K_o]:
        pulseIntensity = max(0.0, pulseIntensity - 0.5 * deltaTime)
        noiseIntensity = max(0.0, noiseIntensity - 0.5 * deltaTime)
    if keys[K_p]:
        pulseIntensity = min(2.0, pulseIntensity + 0.5 * deltaTime)
        noiseIntensity = min(2.0, noiseIntensity + 0.5 * deltaTime)
    
    # Pixel size para shader pixelate
    if keys[K_k]:
        pixelSize = max(1.0, pixelSize - 5.0 * deltaTime)
    if keys[K_l]:
        pixelSize = min(50.0, pixelSize + 5.0 * deltaTime)
    
    # Controles de cámara
    if keys[K_LEFT]:
        camAngle -= 60 * deltaTime
    if keys[K_RIGHT]:
        camAngle += 60 * deltaTime
    
    # Zoom con teclado
    if keys[K_q]:
        cameraOrbitDistance -= 5 * deltaTime
    if keys[K_e]:
        cameraOrbitDistance += 5 * deltaTime
    
    if cameraOrbitDistance < 0.5:
        cameraOrbitDistance = 0.5
    
    # Movimiento vertical
    if keys[K_UP]:
        rend.camera.position.y += 3 * deltaTime
    if keys[K_DOWN]:
        rend.camera.position.y -= 3 * deltaTime
    
    # Movimiento con mouse
    if pygame.mouse.get_pressed()[0]:
        rend.camera.position.x += mouseVel[0] * deltaTime
        rend.camera.position.y += mouseVel[1] * deltaTime
    
    # Orbitar con click derecho
    if pygame.mouse.get_pressed()[2]:
        camAngle += mouseVel[0] * 0.5
    
    # Actualizar posición de cámara
    if len(rend.scene) > 0:
        center = rend.scene[modelIndex].position
        y = rend.camera.position.y
        rend.camera.Orbit(center, cameraOrbitDistance, camAngle)
        rend.camera.position.y = y
    
    # Asegurar que la cámara mire al centro
    rend.camera.LookAt(rend.scene[modelIndex].position)
    
    # Pasar uniformes especiales a los shaders
    for model in rend.scene:
        if hasattr(model, 'shaderProgram') and model.shaderProgram is not None:
            prog = model.shaderProgram
            # Make the program active before setting its uniforms
            glUseProgram(prog)
            
            # Pasar waveAmplitude para el shader de ondas
            loc = glGetUniformLocation(prog, "waveAmplitude")
            if loc != -1:
                glUniform1f(loc, waveAmplitude)
            
            # Pasar rotationSpeed para el shader de rotación
            loc = glGetUniformLocation(prog, "rotationSpeed")
            if loc != -1:
                glUniform1f(loc, rotationSpeed)
            
            # Pasar explosionFactor para el shader de explosión
            loc = glGetUniformLocation(prog, "explosionFactor")
            if loc != -1:
                glUniform1f(loc, explosionFactor)
                
            # Pasar pulseIntensity para shader de pulso
            loc = glGetUniformLocation(prog, "pulseIntensity")
            if loc != -1:
                glUniform1f(loc, pulseIntensity)
                
            # Pasar noiseIntensity para shader de ruido
            loc = glGetUniformLocation(prog, "noiseIntensity")
            if loc != -1:
                glUniform1f(loc, noiseIntensity)
                
            # Pasar pixelSize para shader de pixelado
            loc = glGetUniformLocation(prog, "pixelSize")
            if loc != -1:
                glUniform1f(loc, pixelSize)
            # It's safe to unbind the program here; Render() will bind the program again when drawing
            glUseProgram(0)
    
    # Renderizar la escena
    rend.Render()
    
    # Mostrar información en el título de la ventana
    if showMenu:
        fps = int(clock.get_fps())
        post_names = ["None", "GrayScale", "Negative", "Hurt", "Depth", "Fog", "DoF", "Edge", "Outline"]
        model_names = ["Creeper", "Pickaxe", "Sword", "Bucket", "Plane"]
        
        title = f"Diorama OpenGL | FPS: {fps} | Model: {model_names[modelIndex]} | Post-FX: {post_names[postProcessIndex]} | [I] Info [H] Help"
        pygame.display.set_caption(title)
    else:
        pygame.display.set_caption("Diorama OpenGL - Proyecto 3 | [I] Show Info")
    
    # Mostrar información detallada en consola cada segundo
    frameCount += 1
    if rend.elapsedTime - lastInfoUpdate >= 2.0:
        lastInfoUpdate = rend.elapsedTime
        if showMenu:
            fps = int(clock.get_fps())
            post_names = ["None", "GrayScale", "Negative", "Hurt", "Depth", "Fog", "DoF", "Edge", "Outline"]
            model_names = ["Creeper", "Pickaxe", "Sword", "Bucket", "Plane"]
            
            print("\n" + "="*80)
            print(f"  FPS: {fps} | Modelo Seleccionado: {model_names[modelIndex]} | Post-Proceso: {post_names[postProcessIndex]}")
            print("  " + "-"*76)
            print("  SHADERS ASIGNADOS:")
            print("    • Creeper → Fresh Shader")
            print("    • Pickaxe → Toon Shader")
            print("    • Sword → Wave Effect")
            print("    • Bucket → Neon Effect")
            print("    • Plane → Fire Effect")
            print("="*80)
    
    pygame.display.flip()

# Limpieza al salir
pygame.quit()
print("Programa finalizado correctamente.")