"""
rasterizer.py
Motor de renderizado principal con pipeline de shaders
"""

import math
import numpy as np
from PIL import Image
from math_utils import Vec2, Vec3, Matrix4x4
from geometry import Camera, OBJLoader
from shader_core import ShaderUniforms, ShaderInterpolator
from vertex_shaders import *
from fragment_shaders import *

class ShaderRasterizer:
    """Rasterizador 3D con sistema de shaders programable"""
    
    def __init__(self, width=800, height=600):
        self.width = width
        self.height = height
        self.image = Image.new('RGB', (width, height), (0, 0, 0))
        self.pixels = self.image.load()
        self.z_buffer = np.full((height, width), float('inf'))
        
        # Componentes del sistema
        self.obj_loader = OBJLoader()
        self.camera = Camera(Vec3(0, 0, 5), Vec3(0, 0, 0), Vec3(0, 1, 0), 
                           fov=60, aspect=width/height)
        
        # Sistema de shaders
        self.vertex_shader = StandardVertexShader()
        self.fragment_shader = StandardFragmentShader()
        self.uniforms = ShaderUniforms()
        
        # Registro de shaders disponibles
        self.vertex_shaders = {
            "standard": StandardVertexShader(),
            "wave": WaveVertexShader(),
            
        }
        
        self.fragment_shaders = {
            "standard": StandardFragmentShader(),
            "toon": ToonFragmentShader(),
        }
    
    def get_available_shaders(self):
        """Obtener lista de shaders disponibles"""
        return {
            "vertex": list(self.vertex_shaders.keys()),
            "fragment": list(self.fragment_shaders.keys())
        }
    
    def set_shaders(self, vertex_shader_name, fragment_shader_name):
        """Cambiar los shaders activos"""
        if vertex_shader_name in self.vertex_shaders:
            self.vertex_shader = self.vertex_shaders[vertex_shader_name]
            print(f"🎨 Vertex Shader: {self.vertex_shader.name}")
        else:
            print(f"⚠️  Vertex shader '{vertex_shader_name}' no encontrado")
        
        if fragment_shader_name in self.fragment_shaders:
            self.fragment_shader = self.fragment_shaders[fragment_shader_name]
            print(f"🎨 Fragment Shader: {self.fragment_shader.name}")
        else:
            print(f"⚠️  Fragment shader '{fragment_shader_name}' no encontrado")
    
    def configure_shader_parameters(self, **params):
        """Configurar parámetros específicos de shaders"""
        for key, value in params.items():
            if hasattr(self.uniforms, key):
                setattr(self.uniforms, key, value)
                print(f"⚙️  {key} = {value}")
            else:
                print(f"⚠️  Parámetro '{key}' no reconocido")
    
    def clear_buffers(self):
        """Limpiar buffers para nuevo renderizado"""
        self.image = Image.new('RGB', (self.width, self.height), (0, 0, 0))
        self.pixels = self.image.load()
        self.z_buffer = np.full((self.height, self.width), float('inf'))
    
    def load_model(self, obj_filename, texture_filename=None):
        """Cargar modelo OBJ con textura"""
        return self.obj_loader.load_obj_with_texture(obj_filename, texture_filename)
    
    def calculate_model_bounds(self):
        """Calcular límites del modelo"""
        if not self.obj_loader.vertices:
            return Vec3(), Vec3()
        
        min_x = min(v.x for v in self.obj_loader.vertices)
        max_x = max(v.x for v in self.obj_loader.vertices)
        min_y = min(v.y for v in self.obj_loader.vertices)
        max_y = max(v.y for v in self.obj_loader.vertices)
        min_z = min(v.z for v in self.obj_loader.vertices)
        max_z = max(v.z for v in self.obj_loader.vertices)
        
        return Vec3(min_x, min_y, min_z), Vec3(max_x, max_y, max_z)
    
    def create_model_matrix(self):
        """Crear matriz de modelo (auto-centra y escala)"""
        min_bound, max_bound = self.calculate_model_bounds()
        
        # Centrar el modelo
        center_x = (min_bound.x + max_bound.x) / 2
        center_y = (min_bound.y + max_bound.y) / 2
        center_z = (min_bound.z + max_bound.z) / 2
        
        # Calcular escala apropiada
        size_x = max_bound.x - min_bound.x
        size_y = max_bound.y - min_bound.y
        size_z = max_bound.z - min_bound.z
        max_size = max(size_x, size_y, size_z)
        
        scale_factor = 2.0 / max_size if max_size > 0 else 1.0
        
        # Crear matriz de modelo
        translation_to_origin = Matrix4x4.translation(-center_x, -center_y, -center_z)
        scaling = Matrix4x4.scale(scale_factor, scale_factor, scale_factor)
        
        return scaling * translation_to_origin
    
    def setup_camera_for_shot(self, shot_type):
        """Configurar cámara para diferentes tipos de tomas"""
        distance = 5.0
        
        camera_configs = {
            "medium": (Vec3(0, 0, distance), Vec3(0, 0, 0), Vec3(0, 1, 0)),
            "low_angle": (Vec3(2, -3, distance), Vec3(0, 1, 0), Vec3(0, 1, 0)),
            "high_angle": (Vec3(-2, 4, distance), Vec3(0, -0.5, 0), Vec3(0, 1, 0)),
            "dutch": (Vec3(3, 2, distance), Vec3(0, 0, 0), Vec3(0.3, 1, 0.2)),
            "close_up": (Vec3(0, 0, distance * 0.5), Vec3(0, 0, 0), Vec3(0, 1, 0)),
            "orbit": None  # Se maneja dinámicamente
        }
        
        if shot_type == "orbit":
            # Cámara orbital animada
            angle = self.uniforms.time * 0.5
            radius = distance
            x = radius * math.cos(angle)
            z = radius * math.sin(angle)
            self.camera.position = Vec3(x, 2, z)
            self.camera.target = Vec3(0, 0, 0)
            self.camera.up = Vec3(0, 1, 0)
        elif shot_type in camera_configs:
            pos, target, up = camera_configs[shot_type]
            self.camera.position = pos
            self.camera.target = target
            self.camera.up = up
        else:
            print(f"⚠️  Tipo de toma '{shot_type}' no reconocido, usando 'medium'")
            pos, target, up = camera_configs["medium"]
            self.camera.position = pos
            self.camera.target = target
            self.camera.up = up
    
    def update_uniforms(self):
        """Actualizar variables uniformes"""
        self.uniforms.update_time()
        self.uniforms.camera_pos = self.camera.position
        
        # Actualizar matrices
        self.uniforms.model_matrix = self.create_model_matrix()
        self.uniforms.view_matrix = self.camera.get_view_matrix()
        self.uniforms.projection_matrix = self.camera.get_projection_matrix()
        self.uniforms.mvp_matrix = (self.uniforms.projection_matrix * 
                                   self.uniforms.view_matrix * 
                                   self.uniforms.model_matrix)
    
    def draw_pixel(self, x, y, z, color):
        """Dibujar pixel con z-buffer"""
        if 0 <= x < self.width and 0 <= y < self.height:
            if z < self.z_buffer[y, x]:
                self.z_buffer[y, x] = z
                self.pixels[x, y] = color
    
    def barycentric_coordinates(self, p, a, b, c):
        """Calcular coordenadas baricéntricas"""
        denom = (b.y - c.y) * (a.x - c.x) + (c.x - b.x) * (a.y - c.y)
        if abs(denom) < 1e-10:
            return None
        
        w1 = ((b.y - c.y) * (p.x - c.x) + (c.x - b.x) * (p.y - c.y)) / denom
        w2 = ((c.y - a.y) * (p.x - c.x) + (a.x - c.x) * (p.y - c.y)) / denom
        w3 = 1 - w1 - w2
        
        return w1, w2, w3
    
    def fill_triangle_with_shaders(self, v1_screen, v2_screen, v3_screen, 
                                 shader_out1, shader_out2, shader_out3):
        """Rellenar triángulo usando el pipeline de shaders"""
        # Bounding box del triángulo
        min_x = max(0, int(min(v1_screen[0], v2_screen[0], v3_screen[0])))
        max_x = min(self.width - 1, int(max(v1_screen[0], v2_screen[0], v3_screen[0])))
        min_y = max(0, int(min(v1_screen[1], v2_screen[1], v3_screen[1])))
        max_y = min(self.height - 1, int(max(v1_screen[1], v2_screen[1], v3_screen[1])))
        
        if min_x >= max_x or min_y >= max_y:
            return
        
        # Puntos del triángulo en 2D
        p1 = Vec2(v1_screen[0], v1_screen[1])
        p2 = Vec2(v2_screen[0], v2_screen[1])
        p3 = Vec2(v3_screen[0], v3_screen[1])
        
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
                    
                    # Interpolar atributos del vertex shader
                    fragment_input = ShaderInterpolator.interpolate_shader_output(
                        w1, w2, w3, shader_out1, shader_out2, shader_out3
                    )
                    fragment_input.screen_pos = Vec2(x, y)
                    
                    # Ejecutar fragment shader
                    color = self.fragment_shader.execute(fragment_input, self.uniforms, self.obj_loader)
                    
                    # Dibujar pixel
                    self.draw_pixel(x, y, z, color)
    
    def render_model(self, shot_type="medium"):
        """Renderizar modelo usando shaders"""
        if not self.obj_loader.triangles:
            print("❌ No hay triángulos para renderizar")
            return
        
        # Configurar cámara y actualizar uniforms
        self.setup_camera_for_shot(shot_type)
        self.update_uniforms()
        
        # Matriz de viewport
        viewport_matrix = Matrix4x4.viewport(0, 0, self.width, self.height)
        
        print(f"🎬 Renderizando con {self.vertex_shader.name} + {self.fragment_shader.name}...")
        triangles_rendered = 0
        triangles_clipped = 0
        
        for triangle in self.obj_loader.triangles:
            # Ejecutar vertex shader para cada vértice
            shader_out1 = self.vertex_shader.execute(triangle.v1, self.uniforms)
            shader_out2 = self.vertex_shader.execute(triangle.v2, self.uniforms)
            shader_out3 = self.vertex_shader.execute(triangle.v3, self.uniforms)
            
            # Clipping básico en espacio de clip
            w1, w2, w3 = shader_out1.w, shader_out2.w, shader_out3.w
            if (w1 <= 0 or w2 <= 0 or w3 <= 0 or
                abs(shader_out1.position.x) > abs(w1) or abs(shader_out1.position.y) > abs(w1) or
                abs(shader_out2.position.x) > abs(w2) or abs(shader_out2.position.y) > abs(w2) or
                abs(shader_out3.position.x) > abs(w3) or abs(shader_out3.position.y) > abs(w3)):
                triangles_clipped += 1
                continue
            
            # Dividir por W (perspectiva)
            v1_ndc = Vec3(shader_out1.position.x / w1, shader_out1.position.y / w1, shader_out1.position.z / w1)
            v2_ndc = Vec3(shader_out2.position.x / w2, shader_out2.position.y / w2, shader_out2.position.z / w2)
            v3_ndc = Vec3(shader_out3.position.x / w3, shader_out3.position.y / w3, shader_out3.position.z / w3)
            
            # Transformar al espacio de pantalla
            v1_screen_point, _ = viewport_matrix.transform_point(v1_ndc)
            v2_screen_point, _ = viewport_matrix.transform_point(v2_ndc)
            v3_screen_point, _ = viewport_matrix.transform_point(v3_ndc)
            
            # Convertir a tuplas con profundidad
            v1_screen = (v1_screen_point.x, v1_screen_point.y, v1_ndc.z)
            v2_screen = (v2_screen_point.x, v2_screen_point.y, v2_ndc.z)
            v3_screen = (v3_screen_point.x, v3_screen_point.y, v3_ndc.z)
            
            # Renderizar triángulo con shaders
            self.fill_triangle_with_shaders(v1_screen, v2_screen, v3_screen,
                                          shader_out1, shader_out2, shader_out3)
            triangles_rendered += 1
        
        print(f"✅ Triángulos renderizados: {triangles_rendered}")
        print(f"⚡ Triángulos clipeados: {triangles_clipped}")
    
    def save_image(self, filename):
        """Guardar imagen en el formato apropiado"""
        try:
            if filename.lower().endswith('.bmp'):
                self.image.save(filename, 'BMP')
            elif filename.lower().endswith('.png'):
                self.image.save(filename, 'PNG')
            elif filename.lower().endswith('.jpg') or filename.lower().endswith('.jpeg'):
                self.image.save(filename, 'JPEG')
            else:
                # Añadir extensión PNG por defecto
                filename = filename + '.png'
                self.image.save(filename, 'PNG')
            
            print(f"💾 Imagen guardada: {filename}")
            return True
        except Exception as e:
            print(f"❌ Error guardando imagen: {e}")
            return False
        
        def get_shader_info(self):
            """Obtener información detallada de los shaders"""
            info = {
            "current_vertex": self.vertex_shader.name,
            "current_fragment": self.fragment_shader.name,
            "available_vertex": [shader.name for shader in self.vertex_shaders.values()],
            "available_fragment": [shader.name for shader in self.fragment_shaders.values()],
            "uniforms": {
                "time": self.uniforms.time,
                "wave_frequency": self.uniforms.wave_frequency,
                "wave_amplitude": self.uniforms.wave_amplitude,
                "rim_power": self.uniforms.rim_power,
                "fresnel_power": self.uniforms.fresnel_power,
                "pulse_speed": self.uniforms.pulse_speed,
                "pulse_strength": self.uniforms.pulse_strength,
                "noise_scale": self.uniforms.noise_scale
            }
        }
        return info