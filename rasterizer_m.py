import numpy as np
import random
import math
from PIL import Image
import os

class Vec3:
    def __init__(self, x=0, y=0, z=0):
        self.x = x
        self.y = y
        self.z = z
    
    def __add__(self, other):
        return Vec3(self.x + other.x, self.y + other.y, self.z + other.z)
    
    def __sub__(self, other):
        return Vec3(self.x - other.x, self.y - other.y, self.z - other.z)
    
    def __mul__(self, scalar):
        return Vec3(self.x * scalar, self.y * scalar, self.z * scalar)
    
    def dot(self, other):
        """Producto punto entre dos vectores"""
        return self.x * other.x + self.y * other.y + self.z * other.z
    
    def cross(self, other):
        """Producto cruz entre dos vectores"""
        return Vec3(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x
        )
    
    def normalize(self):
        """Normalizar el vector"""
        length = math.sqrt(self.x**2 + self.y**2 + self.z**2)
        if length > 0:
            return Vec3(self.x / length, self.y / length, self.z / length)
        return Vec3(0, 0, 0)
    
    def length(self):
        """Longitud del vector"""
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)

class Vec2:
    def __init__(self, u=0, v=0):
        self.u = u
        self.v = v
        # Alias para compatibilidad con coordenadas 2D
        self.x = u
        self.y = v

class Vertex:
    def __init__(self, position, uv=None, normal=None):
        self.position = position
        self.uv = uv if uv else Vec2()
        self.normal = normal if normal else Vec3()

class Triangle:
    def __init__(self, v1, v2, v3):
        self.v1 = v1
        self.v2 = v2
        self.v3 = v3
        self.color = (255, 255, 255)  # Color por defecto
    
    def is_degenerate(self):
        """Verificar si el triángulo es degenerado"""
        edge1 = self.v2.position - self.v1.position
        edge2 = self.v3.position - self.v1.position
        cross = edge1.cross(edge2)
        return cross.length() < 1e-6

class Matrix4x4:
    def __init__(self, matrix=None):
        if matrix is None:
            self.m = np.eye(4)
        else:
            self.m = np.array(matrix)
    
    @staticmethod
    def translation(x, y, z):
        """Matriz de traslación"""
        matrix = np.eye(4)
        matrix[0, 3] = x
        matrix[1, 3] = y
        matrix[2, 3] = z
        return Matrix4x4(matrix)
    
    @staticmethod
    def rotation_x(angle):
        """Matriz de rotación en X"""
        c = np.cos(angle)
        s = np.sin(angle)
        matrix = np.array([
            [1, 0, 0, 0],
            [0, c, -s, 0],
            [0, s, c, 0],
            [0, 0, 0, 1]
        ])
        return Matrix4x4(matrix)
    
    @staticmethod
    def rotation_y(angle):
        """Matriz de rotación en Y"""
        c = np.cos(angle)
        s = np.sin(angle)
        matrix = np.array([
            [c, 0, s, 0],
            [0, 1, 0, 0],
            [-s, 0, c, 0],
            [0, 0, 0, 1]
        ])
        return Matrix4x4(matrix)
    
    @staticmethod
    def rotation_z(angle):
        """Matriz de rotación en Z"""
        c = np.cos(angle)
        s = np.sin(angle)
        matrix = np.array([
            [c, -s, 0, 0],
            [s, c, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ])
        return Matrix4x4(matrix)
    
    @staticmethod
    def scale(x, y, z):
        """Matriz de escala"""
        matrix = np.eye(4)
        matrix[0, 0] = x
        matrix[1, 1] = y
        matrix[2, 2] = z
        return Matrix4x4(matrix)
    
    @staticmethod
    def look_at(eye, target, up):
        """Matriz de vista (view matrix)"""
        f = (target - eye).normalize()  # forward
        s = f.cross(up).normalize()     # side
        u = s.cross(f)                  # up
        
        matrix = np.array([
            [s.x, s.y, s.z, -s.dot(eye)],
            [u.x, u.y, u.z, -u.dot(eye)],
            [-f.x, -f.y, -f.z, f.dot(eye)],
            [0, 0, 0, 1]
        ])
        return Matrix4x4(matrix)
    
    @staticmethod
    def perspective(fov, aspect, near, far):
        """Matriz de proyección perspectiva"""
        f = 1.0 / math.tan(fov / 2.0)
        matrix = np.array([
            [f / aspect, 0, 0, 0],
            [0, f, 0, 0],
            [0, 0, (far + near) / (near - far), (2 * far * near) / (near - far)],
            [0, 0, -1, 0]
        ])
        return Matrix4x4(matrix)
    
    @staticmethod
    def viewport(x, y, width, height):
        """Matriz de viewport"""
        matrix = np.array([
            [width/2, 0, 0, x + width/2],
            [0, -height/2, 0, y + height/2],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ])
        return Matrix4x4(matrix)
    
    def transform_point(self, point):
        """Transformar un punto 3D"""
        point_array = np.array([point.x, point.y, point.z, 1.0])
        transformed = self.m @ point_array
        return Vec3(transformed[0], transformed[1], transformed[2]), transformed[3]
    
    def __mul__(self, other):
        return Matrix4x4(self.m @ other.m)

class Camera:
    def __init__(self, position, target, up, fov=60, aspect=4/3, near=0.1, far=100.0):
        self.position = position
        self.target = target
        self.up = up
        self.fov = math.radians(fov)
        self.aspect = aspect
        self.near = near
        self.far = far
    
    def get_view_matrix(self):
        """Obtener matriz de vista"""
        return Matrix4x4.look_at(self.position, self.target, self.up)
    
    def get_projection_matrix(self):
        """Obtener matriz de proyección"""
        return Matrix4x4.perspective(self.fov, self.aspect, self.near, self.far)

class OBJLoader:
    def __init__(self):
        self.vertices = []
        self.triangles = []
        self.texture = None
        self.uv_coords = []
        self.normals = []
    
    def load_obj_with_texture(self, obj_filename, texture_filename=None):
        """Cargar archivo OBJ con textura"""
        vertices = []
        uv_coords = [(0, 0)]  # Índice 0 para UV por defecto
        normals = [Vec3(0, 0, 1)]  # Índice 0 para normal por defecto
        triangles = []
        
        try:
            with open(obj_filename, 'r') as file:
                for line in file:
                    line = line.strip()
                    
                    if not line or line.startswith('#'):
                        continue
                    
                    if line.startswith('v '):
                        # Parsear vértice
                        parts = line.split()
                        if len(parts) >= 4:
                            x = float(parts[1])
                            y = float(parts[2])
                            z = float(parts[3])
                            vertices.append(Vec3(x, y, z))
                    
                    elif line.startswith('vt '):
                        # Parsear coordenada de textura
                        parts = line.split()
                        if len(parts) >= 3:
                            u = float(parts[1])
                            v = float(parts[2])
                            uv_coords.append((u, v))
                    
                    elif line.startswith('vn '):
                        # Parsear normal
                        parts = line.split()
                        if len(parts) >= 4:
                            x = float(parts[1])
                            y = float(parts[2])
                            z = float(parts[3])
                            normals.append(Vec3(x, y, z))
                    
                    elif line.startswith('f '):
                        # Parsear cara
                        face_triangles = self.parse_face_with_texture(line, vertices, uv_coords, normals)
                        triangles.extend(face_triangles)
            
            # Cargar textura si se especifica
            if texture_filename and os.path.exists(texture_filename):
                try:
                    self.texture = Image.open(texture_filename).convert('RGB')
                    print(f"✅ Textura cargada: {texture_filename}")
                except Exception as e:
                    print(f"⚠️  Error cargando textura: {e}")
                    self.texture = None
            else:
                print("⚠️  Sin textura - usando colores por defecto")
                self.texture = None
            
            # Filtrar triángulos degenerados
            valid_triangles = [t for t in triangles if not t.is_degenerate()]
            
            self.vertices = vertices
            self.triangles = valid_triangles
            self.uv_coords = uv_coords
            self.normals = normals
            
            print(f"Modelo cargado exitosamente:")
            print(f"  - {len(vertices)} vértices")
            print(f"  - {len(uv_coords)-1} coordenadas UV")
            print(f"  - {len(normals)-1} normales")
            print(f"  - {len(self.triangles)} triángulos válidos")
            return True
            
        except FileNotFoundError:
            print(f"Error: No se encontró el archivo '{obj_filename}'")
            return False
        except Exception as e:
            print(f"Error al cargar archivo: {e}")
            return False
    
    def parse_face_with_texture(self, line, vertices, uv_coords, normals):
        """Parsear una cara con información de textura"""
        parts = line.split()
        if len(parts) < 4:
            return []
        
        # Parsear vértices con formato v/vt/vn
        face_vertices = []
        for i in range(1, len(parts)):
            vertex_data = parts[i].split('/')
            
            # Índice de vértice (requerido)
            v_idx = int(vertex_data[0]) - 1 if vertex_data[0] else 0
            
            # Índice de textura (opcional)
            uv_idx = 0
            if len(vertex_data) > 1 and vertex_data[1]:
                uv_idx = int(vertex_data[1]) - 1
                if uv_idx < 0 or uv_idx >= len(uv_coords):
                    uv_idx = 0
            
            # Índice de normal (opcional)
            n_idx = 0
            if len(vertex_data) > 2 and vertex_data[2]:
                n_idx = int(vertex_data[2]) - 1
                if n_idx < 0 or n_idx >= len(normals):
                    n_idx = 0
            
            if 0 <= v_idx < len(vertices):
                uv = Vec2(uv_coords[uv_idx][0], uv_coords[uv_idx][1])
                vertex = Vertex(vertices[v_idx], uv, normals[n_idx])
                face_vertices.append(vertex)
        
        # Triangular la cara
        triangles = []
        for i in range(1, len(face_vertices) - 1):
            triangle = Triangle(face_vertices[0], face_vertices[i], face_vertices[i + 1])
            triangles.append(triangle)
        
        return triangles
    
    def sample_texture(self, u, v):
        """Muestrear color de la textura en coordenadas UV"""
        if not self.texture:
            return (128, 128, 128)  # Gris por defecto
        
        # Clamp UV coordinates
        u = max(0, min(1, u))
        v = max(0, min(1, v))
        
        # Convertir a coordenadas de pixel
        x = int(u * (self.texture.width - 1))
        y = int((1 - v) * (self.texture.height - 1))  # Invertir V
        
        return self.texture.getpixel((x, y))

class BMPRasterizer:
    def __init__(self, width=800, height=600):
        self.width = width
        self.height = height
        self.image = Image.new('RGB', (width, height), (0, 0, 0))
        self.pixels = self.image.load()
        self.z_buffer = np.full((height, width), float('inf'))
        
        self.obj_loader = OBJLoader()
        self.camera = Camera(Vec3(0, 0, 5), Vec3(0, 0, 0), Vec3(0, 1, 0), 
                           fov=60, aspect=width/height)
        
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
        """Crear matriz de modelo"""
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
        
        if shot_type == "medium":
            # Medium shot - vista frontal estándar
            self.camera.position = Vec3(0, 0, distance)
            self.camera.target = Vec3(0, 0, 0)
            self.camera.up = Vec3(0, 1, 0)
        
        elif shot_type == "low_angle":
            # Low angle - cámara desde abajo mirando hacia arriba
            self.camera.position = Vec3(2, -3, distance)
            self.camera.target = Vec3(0, 1, 0)
            self.camera.up = Vec3(0, 1, 0)
        
        elif shot_type == "high_angle":
            # High angle - cámara desde arriba mirando hacia abajo
            self.camera.position = Vec3(-2, 4, distance)
            self.camera.target = Vec3(0, -0.5, 0)
            self.camera.up = Vec3(0, 1, 0)
        
        elif shot_type == "dutch":
            # Dutch angle - cámara inclinada
            self.camera.position = Vec3(3, 2, distance)
            self.camera.target = Vec3(0, 0, 0)
            self.camera.up = Vec3(0.3, 1, 0.2)  # Up vector inclinado
        
        print(f"📷 Configuración de cámara para {shot_type}:")
        print(f"   Posición: ({self.camera.position.x:.1f}, {self.camera.position.y:.1f}, {self.camera.position.z:.1f})")
        print(f"   Objetivo: ({self.camera.target.x:.1f}, {self.camera.target.y:.1f}, {self.camera.target.z:.1f})")
    
    def draw_pixel(self, x, y, z, color):
        """Dibujar pixel con z-buffer"""
        if 0 <= x < self.width and 0 <= y < self.height:
            if z < self.z_buffer[y, x]:
                self.z_buffer[y, x] = z
                self.pixels[x, y] = color
    
    def barycentric_coordinates(self, p, a, b, c):
        """Calcular coordenadas baricéntricas"""
        # Usar coordenadas x, y para cálculos 2D
        denom = (b.y - c.y) * (a.x - c.x) + (c.x - b.x) * (a.y - c.y)
        if abs(denom) < 1e-10:
            return None
        
        w1 = ((b.y - c.y) * (p.x - c.x) + (c.x - b.x) * (p.y - c.y)) / denom
        w2 = ((c.y - a.y) * (p.x - c.x) + (a.x - c.x) * (p.y - c.y)) / denom
        w3 = 1 - w1 - w2
        
        return w1, w2, w3
    
    def interpolate_attributes(self, w1, w2, w3, attr1, attr2, attr3):
        """Interpolar atributos usando coordenadas baricéntricas"""
        if hasattr(attr1, 'u'):  # Vec2 (UV)
            u = w1 * attr1.u + w2 * attr2.u + w3 * attr3.u
            v = w1 * attr1.v + w2 * attr2.v + w3 * attr3.v
            return Vec2(u, v)
        else:  # float (z)
            return w1 * attr1 + w2 * attr2 + w3 * attr3
    
    def fill_triangle_textured(self, v1_screen, v2_screen, v3_screen, v1, v2, v3):
        """Rellenar triángulo con textura usando coordenadas baricéntricas"""
        # Bounding box del triángulo
        min_x = max(0, int(min(v1_screen[0], v2_screen[0], v3_screen[0])))
        max_x = min(self.width - 1, int(max(v1_screen[0], v2_screen[0], v3_screen[0])))
        min_y = max(0, int(min(v1_screen[1], v2_screen[1], v3_screen[1])))
        max_y = min(self.height - 1, int(max(v1_screen[1], v2_screen[1], v3_screen[1])))
        
        # Verificar que el bounding box sea válido
        if min_x >= max_x or min_y >= max_y:
            return
        
        # Puntos del triángulo en 2D (usando Vec2 con alias x,y)
        p1 = Vec2(v1_screen[0], v1_screen[1])
        p2 = Vec2(v2_screen[0], v2_screen[1])
        p3 = Vec2(v3_screen[0], v3_screen[1])
        
        for y in range(min_y, max_y + 1):
            for x in range(min_x, max_x + 1):
                p = Vec2(x, y)
                
                # Calcular coordenadas baricéntricas
                bary = self.barycentric_coordinates(p, p1, p2, p3)
                if bary is None:
                    continue
                
                w1, w2, w3 = bary
                
                # Verificar que el punto está dentro del triángulo
                if w1 >= -1e-6 and w2 >= -1e-6 and w3 >= -1e-6:  # Pequeña tolerancia
                    # Interpolar profundidad
                    z = self.interpolate_attributes(w1, w2, w3, v1_screen[2], v2_screen[2], v3_screen[2])
                    
                    # Verificar z-buffer
                    if z >= self.z_buffer[y, x]:
                        continue
                    
                    # Interpolar coordenadas UV
                    uv = self.interpolate_attributes(w1, w2, w3, v1.uv, v2.uv, v3.uv)
                    
                    # Obtener color de la textura
                    color = self.obj_loader.sample_texture(uv.u, uv.v)
                    
                    # Dibujar pixel con z-buffer
                    self.draw_pixel(x, y, z, color)
    
    def render_model(self, shot_type="medium"):
        """Renderizar modelo con el tipo de toma especificado"""
        if not self.obj_loader.triangles:
            print("No hay triángulos para renderizar")
            return
        
        # Configurar cámara
        self.setup_camera_for_shot(shot_type)
        
        # Crear matrices de transformación
        model_matrix = self.create_model_matrix()
        view_matrix = self.camera.get_view_matrix()
        projection_matrix = self.camera.get_projection_matrix()
        viewport_matrix = Matrix4x4.viewport(0, 0, self.width, self.height)
        
        # Matriz MVP combinada
        mvp_matrix = projection_matrix * view_matrix * model_matrix
        
        print(f"🎬 Renderizando {len(self.obj_loader.triangles)} triángulos para toma '{shot_type}'...")
        
        triangles_rendered = 0
        
        for triangle in self.obj_loader.triangles:
            # Transformar vértices al espacio de clip
            v1_clip, w1 = mvp_matrix.transform_point(triangle.v1.position)
            v2_clip, w2 = mvp_matrix.transform_point(triangle.v2.position)
            v3_clip, w3 = mvp_matrix.transform_point(triangle.v3.position)
            
            # Clipping simple (descartar triángulos fuera del frustum)
            if (w1 <= 0 or w2 <= 0 or w3 <= 0 or
                abs(v1_clip.x) > abs(w1) or abs(v1_clip.y) > abs(w1) or
                abs(v2_clip.x) > abs(w2) or abs(v2_clip.y) > abs(w2) or
                abs(v3_clip.x) > abs(w3) or abs(v3_clip.y) > abs(w3)):
                continue
            
            # Dividir por W (perspectiva)
            v1_ndc = Vec3(v1_clip.x / w1, v1_clip.y / w1, v1_clip.z / w1)
            v2_ndc = Vec3(v2_clip.x / w2, v2_clip.y / w2, v2_clip.z / w2)
            v3_ndc = Vec3(v3_clip.x / w3, v3_clip.y / w3, v3_clip.z / w3)
            
            # Transformar al espacio de pantalla
            v1_screen_point, _ = viewport_matrix.transform_point(v1_ndc)
            v2_screen_point, _ = viewport_matrix.transform_point(v2_ndc)
            v3_screen_point, _ = viewport_matrix.transform_point(v3_ndc)
            
            # Convertir a tuplas con profundidad
            v1_screen = (v1_screen_point.x, v1_screen_point.y, v1_ndc.z)
            v2_screen = (v2_screen_point.x, v2_screen_point.y, v2_ndc.z)
            v3_screen = (v3_screen_point.x, v3_screen_point.y, v3_ndc.z)
            
            # Renderizar triángulo con textura
            self.fill_triangle_textured(v1_screen, v2_screen, v3_screen, 
                                      triangle.v1, triangle.v2, triangle.v3)
            triangles_rendered += 1
        
        print(f"✅ Triángulos renderizados: {triangles_rendered}")
    
    def save_bmp(self, filename):
        """Guardar imagen como BMP"""
        try:
            self.image.save(filename, 'BMP')
            print(f"💾 BMP guardado: {filename}")
            return True
        except Exception as e:
            print(f"❌ Error guardando BMP: {e}")
            return False
    
    def save_png(self, filename):
        """Guardar imagen como PNG"""
        try:
            self.image.save(filename, 'PNG')
            print(f"💾 PNG guardado: {filename}")
            return True
        except Exception as e:
            print(f"❌ Error guardando PNG: {e}")
            return False

def create_photoshoot(obj_filename, texture_filename=None):
    """Crear las 4 tomas requeridas del modelo"""
    print("📸 === PHOTOSHOOT 3D ===")
    print("Creando 4 tomas diferentes del modelo...")
    
    shots = [
        ("medium", "Medium Shot - Vista frontal estándar"),
        ("low_angle", "Low Angle - Cámara desde abajo"),
        ("high_angle", "High Angle - Cámara desde arriba"),
        ("dutch", "Dutch Angle - Cámara inclinada")
    ]
    
    base_name = obj_filename.replace('.obj', '')
    
    for shot_type, description in shots:
        print(f"\n🎬 Renderizando: {description}")
        
        # Crear nuevo rasterizador para cada toma
        rasterizer = BMPRasterizer(800, 600)
        
        # Cargar modelo
        if not rasterizer.load_model(obj_filename, texture_filename):
            print(f"❌ Error cargando modelo para {shot_type}")
            continue
        
        # Renderizar
        rasterizer.render_model(shot_type)
        
        # Guardar archivos
        bmp_filename = f"{base_name}_{shot_type}.bmp"
        png_filename = f"{base_name}_{shot_type}.png"
        
        rasterizer.save_bmp(bmp_filename)
        rasterizer.save_png(png_filename)
        
        print(f"✅ Toma completada: {bmp_filename}")
    
    print(f"\n🎉 PHOTOSHOOT COMPLETADO!")
    print(f"📁 Archivos generados:")
    for shot_type, _ in shots:
        print(f"   - {base_name}_{shot_type}.bmp")
        print(f"   - {base_name}_{shot_type}.png")

def main():
    print("🎨 === RENDERIZADOR 3D CON TEXTURAS Y CÁMARA PERSPECTIVA ===")
    print("\nCaracterísticas implementadas:")
    print("✅ Carga de archivos OBJ con texturas")
    print("✅ Matriz Model (centrado y escalado)")
    print("✅ Matriz View (look-at camera)")
    print("✅ Matriz Projection (perspectiva)")
    print("✅ Matriz Viewport (transformación a pantalla)")
    print("✅ Z-Buffer para profundidad")
    print("✅ Interpolación de coordenadas UV")
    print("✅ 4 tipos de tomas de cámara")
    print("\n" + "="*50)
    
    # Solicitar archivos
    obj_filename = input("📝 Nombre del archivo OBJ: ").strip()
    if not obj_filename:
        obj_filename = "model.obj"
    
    # Verificar si existe archivo de textura
    texture_filename = None
    texture_input = input("🖼️  Nombre del archivo de textura (opcional, Enter para omitir): ").strip()
    if texture_input and os.path.exists(texture_input):
        texture_filename = texture_input
    elif texture_input:
        print(f"⚠️  Archivo de textura '{texture_input}' no encontrado - continuando sin textura")
    
    print("\n🎬 OPCIONES DE RENDERIZADO:")
    print("1. Renderizar una toma específica")
    print("2. Crear photoshoot completo (4 tomas)")
    
    choice = input("\nSelecciona una opción (1 o 2): ").strip()
    
    if choice == "1":
        # Renderizar una toma específica
        print("\n📷 TIPOS DE TOMAS DISPONIBLES:")
        print("1. Medium Shot - Vista frontal estándar")
        print("2. Low Angle - Cámara desde abajo mirando hacia arriba")
        print("3. High Angle - Cámara desde arriba mirando hacia abajo")
        print("4. Dutch Angle - Cámara inclinada (efecto artístico)")
        
        shot_choice = input("\nSelecciona tipo de toma (1-4): ").strip()
        shot_types = ["medium", "low_angle", "high_angle", "dutch"]
        shot_names = ["Medium Shot", "Low Angle", "High Angle", "Dutch Angle"]
        
        if shot_choice in ["1", "2", "3", "4"]:
            shot_idx = int(shot_choice) - 1
            shot_type = shot_types[shot_idx]
            shot_name = shot_names[shot_idx]
            
            print(f"\n🎬 Renderizando: {shot_name}")
            
            # Crear rasterizador
            rasterizer = BMPRasterizer(800, 600)
            
            # Cargar modelo
            if rasterizer.load_model(obj_filename, texture_filename):
                print(f"✅ Modelo cargado exitosamente!")
                
                # Renderizar
                rasterizer.render_model(shot_type)
                
                # Guardar archivos
                base_name = obj_filename.replace('.obj', '')
                bmp_filename = f"{base_name}_{shot_type}.bmp"
                png_filename = f"{base_name}_{shot_type}.png"
                
                rasterizer.save_bmp(bmp_filename)
                rasterizer.save_png(png_filename)
                
                print(f"\n🎉 Renderizado completado!")
                print(f"📁 Archivos generados:")
                print(f"   - {bmp_filename} (BMP requerido)")
                print(f"   - {png_filename} (para visualización)")
            else:
                print("❌ Error cargando el modelo")
        else:
            print("❌ Opción inválida")
    
    elif choice == "2":
        # Crear photoshoot completo
        create_photoshoot(obj_filename, texture_filename)
    
    else:
        print("❌ Opción inválida")
    
    print("\n" + "="*50)
    print("📖 INSTRUCCIONES PARA USAR EL RENDERIZADOR:")
    print("\n1. ARCHIVOS NECESARIOS:")
    print("   - Archivo .obj con tu modelo 3D")
    print("   - Archivo de textura (opcional): .jpg, .png, .bmp")
    print("\n2. TIPOS DE TOMAS:")
    print("   🎥 Medium Shot: Vista frontal equilibrada del modelo")
    print("   🎥 Low Angle: Cámara baja mirando hacia arriba (efecto heroico)")
    print("   🎥 High Angle: Cámara alta mirando hacia abajo (efecto dominante)")
    print("   🎥 Dutch Angle: Cámara inclinada (efecto dramático/artístico)")
    print("\n3. MATRICES IMPLEMENTADAS:")
    print("   📐 Model Matrix: Centra y escala el modelo automáticamente")
    print("   📐 View Matrix: Posiciona la cámara usando look-at")
    print("   📐 Projection Matrix: Proyección perspectiva realista")
    print("   📐 Viewport Matrix: Transforma a coordenadas de pantalla")
    print("\n4. CARACTERÍSTICAS TÉCNICAS:")
    print("   🔍 Z-Buffer para manejo correcto de profundidad")
    print("   🎨 Interpolación bilinear de coordenadas UV")
    print("   🖼️  Muestreo de texturas con coordenadas UV")
    print("   ✂️  Clipping básico del frustum de vista")
    print("\n5. ARCHIVOS DE SALIDA:")
    print("   📄 .bmp - Formato requerido para la tarea")
    print("   📄 .png - Para visualización fácil")
    print("\n💡 CONSEJOS:")
    print("   - Usa modelos OBJ con coordenadas UV para mejores resultados")
    print("   - Las texturas deben estar en el mismo directorio")
    print("   - El modelo se auto-centra y escala para verse completo")
    print("   - Cada toma muestra el modelo desde un ángulo único")

if __name__ == "__main__":
    main()