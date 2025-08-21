"""
interactive_scene_builder.py
Constructor in                "position": Vec3(-2, -3, -12),  # MÁS AL FONDO para contexto
                "rotation": Vec3(0, math.pi/8, 0),
                "scale": Vec3(3.5, 3.5, 3.5),  # Grande para ser visible desde lejos
                "vertex_shader": "displacement",
                "fragment_shader": "psychedelic",
                "importance": "🏗️ Para contexto ambiental"
            },
            {
                "name": "modelo_decorativo",
                "description": "Objeto decorativo (cristal, arma, reliquia)",
                "position": Vec3(4, 6, 8),  # MÁS ALTO Y SEPARADO - Flotando arriba
                "rotation": Vec3(math.pi/12, math.pi/6, 0),  # Ligeramente inclinado
                "scale": Vec3(1.8, 1.8, 1.8),  # Más grande para ser visible
                "vertex_shader": "wave",
                "fragment_shader": "metallic",
                "importance": "✨ Para efectos especiales (flotante)"
            }nas que pide nombres de archivos OBJ
"""

import os
import math
from math_utils import Vec3
from scene_manager import Scene, SceneModel

class InteractiveSceneBuilder:
    """Constructor de escenas interactivo que solicita archivos OBJ"""
    
    @staticmethod
    def build_demo_scene_interactive():
        """Construir escena de demostración pidiendo archivos interactivamente"""
        print("\n🎬 CONSTRUCTOR DE ESCENA DE DEMOSTRACIÓN - VERSIÓN OPTIMIZADA v2")
        print("="*60)
        print("📝 Necesitas 4 modelos OBJ con texturas para máxima puntuación")
        print("💡 Tip: Usa modelos de diferentes tipos para mejor puntuación")
        print("🔧 OPTIMIZACIONES APLICADAS:")
        print("   ✅ Escalas REDUCIDAS para tamaños apropiados")
        print("   ✅ Cámara MÁS ALEJADA para mejor perspectiva")
        print("   ✅ Posiciones bien separadas sin superposición")
        print("   ✅ Composición balanceada y visualmente atractiva")
        print()
        
        scene = Scene("Escena de Demostración Personalizada")
        
        # Configuraciones predefinidas para cada modelo con MEJOR SEPARACIÓN
        model_configs = [
            {
                "name": "modelo_principal",
                "description": "Modelo principal (COMPLEJO: personaje, robot, vehículo)",
                "position": Vec3(-8, 0, 4),  # MÁS SEPARADO - Izquierda, adelante
                "rotation": Vec3(0, math.pi/4, 0),  # Girado hacia el centro
                "scale": Vec3(1.2, 1.2, 1.2),  # ESCALA REDUCIDA - más apropiada
                "vertex_shader": "displacement",
                "fragment_shader": "metallic",
                "importance": "🏆 CRÍTICO para 10 pts extra"
            },
            {
                "name": "modelo_secundario",
                "description": "Modelo secundario (vehículo, máquina, criatura)",
                "position": Vec3(8, 0, -4),  # MÁS SEPARADO - Derecha, atrás
                "rotation": Vec3(0, -math.pi/4, 0),  # Girado hacia el centro
                "scale": Vec3(1.0, 1.0, 1.0),  # ESCALA REDUCIDA - tamaño normal
                "vertex_shader": "wave",
                "fragment_shader": "psychedelic",
                "importance": "⭐ Importante para variedad"
            },
            {
                "name": "modelo_arquitectonico",
                "description": "Elemento arquitectónico (edificio, castillo, estructura)",
                "position": Vec3(-2, -3, -12),  # MÁS AL FONDO para contexto
                "rotation": Vec3(0, math.pi/8, 0),
                "scale": Vec3(1.8, 1.8, 1.8),  # ESCALA REDUCIDA - más proporcionado
                "vertex_shader": "displacement",
                "fragment_shader": "psychedelic",
                "importance": "🏗️ Para contexto ambiental"
            },
            {
                "name": "modelo_decorativo",
                "description": "Objeto decorativo (cristal, arma, reliquia)",
                "position": Vec3(4, 6, 8),  # MÁS ALTO Y SEPARADO - Flotando arriba
                "rotation": Vec3(math.pi/12, math.pi/6, 0),  # Ligeramente inclinado
                "scale": Vec3(0.8, 0.8, 0.8),  # ESCALA PEQUEÑA - objeto decorativo
                "vertex_shader": "wave",
                "fragment_shader": "metallic",
                "importance": "✨ Para efectos especiales (flotante)"
            }
        ]
        
        models_added = 0
        
        for i, config in enumerate(model_configs, 1):
            print(f"\n📦 MODELO {i}/4: {config['name'].upper()}")
            print(f"📝 Tipo: {config['description']}")
            print(f"🎯 {config['importance']}")
            print(f"🎨 Shaders: {config['vertex_shader']} + {config['fragment_shader']}")
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
                    
                    # Ofrecer ayuda
                    print("💡 Opciones:")
                    print("   1. Verificar el nombre del archivo")
                    print("   2. Verificar que esté en el directorio actual")
                    print("   3. Usar ruta completa (ej: models/mi_modelo.obj)")
                    
                    retry = input("¿Intentar de nuevo? (s/n): ").lower()
                    if retry != 's':
                        print("⏭️  Saltando este modelo...")
                        obj_file = None
                        break
            
            if not obj_file:
                continue
            
            # Solicitar textura (opcional)
            print(f"\n🖼️  TEXTURA para {config['name']} (opcional pero recomendado):")
            texture_file = input("📁 Archivo de textura (Enter para omitir): ").strip()
            
            if texture_file:
                # Añadir extensión común si no la tiene
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
            
            # Crear modelo
            model = SceneModel(
                name=config['name'],
                obj_file=obj_file,
                texture_file=texture_file
            ).set_transform(
                position=config['position'],
                rotation=config['rotation'],
                scale=config['scale']
            ).set_shaders(config['vertex_shader'], config['fragment_shader'])
            
            scene.add_model(model)
            models_added += 1
            
            print(f"✅ {config['name']} configurado exitosamente!")
            
            # Preguntar si continuar
            if i < len(model_configs):
                print(f"\n📊 Progreso: {models_added}/{len(model_configs)} modelos configurados")
                continue_adding = input("¿Continuar con el siguiente modelo? (s/n): ").lower()
                if continue_adding != 's':
                    break
        
        # Configurar cámara
        print(f"\n📷 CONFIGURACIÓN DE CÁMARA")
        print("💡 Posición optimizada para ver todos los modelos separados")
        
        use_default_camera = input("¿Usar cámara OPTIMIZADA por defecto? (s/n): ").lower()
        
        if use_default_camera != 's':
            try:
                print("📍 Posición de cámara:")
                cam_x = float(input("  X (-8): ") or "-8")
                cam_y = float(input("  Y (10): ") or "10") 
                cam_z = float(input("  Z (20): ") or "20")
                scene.camera_position = Vec3(cam_x, cam_y, cam_z)
                
                print("🎯 Punto de enfoque:")
                target_x = float(input("  X (0): ") or "0")
                target_y = float(input("  Y (2): ") or "2")
                target_z = float(input("  Z (-2): ") or "-2")
                scene.camera_target = Vec3(target_x, target_y, target_z)
                
            except ValueError:
                print("⚠️  Valores inválidos, usando cámara por defecto")
                scene.camera_position = Vec3(-8, 10, 20)  # Cámara MÁS ALEJADA
                scene.camera_target = Vec3(0, 2, -2)
        else:
            scene.camera_position = Vec3(-8, 10, 20)  # Cámara MÁS ALEJADA para mejor perspectiva
            scene.camera_target = Vec3(0, 2, -2)      # Apuntando ligeramente hacia arriba
        
        # Configurar fondo
        print(f"\n🎨 CONFIGURACIÓN DE FONDO")
        print("Opciones:")
        print("1. Imagen de fondo personalizada")
        print("2. Color sólido")
        
        background_choice = input("Seleccionar tipo de fondo (1-2, Enter para color): ").strip()
        
        if background_choice == "1":
            # Imagen de fondo
            print(f"\n🖼️  IMAGEN DE FONDO:")
            background_image = input("📁 Ruta a imagen de fondo (jpg/png): ").strip()
            
            if background_image and os.path.exists(background_image):
                scene.set_background_image(background_image)
                print(f"✅ Imagen de fondo configurada: {background_image}")
            else:
                print(f"⚠️  Imagen '{background_image}' no encontrada, usando color sólido")
                background_choice = "2"
        
        if background_choice != "1":
            # Color sólido
            backgrounds = {
                "1": ((20, 30, 50), "Azul nocturno"),
                "2": ((50, 20, 30), "Rojo dramático"), 
                "3": ((30, 50, 20), "Verde bosque"),
                "4": ((10, 10, 10), "Negro espacial"),
                "5": ((40, 40, 40), "Gris neutro"),
                "6": ((60, 40, 20), "Sepia vintage"),
                "7": ((20, 40, 60), "Azul profundo")
            }
            
            print(f"\n🎨 COLORES DE FONDO:")
            for key, (color, name) in backgrounds.items():
                print(f"  {key}. {name} {color}")
            
            bg_choice = input("Seleccionar color (1-7, Enter para azul nocturno): ").strip()
            scene.background_color = backgrounds.get(bg_choice, backgrounds["1"])[0]
        
        # Resumen final con visualización de posiciones
        print(f"\n📋 RESUMEN DE ESCENA CREADA:")
        print("="*50)
        print(f"📦 Modelos configurados: {models_added}")
        print(f"📷 Cámara: pos=({scene.camera_position.x:.1f},{scene.camera_position.y:.1f},{scene.camera_position.z:.1f})")
        
        if scene.background_image_path:
            print(f"🖼️  Fondo: Imagen - {os.path.basename(scene.background_image_path)}")
        else:
            print(f"🎨 Fondo: Color - {scene.background_color}")
        
        print("\n🗺️  DISTRIBUCIÓN ESPACIAL (MUY SEPARADOS):")
        print("       [VISTA DESDE ARRIBA - ESCALA AMPLIADA]")
        print("                    Z")
        print("                    |")
        print("              📦4   |   ")
        print("                    |")
        print("   📦1          ----+----          📦2  → X")
        print("                    |")
        print("                    |")
        print("                 📦3|")
        print("                    |")
        print("                    |")
        print("                  📷 (cámara muy alejada)")
        
        print(f"\n🔍 DISTANCIAS ENTRE MODELOS:")
        for i in range(len(scene.models)):
            for j in range(i + 1, len(scene.models)):
                model1 = scene.models[i]
                model2 = scene.models[j]
                distance = ((model1.position.x - model2.position.x)**2 + 
                           (model1.position.y - model2.position.y)**2 + 
                           (model1.position.z - model2.position.z)**2)**0.5
                print(f"   📏 {model1.name} ↔ {model2.name}: {distance:.1f} unidades")
        
        print("\n🎨 Combinaciones de shaders:")
        
        for i, model in enumerate(scene.models, 1):
            pos = model.position
            print(f"   📦{i} {model.name}: {model.vertex_shader} + {model.fragment_shader}")
            print(f"      └ Posición: ({pos.x:+.1f}, {pos.y:+.1f}, {pos.z:+.1f})")
        
        # Estimación de puntuación
        estimated_score = models_added * 10  # Modelos
        estimated_score += min(len(set(f"{m.vertex_shader}+{m.fragment_shader}" for m in scene.models)) * 10, 40)  # Shaders
        estimated_score += 20  # Estética base
        
        print(f"\n📊 PUNTUACIÓN ESTIMADA: {estimated_score}/100")
        
        if models_added >= 4:
            print("🏆 ¡Excelente! Tienes suficientes modelos para máxima puntuación")
        elif models_added >= 3:
            print("⭐ Bien! Considera añadir un modelo más para puntuación completa")
        else:
            print("⚠️  Necesitas más modelos para mejor puntuación")
        
        return scene
    
    @staticmethod
    def quick_scene_from_directory():
        """Crear escena rápida escaneando directorio de modelos"""
        print("\n🔍 ESCANEANDO DIRECTORIO DE MODELOS")
        print("="*50)
        
        # Buscar archivos OBJ
        obj_files = []
        
        # Buscar en directorio actual
        for file in os.listdir('.'):
            if file.lower().endswith('.obj'):
                obj_files.append(file)
        
        # Buscar en subdirectorio models/
        if os.path.exists('models'):
            for file in os.listdir('models'):
                if file.lower().endswith('.obj'):
                    obj_files.append(os.path.join('models', file))
        
        if not obj_files:
            print("❌ No se encontraron archivos OBJ")
            print("💡 Asegúrate de tener archivos .obj en el directorio actual o en models/")
            return None
        
        print(f"📦 Archivos OBJ encontrados: {len(obj_files)}")
        for i, file in enumerate(obj_files, 1):
            print(f"   {i}. {file}")
        
        # Seleccionar hasta 4 modelos
        scene = Scene("Escena Rápida")
        max_models = min(4, len(obj_files))
        
        print(f"\n🎯 Seleccionando {max_models} modelos:")
        
        shaders_combinations = [
            ("displacement", "metallic"),
            ("wave", "psychedelic"),
            ("displacement", "psychedelic"),
            ("wave", "metallic")
        ]
        
        positions = [
            Vec3(-8, 0, 4),    # MUY izquierda adelante
            Vec3(8, 0, -4),    # MUY derecha atrás  
            Vec3(0, -2, -10),  # MUY al fondo
            Vec3(-2, 5, 6)     # MUY arriba adelante
        ]
        
        for i in range(max_models):
            obj_file = obj_files[i]
            
            # Buscar textura correspondiente
            texture_file = None
            base_name = os.path.splitext(os.path.basename(obj_file))[0]
            
            # Posibles extensiones de textura
            for ext in ['.png', '.jpg', '.jpeg', '.bmp']:
                for prefix in ['', 'textures/', 'texture/']:
                    potential_texture = prefix + base_name + ext
                    if os.path.exists(potential_texture):
                        texture_file = potential_texture
                        break
                if texture_file:
                    break
            
            # Crear modelo
            model_name = f"model_{i+1}"
            vertex_shader, fragment_shader = shaders_combinations[i]
            
            model = SceneModel(
                name=model_name,
                obj_file=obj_file,
                texture_file=texture_file
            ).set_transform(
                position=positions[i],
                scale=Vec3(1, 1, 1)
            ).set_shaders(vertex_shader, fragment_shader)
            
            scene.add_model(model)
            
            texture_status = "✅ con textura" if texture_file else "⚠️ sin textura"
            print(f"   {i+1}. {os.path.basename(obj_file)} - {vertex_shader}+{fragment_shader} {texture_status}")
        
        scene.camera_position = Vec3(-4, 6, 15)  # Cámara alejada para ver todo
        scene.camera_target = Vec3(0, 0, 0)
        
        print(f"\n✅ Escena rápida creada con {max_models} modelos")
        return scene
    
    @staticmethod
    def list_available_files():
        """Listar archivos disponibles para ayuda"""
        print("\n📁 ARCHIVOS DISPONIBLES EN EL SISTEMA")
        print("="*50)
        
        # Archivos OBJ
        obj_files = []
        for root, dirs, files in os.walk('.'):
            for file in files:
                if file.lower().endswith('.obj'):
                    obj_files.append(os.path.join(root, file))
        
        if obj_files:
            print(f"📦 ARCHIVOS OBJ ENCONTRADOS ({len(obj_files)}):")
            for file in sorted(obj_files):
                size = os.path.getsize(file)
                print(f"   • {file} ({size:,} bytes)")
        else:
            print("❌ No se encontraron archivos OBJ")
        
        # Archivos de textura
        texture_extensions = ['.png', '.jpg', '.jpeg', '.bmp', '.tga']
        texture_files = []
        
        for root, dirs, files in os.walk('.'):
            for file in files:
                if any(file.lower().endswith(ext) for ext in texture_extensions):
                    texture_files.append(os.path.join(root, file))
        
        if texture_files:
            print(f"\n🖼️  ARCHIVOS DE TEXTURA ENCONTRADOS ({len(texture_files)}):")
            for file in sorted(texture_files):
                size = os.path.getsize(file)
                print(f"   • {file} ({size:,} bytes)")
        else:
            print("\n❌ No se encontraron archivos de textura")
        
        # Archivos de fondo
        background_files = []
        background_extensions = ['.jpg', '.jpeg', '.png', '.bmp']
        
        # Buscar en directorio backgrounds/
        if os.path.exists('backgrounds'):
            for file in os.listdir('backgrounds'):
                if any(file.lower().endswith(ext) for ext in background_extensions):
                    background_files.append(os.path.join('backgrounds', file))
        
        # Buscar en directorio actual también
        for file in os.listdir('.'):
            if any(file.lower().endswith(ext) for ext in background_extensions):
                if 'background' in file.lower() or 'wallpaper' in file.lower() or 'sky' in file.lower():
                    background_files.append(file)
        
        if background_files:
            print(f"\n🌄 IMÁGENES DE FONDO ENCONTRADAS ({len(background_files)}):")
            for file in sorted(background_files):
                if os.path.exists(file):
                    size = os.path.getsize(file)
                    print(f"   • {file} ({size:,} bytes)")
        else:
            print("\n💡 No se encontraron imágenes de fondo")
            print("   📁 Crea carpeta 'backgrounds/' y añade imágenes .jpg/.png")
        
        print("\n💡 RECOMENDACIONES:")
        print("   • Usa modelos con al menos 100-1000 triángulos para mejor visual")
        print("   • Las texturas PNG/JPG funcionan mejor")
        print("   • Organiza archivos en carpetas models/ y textures/")
        print("   • Para fondos: carpeta backgrounds/ con imágenes panorámicas")
        print("   • Resolución recomendada para fondos: 1920x1080 o mayor")
        
        return obj_files, texture_files

    @staticmethod
    def build_automatic_scene():
        """Construir escena automática con M.obj, R.obj, Kids_Slide.obj, t.obj"""
        print("\n🎬 CONSTRUCTOR AUTOMÁTICO - ARCHIVOS PREDEFINIDOS")
        print("="*60)
        print("📝 Usando automáticamente: M.obj, R.obj, Kids_Slide.obj, t.obj")
        print("💡 Escalas ajustadas según complejidad de cada modelo")
        print("🔧 CONFIGURACIÓN AUTOMÁTICA:")
        print("   ✅ Sin preguntas interactivas")
        print("   ✅ Escalas optimizadas por número de vértices")
        print("   ✅ Posiciones balanceadas sin rotaciones complejas")
        print("   ✅ Cámara perfectamente posicionada")
        print()
        
        scene = Scene("Escena Automática Optimizada")
        
        # Configuraciones automáticas basadas en complejidad de modelos
        model_configs = [
            {
                "name": "modelo_principal",
                "description": "M.obj (7088 vértices - Complejidad media)",
                "obj_file": "M.obj",
                "position": Vec3(-10, 0, 3),  # MÁS A LA IZQUIERDA
                "rotation": Vec3(0, math.pi/6, 0),  # ROTACIÓN LIGERA (30 grados en Y)
                "scale": Vec3(0.8, 0.8, 0.8),  # ESCALA MÁS PEQUEÑA para M.obj
                "vertex_shader": "displacement",
                "fragment_shader": "metallic"
            },
            {
                "name": "modelo_secundario", 
                "description": "R.obj (51246 vértices - Muy complejo)",
                "obj_file": "R.obj",
                "position": Vec3(6, 0, -3),  # Derecha atrás
                "rotation": Vec3(0, 0, 0),  # SIN ROTACIÓN
                "scale": Vec3(0.6, 0.6, 0.6),  # Escala pequeña para 51K vértices
                "vertex_shader": "wave", 
                "fragment_shader": "psychedelic"
            },
            {
                "name": "modelo_arquitectonico",
                "description": "Kids_Slide.obj (32999 vértices - Complejo)",
                "obj_file": "Kids_Slide.obj",
                "position": Vec3(0, -5, -8),  # MÁS ABAJO (era -2, ahora -5)
                "rotation": Vec3(0, 0, 0),  # SIN ROTACIÓN
                "scale": Vec3(0.05, 0.05, 0.05),  # ESCALA MINÚSCULA para el slide
                "vertex_shader": "displacement",
                "fragment_shader": "psychedelic"
            },
            {
                "name": "modelo_decorativo",
                "description": "t.obj (2234 vértices - Simple)",
                "obj_file": "t.obj", 
                "position": Vec3(-2, 4, 5),  # Flotando arriba
                "rotation": Vec3(0, 0, 0),  # SIN ROTACIÓN
                "scale": Vec3(12.0, 12.0, 12.0),  # ESCALA MUCHO MÁS GRANDE para t.obj
                "vertex_shader": "wave",
                "fragment_shader": "metallic"
            }
        ]
        
        models_added = 0
        
        for config in model_configs:
            print(f"\n📦 CARGANDO: {config['name'].upper()}")
            print(f"📁 Archivo: {config['obj_file']}")
            print(f"📝 {config['description']}")
            print(f"📐 Escala: {config['scale'].x}x")
            print(f"📍 Posición: ({config['position'].x}, {config['position'].y}, {config['position'].z})")
            print(f"🎨 Shaders: {config['vertex_shader']} + {config['fragment_shader']}")
            
            # Verificar si el archivo existe
            if not os.path.exists(config['obj_file']):
                print(f"❌ Archivo '{config['obj_file']}' no encontrado - saltando...")
                continue
            
            print(f"✅ Archivo verificado: {config['obj_file']}")
            
            # Crear modelo sin textura (automático)
            model = SceneModel(
                name=config['name'],
                obj_file=config['obj_file'],
                texture_file=None  # Sin textura para simplificar
            ).set_transform(
                position=config['position'],
                rotation=config['rotation'],
                scale=config['scale']
            ).set_shaders(config['vertex_shader'], config['fragment_shader'])
            
            scene.add_model(model)
            models_added += 1
            
            print(f"✅ {config['name']} configurado exitosamente!")
        
        if models_added == 0:
            print("❌ No se pudo cargar ningún modelo")
            return None
        
        # Configurar cámara automáticamente
        scene.camera_position = Vec3(-8, 10, 20)  # Cámara alejada para vista completa
        scene.camera_target = Vec3(0, 2, -2)      # Enfoque al centro de la escena
        
        # Configurar imagen de fondo automáticamente
        background_file = "fondo.jpg"
        if os.path.exists(background_file):
            scene.set_background_image(background_file)
            print(f"\n🖼️  FONDO CONFIGURADO AUTOMÁTICAMENTE:")
            print(f"   📁 Imagen: {background_file}")
            print(f"   ✅ Fondo cargado exitosamente")
        else:
            print(f"\n⚠️  FONDO NO ENCONTRADO:")
            print(f"   📁 Buscando: {background_file}")
            print(f"   💡 Continuando sin imagen de fondo")
        
        print(f"\n📷 CÁMARA CONFIGURADA AUTOMÁTICAMENTE:")
        print(f"   📍 Posición: (-8, 10, 20)")
        print(f"   🎯 Target: (0, 2, -2)")
        print(f"   🎬 Vista: Panorámica optimizada")
        
        print(f"\n✅ ESCENA AUTOMÁTICA COMPLETADA:")
        print(f"   📦 Modelos cargados: {models_added}/4")
        print(f"   🎨 Shaders únicos: 4 combinaciones")
        print(f"   📐 Escalas y posiciones optimizadas:")
        print(f"      • M.obj: 0.8x (pequeño) → Pos (-10, 0, 3) + Rot 30°")
        print(f"      • R.obj: 0.6x (pequeño) → Posición (6, 0, -3)")
        print(f"      • Kids_Slide.obj: 0.05x (minúsculo) → Posición (0, -5, -8)")
        print(f"      • t.obj: 12.0x (SUPER GIGANTE) → Posición (-2, 4, 5)")
        print(f"   🔄 M.obj rotado 30° para dinamismo")
        print(f"   🖼️  Fondo: fondo.jpg (si existe)")
        
        return scene