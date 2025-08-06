"""
geometry.py
Clases para geometría, cámara y carga de modelos OBJ
"""

import math
import os
from PIL import Image
from math_utils import Vec2, Vec3, Matrix4x4

class Vertex:
    """Representa un vértice con posición, normal y coordenadas UV"""
    def __init__(self, position=None, normal=None, uv=None):
        self.position = position or Vec3(0, 0, 0)
        self.normal = normal or Vec3(0, 1, 0)
        self.uv = uv or Vec2(0, 0)

class Triangle:
    """Representa un triángulo con tres vértices"""
    def __init__(self, v1, v2, v3):
        self.v1 = v1
        self.v2 = v2
        self.v3 = v3

class Camera:
    """Cámara 3D con transformaciones de vista y proyección"""
    
    def __init__(self, position, target, up, fov=60, aspect=16/9, near=0.1, far=100):
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
        """Obtener matriz de proyección perspectiva"""
        return Matrix4x4.perspective(self.fov, self.aspect, self.near, self.far)

class OBJLoader:
    """Cargador de archivos OBJ con soporte para texturas"""
    
    def __init__(self):
        self.vertices = []
        self.normals = []
        self.uvs = []
        self.triangles = []
        self.texture = None
    
    def load_obj_with_texture(self, obj_filename, texture_filename=None):
        """Cargar archivo OBJ y textura opcional"""
        try:
            # Cargar textura si se proporciona
            if texture_filename and os.path.exists(texture_filename):
                self.texture = Image.open(texture_filename).convert('RGB')
                print(f"✅ Textura cargada: {texture_filename} ({self.texture.size[0]}x{self.texture.size[1]})")
            
            # Cargar archivo OBJ
            return self.load_obj(obj_filename)
        
        except Exception as e:
            print(f"❌ Error cargando modelo: {e}")
            return False
    
    def load_obj(self, filename):
        """Cargar archivo OBJ"""
        if not os.path.exists(filename):
            print(f"❌ Archivo no encontrado: {filename}")
            return False
        
        # Limpiar datos anteriores
        self.vertices.clear()
        self.normals.clear()
        self.uvs.clear()
        self.triangles.clear()
        
        # Listas temporales para parseo
        temp_vertices = []
        temp_normals = []
        temp_uvs = []
        
        try:
            with open(filename, 'r') as file:
                for line in file:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    
                    parts = line.split()
                    if not parts:
                        continue
                    
                    # Vértices
                    if parts[0] == 'v':
                        x = float(parts[1])
                        y = float(parts[2])
                        z = float(parts[3])
                        temp_vertices.append(Vec3(x, y, z))
                    
                    # Coordenadas de textura
                    elif parts[0] == 'vt':
                        u = float(parts[1])
                        v = float(parts[2]) if len(parts) > 2 else 0.0
                        temp_uvs.append(Vec2(u, v))
                    
                    # Normales
                    elif parts[0] == 'vn':
                        x = float(parts[1])
                        y = float(parts[2])
                        z = float(parts[3])
                        temp_normals.append(Vec3(x, y, z).normalize())
                    
                    # Caras (triángulos)
                    elif parts[0] == 'f':
                        # Manejar diferentes formatos de caras
                        vertices_data = []
                        for i in range(1, len(parts)):
                            vertex_data = parts[i].split('/')
                            v_idx = int(vertex_data[0]) - 1  # OBJ usa índices 1-based
                            uv_idx = int(vertex_data[1]) - 1 if len(vertex_data) > 1 and vertex_data[1] else 0
                            n_idx = int(vertex_data[2]) - 1 if len(vertex_data) > 2 and vertex_data[2] else 0
                            
                            vertices_data.append((v_idx, uv_idx, n_idx))
                        
                        # Triangular caras (si tiene más de 3 vértices)
                        for i in range(1, len(vertices_data) - 1):
                            self.create_triangle(
                                vertices_data[0], vertices_data[i], vertices_data[i + 1],
                                temp_vertices, temp_uvs, temp_normals
                            )
            
            # Almacenar vértices finales
            self.vertices = temp_vertices.copy()
            self.uvs = temp_uvs.copy()
            self.normals = temp_normals.copy()
            
            print(f"✅ Modelo OBJ cargado: {filename}")
            print(f"   📊 Vértices: {len(temp_vertices)}")
            print(f"   📊 Triángulos: {len(self.triangles)}")
            print(f"   📊 UVs: {len(temp_uvs)}")
            print(f"   📊 Normales: {len(temp_normals)}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error parseando OBJ: {e}")
            return False
    
    def create_triangle(self, v1_data, v2_data, v3_data, temp_vertices, temp_uvs, temp_normals):
        """Crear triángulo a partir de índices"""
        try:
            # Obtener datos del primer vértice
            v1_pos = temp_vertices[v1_data[0]] if v1_data[0] < len(temp_vertices) else Vec3()
            v1_uv = temp_uvs[v1_data[1]] if v1_data[1] < len(temp_uvs) and v1_data[1] >= 0 else Vec2()
            v1_normal = temp_normals[v1_data[2]] if v1_data[2] < len(temp_normals) and v1_data[2] >= 0 else Vec3(0, 1, 0)
            
            # Obtener datos del segundo vértice
            v2_pos = temp_vertices[v2_data[0]] if v2_data[0] < len(temp_vertices) else Vec3()
            v2_uv = temp_uvs[v2_data[1]] if v2_data[1] < len(temp_uvs) and v2_data[1] >= 0 else Vec2()
            v2_normal = temp_normals[v2_data[2]] if v2_data[2] < len(temp_normals) and v2_data[2] >= 0 else Vec3(0, 1, 0)
            
            # Obtener datos del tercer vértice
            v3_pos = temp_vertices[v3_data[0]] if v3_data[0] < len(temp_vertices) else Vec3()
            v3_uv = temp_uvs[v3_data[1]] if v3_data[1] < len(temp_uvs) and v3_data[1] >= 0 else Vec2()
            v3_normal = temp_normals[v3_data[2]] if v3_data[2] < len(temp_normals) and v3_data[2] >= 0 else Vec3(0, 1, 0)
            
            # Crear vértices
            vertex1 = Vertex(v1_pos, v1_normal, v1_uv)
            vertex2 = Vertex(v2_pos, v2_normal, v2_uv)
            vertex3 = Vertex(v3_pos, v3_normal, v3_uv)
            
            # Crear triángulo
            triangle = Triangle(vertex1, vertex2, vertex3)
            self.triangles.append(triangle)
            
        except Exception as e:
            print(f"⚠️  Error creando triángulo: {e}")
    
    def get_texture_color(self, u, v):
        """Obtener color de textura en coordenadas UV"""
        if not self.texture:
            return (255, 255, 255)
        
        # Asegurar que las coordenadas estén en rango [0,1]
        u = u % 1.0
        v = v % 1.0
        
        # Convertir a coordenadas de pixel
        x = int(u * (self.texture.size[0] - 1))
        y = int((1.0 - v) * (self.texture.size[1] - 1))  # Invertir V
        
        # Obtener color
        try:
            return self.texture.getpixel((x, y))
        except:
            return (255, 255, 255)
    
    def calculate_bounds(self):
        """Calcular límites del modelo"""
        if not self.vertices:
            return Vec3(), Vec3()
        
        min_x = min(v.x for v in self.vertices)
        max_x = max(v.x for v in self.vertices)
        min_y = min(v.y for v in self.vertices)
        max_y = max(v.y for v in self.vertices)
        min_z = min(v.z for v in self.vertices)
        max_z = max(v.z for v in self.vertices)
        
        return Vec3(min_x, min_y, min_z), Vec3(max_x, max_y, max_z)