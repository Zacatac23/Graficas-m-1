"""
geometry.py
Clases para geometría, vértices, triángulos y carga de modelos OBJ
"""

import math
from math_utils import Vec3, Vec2
from PIL import Image
import os

class Vertex:
    """Vértice con posición, UV y normal"""
    def __init__(self, position, uv=None, normal=None):
        self.position = position
        self.uv = uv if uv else Vec2()
        self.normal = normal if normal else Vec3(0, 0, 1)

class Triangle:
    """Triángulo formado por 3 vértices"""
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

class Camera:
    """Cámara con transformaciones de vista y proyección"""
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
        from math_utils import Matrix4x4
        return Matrix4x4.look_at(self.position, self.target, self.up)
    
    def get_projection_matrix(self):
        """Obtener matriz de proyección"""
        from math_utils import Matrix4x4
        return Matrix4x4.perspective(self.fov, self.aspect, self.near, self.far)

class OBJLoader:
    """Cargador de archivos OBJ con soporte para texturas"""
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
                if texture_filename:
                    print(f"⚠️  Archivo de textura no encontrado: {texture_filename}")
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