"""
kids_room_scene.py
Configuración específica para escena de cuarto de niño con juguetes
"""

import math
import os
from math_utils import Vec3
from scene_manager import Scene, SceneModel
from adaptive_positioning import AdaptivePositioning

class KidsRoomSceneBuilder:
    """Constructor de escenas específico para cuarto de niño"""
    
    @staticmethod
    def create_kids_room_scene():
        """Crear escena de cuarto de niño con juguetes"""
        scene = Scene("Cuarto de Niño con Juguetes")
        
        # JUGUETE 1: Peluche/Muñeco (principal) - MUY A LA IZQUIERDA Y ALTO
        toy1 = SceneModel(
            name="peluche_principal",
            obj_file="models/teddy_bear.obj",  # o tu archivo
            texture_file="textures/teddy_texture.png"
        ).set_transform(
            position=Vec3(-6, 2, 8),          # MUY izquierda, alto, adelante
            rotation=Vec3(0, math.pi/4, 0),   # Girado hacia el centro
            scale=Vec3(1.5, 1.5, 1.5)        # Más grande por ser principal
        ).set_shaders("displacement", "metallic")  # Suave y peludo
        
        # JUGUETE 2: Carro/Avión de juguete - MUY A LA DERECHA Y ATRÁS
        toy2 = SceneModel(
            name="vehiculo_juguete",
            obj_file="models/toy_car.obj",    # o tu archivo  
            texture_file="textures/toy_car_texture.png"
        ).set_transform(
            position=Vec3(8, 0, -6),          # MUY derecha, atrás
            rotation=Vec3(0, -math.pi/3, 0),  # Girado hacia centro
            scale=Vec3(1.2, 1.2, 1.2)
        ).set_shaders("wave", "psychedelic")  # Colores brillantes de juguete
        
        # JUGUETE 3: Bloque/Cubo de construcción - CENTRO FONDO
        toy3 = SceneModel(
            name="bloque_construccion",
            obj_file="models/building_block.obj",  # o tu archivo
            texture_file="textures/block_texture.png"
        ).set_transform(
            position=Vec3(-3, 1, -10),        # Centro-izquierda, MUY al fondo
            rotation=Vec3(0, math.pi/6, 0),   # Ligeramente rotado
            scale=Vec3(1.0, 1.0, 1.0)
        ).set_shaders("displacement", "psychedelic")  # Colores vibrantes
        
        # JUGUETE 4: Pelota/Balón - MUY ADELANTE DERECHA
        toy4 = SceneModel(
            name="pelota_juguete",
            obj_file="models/ball.obj",       # o tu archivo
            texture_file="textures/ball_texture.png"
        ).set_transform(
            position=Vec3(4, 0.5, 10),        # Derecha, ligeramente alto, MUY adelante
            rotation=Vec3(math.pi/8, 0, 0),   # Ligeramente inclinada
            scale=Vec3(0.9, 0.9, 0.9)
        ).set_shaders("wave", "metallic")    # Superficie brillante de pelota
        
        # Añadir juguetes a la escena
        scene.add_model(toy1)
        scene.add_model(toy2)
        scene.add_model(toy3)
        scene.add_model(toy4)
        
        # Configurar cámara como "vista panorámica del cuarto"
        scene.camera_position = Vec3(-2, 4, 12)  # Alejada para ver todo el cuarto
        scene.camera_target = Vec3(0, 1, 0)      # Mirando el centro del cuarto
        
        # Color de fondo cálido (si no hay imagen)
        scene.background_color = (255, 240, 220)  # Beige cálido de habitación
        
        # Configurar imagen de fondo de cuarto
        # scene.set_background_image("backgrounds/kids_room.jpg")
        
        return scene
    
    @staticmethod
    def create_kids_room_interactive():
        """Crear escena de cuarto de niño pidiendo archivos interactivamente"""
        print("\n🧸 CREADOR DE CUARTO DE NIÑO INTERACTIVO")
        print("="*60)
        print("🎨 Tema: Cuarto de niño con juguetes")
        print("💡 Posiciones optimizadas para ambiente infantil")
        print()
        
        scene = Scene("Mi Cuarto de Juguetes")
        
        # Configuraciones específicas para juguetes CON MÁXIMA SEPARACIÓN
        toy_configs = [
            {
                "name": "juguete_principal",
                "description": "Juguete principal (peluche, muñeco, robot)",
                "position": Vec3(-6, 2, 8),       # MUY A LA IZQUIERDA, ALTO, ADELANTE
                "rotation": Vec3(0, math.pi/4, 0),
                "scale": Vec3(1.5, 1.5, 1.5),    # Más grande
                "vertex_shader": "displacement",
                "fragment_shader": "metallic",
                "suggestion": "🧸 Peluche, muñeco, robot de juguete"
            },
            {
                "name": "vehiculo_juguete",
                "description": "Vehículo de juguete (carro, avión, tren)",
                "position": Vec3(8, 0, -6),      # MUY A LA DERECHA, ATRÁS
                "rotation": Vec3(0, -math.pi/3, 0),
                "scale": Vec3(1.2, 1.2, 1.2),
                "vertex_shader": "wave",
                "fragment_shader": "psychedelic",
                "suggestion": "🚗 Carro, avión, tren de juguete"
            },
            {
                "name": "juguete_construccion",
                "description": "Juguete de construcción (bloque, LEGO)",
                "position": Vec3(-3, 1, -10),    # CENTRO-IZQUIERDA, MUY AL FONDO
                "rotation": Vec3(0, math.pi/6, 0),
                "scale": Vec3(1.0, 1.0, 1.0),
                "vertex_shader": "displacement",
                "fragment_shader": "psychedelic",
                "suggestion": "🧱 Bloque, LEGO, pieza de construcción"
            },
            {
                "name": "pelota_juguete",
                "description": "Pelota o juguete redondo",
                "position": Vec3(4, 0.5, 10),    # DERECHA, LIGERAMENTE ALTO, MUY ADELANTE
                "rotation": Vec3(math.pi/8, 0, 0),
                "scale": Vec3(0.9, 0.9, 0.9),
                "vertex_shader": "wave",
                "fragment_shader": "metallic",
                "suggestion": "⚽ Pelota, balón, esfera de juguete"
            }
        ]
        
        models_added = 0
        
        for i, config in enumerate(toy_configs, 1):
            print(f"\n🧸 JUGUETE {i}/4: {config['name'].upper()}")
            print(f"📍 Posición: {config['suggestion']}")
            print(f"📐 Ubicación en cuarto: {config['description']}")
            print(f"🎨 Efecto visual: {config['vertex_shader']} + {config['fragment_shader']}")
            print("-" * 50)
            
            # Solicitar archivo OBJ
            while True:
                obj_file = input(f"📁 Archivo OBJ para {config['name']}: ").strip()
                
                if not obj_file:
                    print("⚠️  Debes especificar un archivo OBJ")
                    continue
                
                # Añadir extensión si no la tiene
                if not obj_file.lower().endswith('.obj'):
                    obj_file += '.obj'
                
                # Verificar si existe
                if os.path.exists(obj_file):
                    print(f"✅ Archivo encontrado: {obj_file}")
                    break
                else:
                    print(f"❌ Archivo '{obj_file}' no encontrado")
                    print("💡 Ejemplos de nombres comunes:")
                    print("   • teddy_bear.obj, toy_car.obj, block.obj, ball.obj")
                    print("   • bear.obj, car.obj, cube.obj, sphere.obj")
                    
                    retry = input("¿Intentar de nuevo? (s/n): ").lower()
                    if retry != 's':
                        print("⏭️  Saltando este juguete...")
                        obj_file = None
                        break
            
            if not obj_file:
                continue
            
            # Solicitar textura
            print(f"\n🎨 TEXTURA para {config['name']}:")
            texture_file = input("📁 Archivo de textura (Enter para omitir): ").strip()
            
            if texture_file:
                if not any(texture_file.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.bmp']):
                    texture_file += '.png'
                
                if os.path.exists(texture_file):
                    print(f"✅ Textura encontrada: {texture_file}")
                else:
                    print(f"⚠️  Textura '{texture_file}' no encontrada - continuando sin textura")
                    texture_file = None
            else:
                texture_file = None
                print("📝 Continuando sin textura")
            
            # Crear modelo con configuración adaptativa
            # Primero, necesitamos obtener el número de vértices del modelo cargado
            temp_loader = None
            vertex_count = 5000  # Default si no podemos obtener el número real
            
            try:
                from geometry import OBJLoader
                temp_loader = OBJLoader()
                if temp_loader.load_obj(obj_file):
                    vertex_count = len(temp_loader.vertices)
                    print(f"📊 Detectados {vertex_count} vértices en {obj_file}")
            except:
                print(f"⚠️  No se pudo analizar {obj_file}, usando configuración por defecto")
            
            # Determinar complejidad y ajustar configuración
            complexity = AdaptivePositioning.calculate_model_complexity(vertex_count)
            adaptive_scale = AdaptivePositioning.get_scale_for_complexity(complexity)
            
            # Ajustar posición base según complejidad
            base_positions = [
                Vec3(-8, 1, 6),    # Izquierda-adelante
                Vec3(10, 0, -8),   # Derecha-atrás  
                Vec3(-4, 0.5, -12), # Centro-fondo
                Vec3(6, 1, 8)      # Derecha-adelante
            ]
            
            adaptive_position = AdaptivePositioning.get_position_for_model(
                models_added, complexity, base_positions
            )
            
            # Escala combinada (configuración original * adaptativa)
            original_scale = config['scale'].x
            final_scale = original_scale * adaptive_scale
            
            print(f"🎯 ADAPTACIÓN APLICADA:")
            print(f"   📊 Complejidad: {complexity}")
            print(f"   📏 Escala adaptativa: {adaptive_scale:.1f}x")
            print(f"   📍 Posición ajustada: ({adaptive_position.x:+.1f}, {adaptive_position.y:+.1f}, {adaptive_position.z:+.1f})")
            
            model = SceneModel(
                name=config['name'],
                obj_file=obj_file,
                texture_file=texture_file
            ).set_transform(
                position=adaptive_position,  # Posición adaptativa
                rotation=config['rotation'],
                scale=Vec3(final_scale, final_scale, final_scale)  # Escala adaptativa
            ).set_shaders(config['vertex_shader'], config['fragment_shader'])
            
            scene.add_model(model)
            models_added += 1
            
            print(f"✅ {config['name']} configurado en posición de {config['description']}")
        
        # Configurar ambiente de cuarto
        print(f"\n🏠 CONFIGURACIÓN DEL CUARTO")
        
        # Cámara
        print("📷 Posición de cámara (perspectiva de niño):")
        use_default_camera = input("¿Usar cámara por defecto de niño? (s/n): ").lower()
        
        if use_default_camera != 's':
            try:
                cam_x = float(input("  X (-2): ") or "-2")
                cam_y = float(input("  Y (altura - 2): ") or "2") 
                cam_z = float(input("  Z (distancia - 6): ") or "6")
                scene.camera_position = Vec3(cam_x, cam_y, cam_z)
                scene.camera_target = Vec3(0, 0.5, 0)
            except ValueError:
                print("⚠️  Usando cámara por defecto")
                scene.camera_position = Vec3(-2, 4, 12)  # Cámara alejada
                scene.camera_target = Vec3(0, 1, 0)
        else:
            # Configurar cámara adaptativa basada en los modelos cargados
            if models_added > 0:
                # Calcular posición óptima de cámara
                model_positions = []
            for model in scene.models:
                model_positions.append({
                    'position': model.position,
                    'scale': model.scale.x
                })
            
            # Calcular límites de la escena
            if model_positions:
                min_x = min(pos['position'].x - pos['scale'] for pos in model_positions)
                max_x = max(pos['position'].x + pos['scale'] for pos in model_positions)
                min_z = min(pos['position'].z - pos['scale'] for pos in model_positions)
                max_z = max(pos['position'].z + pos['scale'] for pos in model_positions)
                
                # Centro y tamaño de la escena
                center_x = (min_x + max_x) / 2
                center_z = (min_z + max_z) / 2
                scene_size = max(max_x - min_x, max_z - min_z)
                
                # Calcular distancia de cámara
                camera_distance = scene_size * 0.7 + 10
                camera_height = scene_size * 0.3 + 4
                
                scene.camera_position = Vec3(
                    center_x - camera_distance * 0.4,
                    camera_height,
                    center_z + camera_distance
                )
                scene.camera_target = Vec3(center_x, 1, center_z)
                
                print(f"📷 CÁMARA ADAPTATIVA:")
                print(f"   📐 Tamaño de escena: {scene_size:.1f} unidades")
                print(f"   📍 Posición: ({scene.camera_position.x:.1f}, {scene.camera_position.y:.1f}, {scene.camera_position.z:.1f})")
                print(f"   🎯 Objetivo: ({scene.camera_target.x:.1f}, {scene.camera_target.y:.1f}, {scene.camera_target.z:.1f})")
            else:
                # Fallback a cámara por defecto
                scene.camera_position = Vec3(-2, 4, 12)
                scene.camera_target = Vec3(0, 1, 0)   # Mirando ligeramente hacia arriba
        
        # Fondo del cuarto
        print(f"\n🖼️  FONDO DEL CUARTO:")
        print("1. Imagen de cuarto de niño")
        print("2. Color cálido de habitación")
        
        background_choice = input("Seleccionar tipo de fondo (1-2): ").strip()
        
        if background_choice == "1":
            background_image = input("📁 Imagen de cuarto de niño: ").strip()
            if background_image and os.path.exists(background_image):
                scene.set_background_image(background_image)
                print(f"✅ Fondo de cuarto configurado: {background_image}")
            else:
                print("⚠️  Imagen no encontrada, usando color cálido")
                scene.background_color = (255, 240, 220)  # Beige cálido
        else:
            # Colores de cuarto
            room_colors = {
                "1": ((255, 240, 220), "Beige cálido"),
                "2": ((240, 248, 255), "Azul bebé"),
                "3": ((255, 240, 245), "Rosa suave"),
                "4": ((245, 255, 240), "Verde menta"),
                "5": ((255, 248, 220), "Amarillo suave")
            }
            
            print("Colores de cuarto:")
            for key, (color, name) in room_colors.items():
                print(f"  {key}. {name}")
            
            color_choice = input("Seleccionar color (1-5): ").strip()
            scene.background_color = room_colors.get(color_choice, room_colors["1"])[0]
        
        # Resumen de cuarto creado
        print(f"\n🧸 RESUMEN DEL CUARTO CREADO:")
        print("="*50)
        print(f"🏠 Tema: Cuarto de niño con juguetes")
        print(f"📦 Juguetes configurados: {models_added}")
        print(f"📷 Perspectiva: Altura de niño")
        
        print(f"\n🗺️  DISPOSICIÓN ADAPTATIVA DEL CUARTO:")
        print("       [Posiciones ajustadas según tamaño de modelo]")
        print("                                              ")
        
        # Mostrar cada modelo con su info específica
        for i, model in enumerate(scene.models, 1):
            pos = model.position
            scale = model.scale.x
            print(f"   🎯 {model.name}:")
            print(f"      └ Pos: ({pos.x:+.1f}, {pos.y:+.1f}, {pos.z:+.1f}) | Escala: {scale:.1f}x")
        
        print(f"                                              ")
        print(f"   📷 Cámara adaptativa en: ({scene.camera_position.x:.1f}, {scene.camera_position.y:.1f}, {scene.camera_position.z:.1f})")
        print(f"                                              ")
        
        # Calcular distancias entre modelos
        if len(scene.models) >= 2:
            print(f"\n📏 DISTANCIAS ENTRE MODELOS:")
            for i in range(len(scene.models)):
                for j in range(i + 1, len(scene.models)):
                    model1 = scene.models[i]
                    model2 = scene.models[j]
                    distance = ((model1.position.x - model2.position.x)**2 + 
                               (model1.position.y - model2.position.y)**2 + 
                               (model1.position.z - model2.position.z)**2)**0.5
                    print(f"   📐 {model1.name} ↔ {model2.name}: {distance:.1f} unidades")
        
        if scene.background_image_path:
            print(f"🖼️  Fondo: {os.path.basename(scene.background_image_path)}")
        else:
            print(f"🎨 Color de cuarto: {scene.background_color}")
        
        print("\n🎨 Efectos por juguete:")
        for model in scene.models:
            print(f"   🧸 {model.name}: {model.vertex_shader} + {model.fragment_shader}")
        
        return scene

# Configuraciones de fondos recomendados para cuarto de niño
KIDS_ROOM_BACKGROUNDS = {
    "modern_kids_room": {
        "description": "Cuarto moderno con cama, estantes, ventana",
        "mood": "Luminoso y organizado",
        "keywords": "modern kids bedroom, toy room, children's bedroom"
    },
    "cozy_nursery": {
        "description": "Cuarto acogedor con colores suaves",
        "mood": "Cálido y relajante",
        "keywords": "cozy nursery, baby room, soft colors"
    },
    "playroom": {
        "description": "Sala de juegos con alfombras coloridas",
        "mood": "Vibrante y divertido",
        "keywords": "children playroom, colorful carpet, toy storage"
    },
    "bedroom_window": {
        "description": "Cuarto con ventana y luz natural",
        "mood": "Natural y tranquilo",
        "keywords": "kids bedroom window, natural light, curtains"
    }
}

def get_kids_room_background_suggestions():
    """Obtener sugerencias de fondos para cuarto de niño"""
    print("\n🖼️  SUGERENCIAS DE FONDOS PARA CUARTO DE NIÑO:")
    print("="*60)
    
    for name, info in KIDS_ROOM_BACKGROUNDS.items():
        print(f"\n📁 {name}:")
        print(f"   📝 {info['description']}")
        print(f"   🎭 Ambiente: {info['mood']}")
        print(f"   🔍 Buscar: {info['keywords']}")
    
    print(f"\n💡 SITIOS RECOMENDADOS:")
    print("   • Unsplash.com - Buscar 'kids bedroom'")
    print("   • Pixabay.com - Buscar 'children room'")
    print("   • Pexels.com - Buscar 'nursery interior'")
    
    print(f"\n📐 TAMAÑO RECOMENDADO:")
    print("   • 1920x1080 (panorámica)")
    print("   • 1600x1200 (cuadrada)")
    print("   • Formato: JPG o PNG")