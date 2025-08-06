"""
math_utils.py
Utilidades matemáticas para el renderizador 3D
"""

import math

class Vec2:
    """Vector 2D"""
    def __init__(self, x=0, y=0):
        self.x = float(x)
        self.y = float(y)
    
    def __add__(self, other):
        return Vec2(self.x + other.x, self.y + other.y)
    
    def __sub__(self, other):
        return Vec2(self.x - other.x, self.y - other.y)
    
    def __mul__(self, scalar):
        return Vec2(self.x * scalar, self.y * scalar)
    
    def dot(self, other):
        return self.x * other.x + self.y * other.y
    
    def length(self):
        return math.sqrt(self.x * self.x + self.y * self.y)
    
    def normalize(self):
        l = self.length()
        if l > 0:
            return Vec2(self.x / l, self.y / l)
        return Vec2(0, 0)

class Vec3:
    """Vector 3D"""
    def __init__(self, x=0, y=0, z=0):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)
    
    def __add__(self, other):
        return Vec3(self.x + other.x, self.y + other.y, self.z + other.z)
    
    def __sub__(self, other):
        return Vec3(self.x - other.x, self.y - other.y, self.z - other.z)
    
    def __mul__(self, scalar):
        return Vec3(self.x * scalar, self.y * scalar, self.z * scalar)
    
    def __neg__(self):
        return Vec3(-self.x, -self.y, -self.z)
    
    def dot(self, other):
        return self.x * other.x + self.y * other.y + self.z * other.z
    
    def cross(self, other):
        return Vec3(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x
        )
    
    def length(self):
        return math.sqrt(self.x * self.x + self.y * self.y + self.z * self.z)
    
    def length_squared(self):
        return self.x * self.x + self.y * self.y + self.z * self.z
    
    def normalize(self):
        l = self.length()
        if l > 0:
            return Vec3(self.x / l, self.y / l, self.z / l)
        return Vec3(0, 0, 1)  # Default normal
    
    def reflect(self, normal):
        """Reflejar vector sobre normal"""
        return self - normal * (2 * self.dot(normal))

class Matrix4x4:
    """Matriz 4x4 para transformaciones 3D"""
    def __init__(self, data=None):
        if data:
            self.m = [row[:] for row in data]  # Copia profunda
        else:
            self.m = [[0.0 for _ in range(4)] for _ in range(4)]
    
    @staticmethod
    def identity():
        """Crear matriz identidad"""
        matrix = Matrix4x4()
        for i in range(4):
            matrix.m[i][i] = 1.0
        return matrix
    
    @staticmethod
    def translation(x, y, z):
        """Crear matriz de traslación"""
        matrix = Matrix4x4.identity()
        matrix.m[0][3] = x
        matrix.m[1][3] = y
        matrix.m[2][3] = z
        return matrix
    
    @staticmethod
    def scale(x, y, z):
        """Crear matriz de escalado"""
        matrix = Matrix4x4.identity()
        matrix.m[0][0] = x
        matrix.m[1][1] = y
        matrix.m[2][2] = z
        return matrix
    
    @staticmethod
    def rotation_x(angle_rad):
        """Crear matriz de rotación en X"""
        cos_a = math.cos(angle_rad)
        sin_a = math.sin(angle_rad)
        matrix = Matrix4x4.identity()
        matrix.m[1][1] = cos_a
        matrix.m[1][2] = -sin_a
        matrix.m[2][1] = sin_a
        matrix.m[2][2] = cos_a
        return matrix
    
    @staticmethod
    def rotation_y(angle_rad):
        """Crear matriz de rotación en Y"""
        cos_a = math.cos(angle_rad)
        sin_a = math.sin(angle_rad)
        matrix = Matrix4x4.identity()
        matrix.m[0][0] = cos_a
        matrix.m[0][2] = sin_a
        matrix.m[2][0] = -sin_a
        matrix.m[2][2] = cos_a
        return matrix
    
    @staticmethod
    def rotation_z(angle_rad):
        """Crear matriz de rotación en Z"""
        cos_a = math.cos(angle_rad)
        sin_a = math.sin(angle_rad)
        matrix = Matrix4x4.identity()
        matrix.m[0][0] = cos_a
        matrix.m[0][1] = -sin_a
        matrix.m[1][0] = sin_a
        matrix.m[1][1] = cos_a
        return matrix
    
    @staticmethod
    def perspective(fov_rad, aspect, near, far):
        """Crear matriz de proyección perspectiva"""
        matrix = Matrix4x4()
        f = 1.0 / math.tan(fov_rad / 2.0)
        matrix.m[0][0] = f / aspect
        matrix.m[1][1] = f
        matrix.m[2][2] = (far + near) / (near - far)
        matrix.m[2][3] = (2 * far * near) / (near - far)
        matrix.m[3][2] = -1.0
        return matrix
    
    @staticmethod
    def look_at(eye, target, up):
        """Crear matriz de vista look-at"""
        f = (target - eye).normalize()
        s = f.cross(up).normalize()
        u = s.cross(f)
        
        matrix = Matrix4x4.identity()
        matrix.m[0][0] = s.x
        matrix.m[1][0] = s.y
        matrix.m[2][0] = s.z
        matrix.m[0][1] = u.x
        matrix.m[1][1] = u.y
        matrix.m[2][1] = u.z
        matrix.m[0][2] = -f.x
        matrix.m[1][2] = -f.y
        matrix.m[2][2] = -f.z
        matrix.m[0][3] = -s.dot(eye)
        matrix.m[1][3] = -u.dot(eye)
        matrix.m[2][3] = f.dot(eye)
        
        return matrix
    
    @staticmethod
    def viewport(x, y, width, height):
        """Crear matriz de viewport"""
        matrix = Matrix4x4.identity()
        matrix.m[0][0] = width / 2.0
        matrix.m[1][1] = -height / 2.0  # Y invertida para pantalla
        matrix.m[2][2] = 1.0
        matrix.m[0][3] = x + width / 2.0
        matrix.m[1][3] = y + height / 2.0
        return matrix
    
    def __mul__(self, other):
        """Multiplicación de matrices"""
        result = Matrix4x4()
        for i in range(4):
            for j in range(4):
                for k in range(4):
                    result.m[i][j] += self.m[i][k] * other.m[k][j]
        return result
    
    def transform_point(self, point):
        """Transformar punto 3D"""
        x = self.m[0][0] * point.x + self.m[0][1] * point.y + self.m[0][2] * point.z + self.m[0][3]
        y = self.m[1][0] * point.x + self.m[1][1] * point.y + self.m[1][2] * point.z + self.m[1][3]
        z = self.m[2][0] * point.x + self.m[2][1] * point.y + self.m[2][2] * point.z + self.m[2][3]
        w = self.m[3][0] * point.x + self.m[3][1] * point.y + self.m[3][2] * point.z + self.m[3][3]
        
        return Vec3(x, y, z), w
    
    def transform_vector(self, vector):
        """Transformar vector 3D (sin traslación)"""
        x = self.m[0][0] * vector.x + self.m[0][1] * vector.y + self.m[0][2] * vector.z
        y = self.m[1][0] * vector.x + self.m[1][1] * vector.y + self.m[1][2] * vector.z
        z = self.m[2][0] * vector.x + self.m[2][1] * vector.y + self.m[2][2] * vector.z
        
        return Vec3(x, y, z)