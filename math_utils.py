"""
math_utils.py
Clases matemáticas básicas para el renderizador 3D
"""

import math
import numpy as np

class Vec3:
    """Vector 3D con operaciones básicas"""
    def __init__(self, x=0, y=0, z=0):
        self.x = x
        self.y = y
        self.z = z
    
    def __add__(self, other):
        return Vec3(self.x + other.x, self.y + other.y, self.z + other.z)
    
    def __sub__(self, other):
        return Vec3(self.x - other.x, self.y - other.y, self.z - other.z)
    
    def __mul__(self, scalar):
        if isinstance(scalar, (int, float)):
            return Vec3(self.x * scalar, self.y * scalar, self.z * scalar)
        return Vec3(self.x * scalar.x, self.y * scalar.y, self.z * scalar.z)
    
    def __str__(self):
        return f"Vec3({self.x:.2f}, {self.y:.2f}, {self.z:.2f})"
    
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
    """Vector 2D para coordenadas UV y de pantalla"""
    def __init__(self, u=0, v=0):
        self.u = u
        self.v = v
        # Alias para compatibilidad con coordenadas 2D
        self.x = u
        self.y = v
    
    def __str__(self):
        return f"Vec2({self.u:.2f}, {self.v:.2f})"

class Matrix4x4:
    """Matriz 4x4 para transformaciones 3D"""
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