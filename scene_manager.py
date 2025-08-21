"""
scene_manager.py
Sistema de manejo de escenas con múltiples modelos
"""

import math
import os
from math_utils import Vec3, Matrix4x4
from geometry import OBJLoader

class SceneModel:
    """Representa un modelo individual en la escena"""
    def __init__(self, name, obj_file, texture_file=None, normal_map=None):
        self.name = name
        self.obj_file = obj_file
        self.texture_file = texture_file
        self.normal_map = normal_map
        
        # Transformaciones
        self.position = Vec3(0, 0, 0)
        self.rotation = Vec3(0, 0, 0)  # En radianes
        self.scale = Vec3(1, 1, 1)
        
        # Configuración de shaders
        self.vertex_shader = "displacement"
        self.fragment_shader = "metallic"
        
        # Loader del modelo
        self.loader = None
        self.is_loaded = False
    
    def set_transform(self, position=None, rotation=None, scale=None):
        """Configurar transformación del modelo"""
        if position:
            self.position = position
        if rotation:
            self.rotation = rotation
        if scale:
            self.scale = scale
        return self
    
    def set_shaders(self, vertex_shader, fragment_shader):
        """Configurar shaders del modelo"""
        self.vertex_shader = vertex_shader
        self.fragment_shader = fragment_shader
        return self
    
    def load(self):
        """Cargar modelo OBJ"""
        if self.is_loaded:
            return True
        
        self.loader = OBJLoader()
        success = self.loader.load_obj_with_texture(self.obj_file, self.texture_file)
        
        if success:
            self.is_loaded = True
            print(f"✅ Modelo cargado: {self.name}")
            return True
        else:
            print(f"❌ Error cargando modelo: {self.name}")
            return False
    
    def get_model_matrix(self, time=0):
        """Obtener matriz de transformación del modelo"""
        # Matrices de transformación
        translation = Matrix4x4.translation(self.position.x, self.position.y, self.position.z)
        
        rotation_x = Matrix4x4.rotation_x(self.rotation.x)
        rotation_y = Matrix4x4.rotation_y(self.rotation.y) 
        rotation_z = Matrix4x4.rotation_z(self.rotation.z)
        rotation = rotation_z * rotation_y * rotation_x
        
        scaling = Matrix4x4.scale(self.scale.x, self.scale.y, self.scale.z)
        
        # Combinar transformaciones: T * R * S
        return translation * rotation * scaling

class Scene:
    """Maneja una escena completa con múltiples modelos"""
    def __init__(self, name="Demo Scene"):
        self.name = name
        self.models = []
        self.lights = []
        self.camera_position = Vec3(0, 2, 8)
        self.camera_target = Vec3(0, 0, 0)
        self.background_color = (20, 30, 50)  # Azul oscuro
        self.background_image_path = None  # Ruta a imagen de fondo
    
    def set_background_image(self, image_path):
        """Configurar imagen de fondo"""
        self.background_image_path = image_path
        return self
    
    def add_model(self, model):
        """Añadir modelo a la escena"""
        self.models.append(model)
        print(f"📦 Modelo añadido a escena: {model.name}")
        return self
    
    def load_all_models(self):
        """Cargar todos los modelos de la escena"""
        print(f"\n🎬 CARGANDO ESCENA: {self.name}")
        print("="*50)
        
        loaded_count = 0
        for model in self.models:
            if model.load():
                loaded_count += 1
        
        print(f"\n📊 RESUMEN DE CARGA:")
        print(f"   ✅ Modelos cargados: {loaded_count}/{len(self.models)}")
        
        if loaded_count == len(self.models):
            print("   🎉 ¡Todos los modelos cargados exitosamente!")
            return True
        else:
            print("   ⚠️  Algunos modelos fallaron al cargar")
            return False
    
    def get_render_queue(self):
        """Obtener cola de renderizado ordenada"""
        # Ordenar por distancia a cámara (render back-to-front para transparencias)
        render_queue = []
        
        for model in self.models:
            if model.is_loaded:
                # Calcular distancia aproximada
                distance = (model.position - self.camera_position).length()
                render_queue.append((distance, model))
        
        # Ordenar de lejos a cerca
        render_queue.sort(key=lambda x: x[0], reverse=True)
        
        return [model for distance, model in render_queue]

class SceneBuilder:
    """Constructor de escenas predefinidas"""
    
    @staticmethod
    def create_demo_scene():
        """Crear escena de demostración con 4 modelos"""
        scene = Scene("Escena de Demostración Final")
        
        # MODELO 1: Personaje principal (complejo) - MUY A LA IZQUIERDA
        character = SceneModel(
            name="character",
            obj_file="models/character.obj",
            texture_file="textures/character.png"
        ).set_transform(
            position=Vec3(-8, 0, 4),          # MUY izquierda, adelante
            rotation=Vec3(0, math.pi/4, 0),   # Girado hacia centro
            scale=Vec3(2.0, 2.0, 2.0)        # Más grande (principal)
        ).set_shaders("displacement", "metallic")
        
        # MODELO 2: Vehículo/Máquina - MUY A LA DERECHA
        vehicle = SceneModel(
            name="vehicle", 
            obj_file="models/vehicle.obj",
            texture_file="textures/vehicle.png"
        ).set_transform(
            position=Vec3(8, 0, -4),          # MUY derecha, atrás
            rotation=Vec3(0, -math.pi/4, 0),  # Girado hacia centro
            scale=Vec3(1.6, 1.6, 1.6)
        ).set_shaders("wave", "psychedelic")
        
        # MODELO 3: Elemento arquitectónico - MUY AL FONDO
        building = SceneModel(
            name="building",
            obj_file="models/building.obj", 
            texture_file="textures/building.png"
        ).set_transform(
            position=Vec3(0, -3, -12),        # MUY al fondo, centrado
            rotation=Vec3(0, 0, 0),           # Sin rotación
            scale=Vec3(3.0, 3.0, 3.0)        # MUY grande para contexto
        ).set_shaders("displacement", "psychedelic")
        
        # MODELO 4: Objeto decorativo - MUY ARRIBA
        crystal = SceneModel(
            name="crystal",
            obj_file="models/crystal.obj",
            texture_file="textures/crystal.png" 
        ).set_transform(
            position=Vec3(-2, 6, 6),          # MUY arriba, adelante
            rotation=Vec3(math.pi/8, 0, 0),   # Ligeramente inclinado
            scale=Vec3(1.2, 1.2, 1.2)
        ).set_shaders("wave", "metallic")
        
        # Añadir modelos a escena
        scene.add_model(character)
        scene.add_model(vehicle) 
        scene.add_model(building)
        scene.add_model(crystal)
        
        # Configurar cámara para vista dramática con ángulo muy amplio
        scene.camera_position = Vec3(-6, 8, 18)  # MUY alejada y alta
        scene.camera_target = Vec3(0, 0, 0)      # Mirando al centro
        
        # Configurar imagen de fondo opcional
        # scene.set_background_image("backgrounds/space_nebula.jpg")  # Descomenta si tienes
        
        return scene
    
    @staticmethod
    def create_simple_test_scene():
        """Crear escena simple para testing"""
        scene = Scene("Escena de Prueba")
        
        # Solo 2 modelos para testing rápido
        model1 = SceneModel(
            name="test1",
            obj_file="models/cube.obj",
            texture_file="textures/test.png"
        ).set_transform(
            position=Vec3(-2, 0, 0),
            scale=Vec3(1, 1, 1)
        ).set_shaders("displacement", "metallic")
        
        model2 = SceneModel(
            name="test2", 
            obj_file="models/sphere.obj",
            texture_file="textures/test2.png"
        ).set_transform(
            position=Vec3(2, 0, 0),
            scale=Vec3(1, 1, 1)
        ).set_shaders("wave", "psychedelic")
        
        scene.add_model(model1)
        scene.add_model(model2)
        
        return scene
    
    @staticmethod
    def create_custom_scene(model_configs):
        """Crear escena personalizada desde configuración"""
        scene = Scene("Escena Personalizada")
        
        for config in model_configs:
            model = SceneModel(
                name=config.get('name', 'model'),
                obj_file=config['obj_file'],
                texture_file=config.get('texture_file'),
                normal_map=config.get('normal_map')
            )
            
            if 'position' in config:
                model.position = config['position']
            if 'rotation' in config:
                model.rotation = config['rotation'] 
            if 'scale' in config:
                model.scale = config['scale']
            if 'vertex_shader' in config:
                model.vertex_shader = config['vertex_shader']
            if 'fragment_shader' in config:
                model.fragment_shader = config['fragment_shader']
            
            scene.add_model(model)
        
        return scene

class SceneValidator:
    """Validador de escenas para asegurar puntuación completa"""
    
    @staticmethod
    def validate_scene_for_grading(scene):
        """Validar que la escena cumple requisitos de calificación"""
        print(f"\n🔍 VALIDANDO ESCENA: {scene.name}")
        print("="*50)
        
        issues = []
        warnings = []
        score_estimate = 0
        
        # Validar número de modelos (40 puntos)
        model_count = len(scene.models)
        if model_count >= 4:
            score_estimate += 40
            print(f"✅ Modelos: {model_count}/4 (40 puntos)")
        else:
            issues.append(f"Solo {model_count} modelos (necesitas 4 para 40 puntos)")
            score_estimate += model_count * 10
        
        # Validar texturas
        textured_models = sum(1 for m in scene.models if m.texture_file)
        if textured_models < len(scene.models):
            warnings.append(f"Solo {textured_models}/{len(scene.models)} modelos tienen textura")
        
        # Validar shaders únicos
        shader_combinations = set()
        for model in scene.models:
            combo = f"{model.vertex_shader}+{model.fragment_shader}"
            shader_combinations.add(combo)
        
        shader_score = min(len(shader_combinations) * 10, 40)
        score_estimate += shader_score
        print(f"✅ Combinaciones shader únicas: {len(shader_combinations)} ({shader_score} puntos)")
        
        # Validar archivos
        missing_files = []
        for model in scene.models:
            if not os.path.exists(model.obj_file):
                missing_files.append(f"OBJ: {model.obj_file}")
            if model.texture_file and not os.path.exists(model.texture_file):
                missing_files.append(f"Textura: {model.texture_file}")
        
        if missing_files:
            issues.extend(missing_files)
        
        # Mostrar resultados
        print(f"\n📊 PUNTUACIÓN ESTIMADA: {score_estimate}/100")
        
        if issues:
            print(f"\n❌ PROBLEMAS CRÍTICOS:")
            for issue in issues:
                print(f"   • {issue}")
        
        if warnings:
            print(f"\n⚠️  ADVERTENCIAS:")
            for warning in warnings:
                print(f"   • {warning}")
        
        if not issues and not warnings:
            print(f"\n🎉 ¡ESCENA PERFECTA! Lista para entregar.")
        
        return len(issues) == 0, score_estimate