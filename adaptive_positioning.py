"""
adaptive_positioning.py
Sistema de posicionamiento adaptativo basado en el tamaño real de los modelos
"""

import math
from math_utils import Vec3

class AdaptivePositioning:
    """Calcula posiciones óptimas basadas en el número de vértices de cada modelo"""
    
    @staticmethod
    def calculate_model_complexity(vertex_count):
        """Determinar complejidad del modelo basada en vértices"""
        if vertex_count < 1000:
            return "tiny"      # Muy pequeño
        elif vertex_count < 3000:
            return "small"     # Pequeño
        elif vertex_count < 10000:
            return "medium"    # Mediano
        elif vertex_count < 30000:
            return "large"     # Grande
        else:
            return "huge"      # Muy grande
    
    @staticmethod
    def get_scale_for_complexity(complexity):
        """Obtener escala apropiada según complejidad"""
        scale_map = {
            "tiny": 4.0,    # AUMENTAR MUCHO los muy pequeños
            "small": 3.0,   # AUMENTAR BASTANTE los pequeños
            "medium": 1.5,  # Aumentar moderadamente los medianos
            "large": 0.8,   # Reducir los grandes
            "huge": 0.3     # Reducir mucho los muy grandes
        }
        return scale_map.get(complexity, 1.0)
    
    @staticmethod
    def get_position_for_model(model_index, complexity, base_positions):
        """Calcular posición ajustada según complejidad"""
        base_pos = base_positions[model_index]
        
        # Ajustar distancia según tamaño del modelo
        distance_multiplier = {
            "tiny": 0.6,    # Acercar MUCHO los muy pequeños
            "small": 0.7,   # Acercar bastante los pequeños
            "medium": 1.0,  # Posición normal
            "large": 1.2,   # Alejar un poco los grandes
            "huge": 1.5     # Alejar los muy grandes
        }
        
        multiplier = distance_multiplier.get(complexity, 1.0)
        
        # Aplicar multiplicador manteniendo dirección
        adjusted_pos = Vec3(
            base_pos.x * multiplier,
            base_pos.y + (0.5 if complexity == "huge" else 0),  # Elevar los muy grandes
            base_pos.z * multiplier
        )
        
        return adjusted_pos
    
    @staticmethod
    def create_adaptive_scene_config(models_info):
        """
        Crear configuración adaptativa para una escena
        models_info: lista de diccionarios con 'name', 'vertex_count', 'obj_file', etc.
        """
        
        # Posiciones base para 4 modelos (MUY separadas y acercadas para modelos pequeños)
        base_positions = [
            Vec3(-6, 2, 4),    # Izquierda-adelante, más cerca
            Vec3(8, 1, -5),    # Derecha-atrás  
            Vec3(-3, 1.5, -8), # Centro-fondo
            Vec3(5, 2, 6)      # Derecha-adelante, más cerca
        ]
        
        # Shaders para cada posición
        shader_combinations = [
            ("displacement", "metallic"),
            ("wave", "psychedelic"),
            ("displacement", "psychedelic"),
            ("wave", "metallic")
        ]
        
        adaptive_configs = []
        
        for i, model_info in enumerate(models_info):
            if i >= 4:  # Máximo 4 modelos
                break
                
            # Determinar complejidad
            complexity = AdaptivePositioning.calculate_model_complexity(
                model_info['vertex_count']
            )
            
            # Calcular escala y posición adaptativa
            scale = AdaptivePositioning.get_scale_for_complexity(complexity)
            position = AdaptivePositioning.get_position_for_model(i, complexity, base_positions)
            
            # Rotación basada en complejidad
            rotation_map = {
                "tiny": Vec3(0, math.pi/6, 0),
                "small": Vec3(0, math.pi/4, 0),
                "medium": Vec3(0, math.pi/3, 0),
                "large": Vec3(0, math.pi/2, 0),
                "huge": Vec3(0, math.pi/8, 0)  # Rotación mínima para ver mejor
            }
            rotation = rotation_map.get(complexity, Vec3(0, 0, 0))
            
            # Configuración adaptativa
            config = {
                "name": model_info['name'],
                "obj_file": model_info['obj_file'],
                "texture_file": model_info.get('texture_file'),
                "position": position,
                "rotation": rotation,
                "scale": Vec3(scale, scale, scale),
                "vertex_shader": shader_combinations[i][0],
                "fragment_shader": shader_combinations[i][1],
                "complexity": complexity,
                "original_vertices": model_info['vertex_count']
            }
            
            adaptive_configs.append(config)
        
        return adaptive_configs
    
    @staticmethod
    def calculate_optimal_camera(model_configs):
        """Calcular posición óptima de cámara basada en los modelos"""
        
        # Encontrar límites de la escena
        min_x = min(config['position'].x - 2 for config in model_configs)
        max_x = max(config['position'].x + 2 for config in model_configs)
        min_z = min(config['position'].z - 2 for config in model_configs)
        max_z = max(config['position'].z + 2 for config in model_configs)
        
        # Centro de la escena
        center_x = (min_x + max_x) / 2
        center_z = (min_z + max_z) / 2
        
        # Tamaño de la escena
        scene_width = max_x - min_x
        scene_depth = max_z - min_z
        max_dimension = max(scene_width, scene_depth)
        
        # Calcular distancia de cámara basada en el tamaño
        # Si hay muchos modelos pequeños, acercar más la cámara
        small_model_count = sum(1 for config in model_configs if config['complexity'] in ['tiny', 'small'])
        
        if small_model_count >= 3:  # Mayoría de modelos pequeños
            camera_distance = max_dimension * 0.5 + 5  # Cámara más cerca
            camera_height = max_dimension * 0.25 + 2
        elif small_model_count >= 2:  # Algunos modelos pequeños
            camera_distance = max_dimension * 0.6 + 6
            camera_height = max_dimension * 0.3 + 3
        else:  # Modelos normales/grandes
            camera_distance = max_dimension * 0.8 + 8
            camera_height = max_dimension * 0.3 + 3
        
        # Posición de cámara
        camera_pos = Vec3(
            center_x - camera_distance * 0.3,  # Ligeramente a la izquierda
            camera_height,                      # Altura calculada
            center_z + camera_distance          # Alejada según tamaño
        )
        
        camera_target = Vec3(center_x, 1, center_z)
        
        return camera_pos, camera_target
    
    @staticmethod
    def print_adaptive_summary(model_configs):
        """Imprimir resumen de la configuración adaptativa"""
        print("\n📊 CONFIGURACIÓN ADAPTATIVA APLICADA:")
        print("="*60)
        
        for i, config in enumerate(model_configs, 1):
            vertices = config['original_vertices']
            complexity = config['complexity']
            scale = config['scale'].x
            pos = config['position']
            
            print(f"\n🎯 MODELO {i}: {config['name']}")
            print(f"   📐 Vértices: {vertices:,}")
            print(f"   📊 Complejidad: {complexity.upper()}")
            print(f"   📏 Escala aplicada: {scale:.1f}x")
            print(f"   📍 Posición: ({pos.x:+.1f}, {pos.y:+.1f}, {pos.z:+.1f})")
            print(f"   🎨 Shaders: {config['vertex_shader']} + {config['fragment_shader']}")
        
        print(f"\n🎯 ESTRATEGIA DE POSICIONAMIENTO:")
        print("   • Modelos grandes (>30k vértices): Alejados y reducidos")
        print("   • Modelos medianos (3k-10k): Posición normal")
        print("   • Modelos pequeños (<3k): Acercados y aumentados")
        print("   • Escalas automáticas para equilibrar tamaños visuales")
        
        # Calcular estadísticas
        total_vertices = sum(config['original_vertices'] for config in model_configs)
        avg_vertices = total_vertices // len(model_configs)
        
        print(f"\n📊 ESTADÍSTICAS DE LA ESCENA:")
        print(f"   • Total de vértices: {total_vertices:,}")
        print(f"   • Promedio por modelo: {avg_vertices:,}")
        print(f"   • Modelo más complejo: {max(config['original_vertices'] for config in model_configs):,} vértices")
        print(f"   • Modelo más simple: {min(config['original_vertices'] for config in model_configs):,} vértices")

# Función específica para tus modelos actuales
def create_config_for_your_models():
    """Configuración específica para los modelos que acabas de cargar"""
    
    your_models = [
        {
            "name": "juguete_principal",
            "obj_file": "M.obj",
            "vertex_count": 7088,
            "texture_file": None
        },
        {
            "name": "vehiculo_juguete", 
            "obj_file": "R.obj",
            "vertex_count": 51246,  # MUY GRANDE
            "texture_file": None
        },
        {
            "name": "juguete_construccion",
            "obj_file": "t.obj", 
            "vertex_count": 2234,   # PEQUEÑO
            "texture_file": None
        },
        {
            "name": "pelota_juguete",
            "obj_file": "SlothSword.obj",
            "vertex_count": 1970,   # PEQUEÑO
            "texture_file": None
        }
    ]
    
    return AdaptivePositioning.create_adaptive_scene_config(your_models)