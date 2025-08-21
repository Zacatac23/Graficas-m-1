"""
multi_model_rasterizer.py
Extensión del rasterizador para manejar múltiples modelos en una escena
"""

import math
import os
import numpy as np
from PIL import Image
from math_utils import Vec2, Vec3, Matrix4x4
from geometry import Camera
from shader_core import ShaderUniforms, ShaderInterpolator
from scene_manager import Scene, SceneModel

# Importar shaders existentes
from vertex_shaders import DisplacementVertexShader, WaveVertexShader
from fragment_shaders import MetallicFragmentShader, PsychedelicFragmentShader

class MultiModelRasterizer:
    """Rasterizador extendido para escenas con múltiples modelos"""
    
    def __init__(self, width=800, height=600):
        self.width = width
        self.height = height
        self.image = Image.new('RGB', (width, height), (0, 0, 0))
        self.pixels = self.image.load()
        self.z_buffer = np.full((height, width), float('inf'))
        
        # Sistema de cámara
        self.camera = Camera(Vec3(0, 0, 5), Vec3(0, 0, 0), Vec3(0, 1, 0), 
                           fov=60, aspect=width/height)
        
        # Sistema de shaders
        self.vertex_shaders = {
            "displacement": DisplacementVertexShader(),
            "wave": WaveVertexShader()
        }
        
        self.fragment_shaders = {
            "metallic": MetallicFragmentShader(),
            "psychedelic": PsychedelicFragmentShader()
        }
        
        # Uniforms globales
        self.uniforms = ShaderUniforms()
        
        # Escena actual
        self.current_scene = None
        
        # Sistema de imagen de fondo
        self.background_image = None
        self.background_pixels = None
        
        # Estadísticas de renderizado
        self.stats = {
            'triangles_rendered': 0,
            'triangles_clipped': 0,
            'models_rendered': 0
        }
    
    def load_background_image(self, background_path):
        """Cargar imagen de fondo"""
        try:
            if background_path and os.path.exists(background_path):
                # Cargar y redimensionar imagen de fondo
                self.background_image = Image.open(background_path).convert('RGB')
                self.background_image = self.background_image.resize((self.width, self.height), Image.Resampling.LANCZOS)
                self.background_pixels = self.background_image.load()
                print(f"✅ Imagen de fondo cargada: {background_path}")
                return True
            else:
                print(f"⚠️  Imagen de fondo '{background_path}' no encontrada")
                self.background_image = None
                self.background_pixels = None
                return False
        except Exception as e:
            print(f"❌ Error cargando imagen de fondo: {e}")
            self.background_image = None
            self.background_pixels = None
            return False
    
    def get_background_color(self, x, y):
        """Obtener color de fondo en coordenadas específicas"""
        if self.background_pixels and 0 <= x < self.width and 0 <= y < self.height:
            return self.background_pixels[x, y]
        elif self.current_scene:
            return self.current_scene.background_color
        else:
            return (0, 0, 0)  # Negro por defecto
    def load_scene(self, scene):
        """Cargar una escena completa"""
        print(f"\n🎬 CARGANDO ESCENA: {scene.name}")
        
        self.current_scene = scene
        
        # Cargar imagen de fondo si está especificada
        if hasattr(scene, 'background_image_path') and scene.background_image_path:
            self.load_background_image(scene.background_image_path)
        
        # Cargar todos los modelos
        success = scene.load_all_models()
        
        if success:
            # Configurar cámara desde la escena
            self.camera.position = scene.camera_position
            self.camera.target = scene.camera_target
            
            print(f"📷 Cámara configurada: pos={scene.camera_position.x:.1f},{scene.camera_position.y:.1f},{scene.camera_position.z:.1f}")
            return True
        else:
            print("❌ Error cargando escena")
            return False
    
    def clear_buffers(self, background_color=None):
        """Limpiar buffers para nuevo renderizado con imagen de fondo"""
        # Si hay imagen de fondo, usarla como base
        if self.background_image:
            self.image = self.background_image.copy()
            self.pixels = self.image.load()
            print("🖼️  Usando imagen de fondo")
        else:
            # Usar color de fondo sólido
            if background_color is None and self.current_scene:
                background_color = self.current_scene.background_color
            if background_color is None:
                background_color = (0, 0, 0)
            
            self.image = Image.new('RGB', (self.width, self.height), background_color)
            self.pixels = self.image.load()
        
        # Limpiar z-buffer
        self.z_buffer = np.full((self.height, self.width), float('inf'))
        
        # Resetear estadísticas
        self.stats = {
            'triangles_rendered': 0,
            'triangles_clipped': 0,
            'models_rendered': 0
        }
    
    def update_global_uniforms(self):
        """Actualizar uniforms globales de la escena"""
        self.uniforms.update_time()
        self.uniforms.camera_pos = self.camera.position
        
        # Matrices de vista y proyección globales
        self.uniforms.view_matrix = self.camera.get_view_matrix()
        self.uniforms.projection_matrix = self.camera.get_projection_matrix()
    
    def render_model(self, model, time_override=None):
        """Renderizar un modelo específico"""
        if not model.is_loaded:
            print(f"⚠️  Modelo {model.name} no está cargado")
            return False
        
        # Configurar shaders específicos del modelo
        if model.vertex_shader not in self.vertex_shaders:
            print(f"⚠️  Vertex shader '{model.vertex_shader}' no encontrado para {model.name}")
            return False
        
        if model.fragment_shader not in self.fragment_shaders:
            print(f"⚠️  Fragment shader '{model.fragment_shader}' no encontrado para {model.name}")
            return False
        
        vertex_shader = self.vertex_shaders[model.vertex_shader]
        fragment_shader = self.fragment_shaders[model.fragment_shader]
        
        # Configurar matriz de modelo específica para este modelo
        current_time = time_override if time_override is not None else self.uniforms.time
        base_matrix = model.get_model_matrix(current_time)
        
        # Aplicar animación especial para algunos modelos
        animated_model_matrix = self.apply_model_animation(model, base_matrix, current_time)
        
        self.uniforms.model_matrix = animated_model_matrix
        self.uniforms.mvp_matrix = (self.uniforms.projection_matrix * 
                                   self.uniforms.view_matrix * 
                                   self.uniforms.model_matrix)
        
        # Renderizar triángulos del modelo
        triangles_rendered = self.render_triangles(
            model.loader.triangles, 
            vertex_shader, 
            fragment_shader,
            model.loader
        )
        
        print(f"  📐 {model.name}: {triangles_rendered} triángulos")
        self.stats['models_rendered'] += 1
        
        return True
    
    def apply_model_animation(self, model, base_matrix, time):
        """Aplicar animaciones específicas a la matriz del modelo"""
        # Animaciones especiales por nombre/tipo
        if model.name == "crystal" or "crystal" in model.name.lower():
            # Rotación continua para cristal
            rotation_speed = 1.0
            animated_rotation = Matrix4x4.rotation_y(time * rotation_speed)
            # Movimiento vertical sutil
            hover_offset = math.sin(time * 1.5) * 0.2
            hover_matrix = Matrix4x4.translation(0, hover_offset, 0)
            return hover_matrix * base_matrix * animated_rotation
        
        elif (model.name == "vehicle" or "vehicle" in model.name.lower() or 
              "car" in model.name.lower() or "ship" in model.name.lower()):
            # Movimiento sutil para vehículos con shader psicodélico
            if model.fragment_shader == "psychedelic":
                hover_offset = math.sin(time * 2.0) * 0.15
                hover_matrix = Matrix4x4.translation(0, hover_offset, 0)
                return hover_matrix * base_matrix
        
        elif "decorativ" in model.name.lower() or model.name == "modelo_decorativo":
            # Rotación y oscilación para objetos decorativos
            rotation_y = Matrix4x4.rotation_y(time * 0.8)
            rotation_x = Matrix4x4.rotation_x(math.sin(time * 1.2) * 0.1)
            return base_matrix * rotation_y * rotation_x
        
        return base_matrix
    
    def render_triangles(self, triangles, vertex_shader, fragment_shader, geometry_data):
        """Renderizar lista de triángulos con shaders específicos"""
        viewport_matrix = Matrix4x4.viewport(0, 0, self.width, self.height)
        triangles_rendered = 0
        
        for triangle in triangles:
            # Ejecutar vertex shader
            shader_out1 = vertex_shader.execute(triangle.v1, self.uniforms)
            shader_out2 = vertex_shader.execute(triangle.v2, self.uniforms)
            shader_out3 = vertex_shader.execute(triangle.v3, self.uniforms)
            
            # Clipping básico
            w1, w2, w3 = shader_out1.w, shader_out2.w, shader_out3.w
            if (w1 <= 0 or w2 <= 0 or w3 <= 0):
                self.stats['triangles_clipped'] += 1
                continue
            
            # Verificar si está en frustum
            if self.is_triangle_clipped(shader_out1, shader_out2, shader_out3):
                self.stats['triangles_clipped'] += 1
                continue
            
            # Transformar a espacio de pantalla
            try:
                # Dividir por W
                v1_ndc = Vec3(shader_out1.position.x / w1, shader_out1.position.y / w1, shader_out1.position.z / w1)
                v2_ndc = Vec3(shader_out2.position.x / w2, shader_out2.position.y / w2, shader_out2.position.z / w2)
                v3_ndc = Vec3(shader_out3.position.x / w3, shader_out3.position.y / w3, shader_out3.position.z / w3)
                
                # Viewport
                v1_screen_point, _ = viewport_matrix.transform_point(v1_ndc)
                v2_screen_point, _ = viewport_matrix.transform_point(v2_ndc)
                v3_screen_point, _ = viewport_matrix.transform_point(v3_ndc)
                
                # Convertir a coordenadas de pantalla
                v1_screen = (v1_screen_point.x, v1_screen_point.y, v1_ndc.z)
                v2_screen = (v2_screen_point.x, v2_screen_point.y, v2_ndc.z)
                v3_screen = (v3_screen_point.x, v3_screen_point.y, v3_ndc.z)
                
                # Rasterizar triángulo
                self.fill_triangle_with_shaders(
                    v1_screen, v2_screen, v3_screen,
                    shader_out1, shader_out2, shader_out3,
                    fragment_shader, geometry_data
                )
                
                triangles_rendered += 1
                self.stats['triangles_rendered'] += 1
                
            except Exception as e:
                # Skip triángulos problemáticos
                continue
        
        return triangles_rendered
    
    def is_triangle_clipped(self, out1, out2, out3):
        """Verificar si triángulo debe ser clipeado"""
        # Clipping contra frustum
        for out in [out1, out2, out3]:
            w = abs(out.w)
            if (abs(out.position.x) > w * 1.5 or 
                abs(out.position.y) > w * 1.5 or 
                out.position.z < -w or 
                out.position.z > w):
                return True
        return False
    
    def render_scene(self):
        """Renderizar escena completa"""
        if not self.current_scene:
            print("❌ No hay escena cargada")
            return False
        
        print(f"\n🎬 RENDERIZANDO ESCENA: {self.current_scene.name}")
        print("="*60)
        
        # Limpiar buffers
        self.clear_buffers()
        
        # Actualizar uniforms globales
        self.update_global_uniforms()
        
        # Obtener cola de renderizado ordenada
        render_queue = self.current_scene.get_render_queue()
        
        print(f"📋 Cola de renderizado: {len(render_queue)} modelos")
        
        # Renderizar cada modelo
        for i, model in enumerate(render_queue, 1):
            print(f"\n🎨 Renderizando {i}/{len(render_queue)}: {model.name}")
            print(f"   Shaders: {model.vertex_shader} + {model.fragment_shader}")
            
            success = self.render_model(model)
            if not success:
                print(f"   ❌ Error renderizando {model.name}")
        
        # Mostrar estadísticas finales
        self.print_render_stats()
        
        return True
    
    def print_render_stats(self):
        """Imprimir estadísticas de renderizado"""
        print(f"\n📊 ESTADÍSTICAS DE RENDERIZADO:")
        print(f"   ✅ Modelos renderizados: {self.stats['models_rendered']}")
        print(f"   📐 Triángulos renderizados: {self.stats['triangles_rendered']}")
        print(f"   ✂️  Triángulos clipeados: {self.stats['triangles_clipped']}")
        total_triangles = self.stats['triangles_rendered'] + self.stats['triangles_clipped']
        if total_triangles > 0:
            efficiency = (self.stats['triangles_rendered'] / total_triangles) * 100
            print(f"   ⚡ Eficiencia: {efficiency:.1f}%")
    
    def fill_triangle_with_shaders(self, v1_screen, v2_screen, v3_screen, 
                                 shader_out1, shader_out2, shader_out3,
                                 fragment_shader, geometry_data):
        """Rellenar triángulo usando shaders específicos"""
        # Bounding box
        min_x = max(0, int(min(v1_screen[0], v2_screen[0], v3_screen[0])))
        max_x = min(self.width - 1, int(max(v1_screen[0], v2_screen[0], v3_screen[0])))
        min_y = max(0, int(min(v1_screen[1], v2_screen[1], v3_screen[1])))
        max_y = min(self.height - 1, int(max(v1_screen[1], v2_screen[1], v3_screen[1])))
        
        if min_x >= max_x or min_y >= max_y:
            return
        
        # Puntos del triángulo
        p1 = Vec2(v1_screen[0], v1_screen[1])
        p2 = Vec2(v2_screen[0], v2_screen[1])
        p3 = Vec2(v3_screen[0], v3_screen[1])
        
        # Rasterización
        for y in range(min_y, max_y + 1):
            for x in range(min_x, max_x + 1):
                p = Vec2(x, y)
                
                # Coordenadas baricéntricas
                bary = self.barycentric_coordinates(p, p1, p2, p3)
                if bary is None:
                    continue
                
                w1, w2, w3 = bary
                
                if w1 >= -1e-6 and w2 >= -1e-6 and w3 >= -1e-6:
                    # Interpolar profundidad
                    z = w1 * v1_screen[2] + w2 * v2_screen[2] + w3 * v3_screen[2]
                    
                    if z >= self.z_buffer[y, x]:
                        continue
                    
                    # Interpolar atributos
                    fragment_input = ShaderInterpolator.interpolate_shader_output(
                        w1, w2, w3, shader_out1, shader_out2, shader_out3
                    )
                    fragment_input.screen_pos = Vec2(x, y)
                    
                    # Ejecutar fragment shader
                    color = fragment_shader.execute(fragment_input, self.uniforms, geometry_data)
                    
                    # Dibujar pixel
                    self.draw_pixel(x, y, z, color)
    
    def barycentric_coordinates(self, p, a, b, c):
        """Calcular coordenadas baricéntricas"""
        denom = (b.y - c.y) * (a.x - c.x) + (c.x - b.x) * (a.y - c.y)
        if abs(denom) < 1e-10:
            return None
        
        w1 = ((b.y - c.y) * (p.x - c.x) + (c.x - b.x) * (p.y - c.y)) / denom
        w2 = ((c.y - a.y) * (p.x - c.x) + (a.x - c.x) * (p.y - c.y)) / denom
        w3 = 1 - w1 - w2
        
        return w1, w2, w3
    
    def draw_pixel(self, x, y, z, color):
        """Dibujar pixel con z-buffer"""
        if 0 <= x < self.width and 0 <= y < self.height:
            if z < self.z_buffer[y, x]:
                self.z_buffer[y, x] = z
                self.pixels[x, y] = color
    
    def save_image(self, filename):
        """Guardar imagen renderizada"""
        try:
            if not filename.lower().endswith(('.bmp', '.png', '.jpg', '.jpeg')):
                filename += '.bmp'  # Formato requerido por el proyecto
            
            if filename.lower().endswith('.bmp'):
                self.image.save(filename, 'BMP')
            elif filename.lower().endswith('.png'):
                self.image.save(filename, 'PNG')
            else:
                self.image.save(filename, 'JPEG')
            
            print(f"💾 Imagen guardada: {filename}")
            return True
        except Exception as e:
            print(f"❌ Error guardando imagen: {e}")
            return False
    
    def configure_camera(self, position=None, target=None, fov=None):
        """Configurar cámara manualmente"""
        if position:
            self.camera.position = position
        if target:
            self.camera.target = target
        if fov:
            self.camera.fov = math.radians(fov)
    
    def get_available_shaders(self):
        """Obtener shaders disponibles"""
        return {
            "vertex": list(self.vertex_shaders.keys()),
            "fragment": list(self.fragment_shaders.keys())
        }