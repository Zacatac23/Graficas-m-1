import numpy as np
from intercept import Intercept

class Shape(object):
    def __init__(self, position, material):
        self.position = position
        self.material = material
        self.type = "None"

    def ray_intersect(self, orig, dir):
        return None

class Sphere(Shape):
    def __init__(self, position, radius, material):
        super().__init__(position, material)
        self.radius = radius
        self.type = "Sphere"
    
    def ray_intersect(self, orig, dir):
        # Asegurarse de trabajar con numpy arrays
        orig = np.array(orig, dtype=float)
        dir = np.array(dir, dtype=float)

        # Vector desde el origen del rayo hasta el centro de la esfera
        dir_length = np.linalg.norm(dir)
        if dir_length == 0:
            return None
        dir = dir / dir_length  # Normalizar la dirección del rayo

        # Vector del origen del rayo al centro de la esfera
        origin_to_center = np.array(self.position, dtype=float) - orig

        # Proyeccion de que tan lejos esta el punto mas cercano del rayo al centro
        projection_distance = np.dot(origin_to_center, dir)

        # Distancia perpendicular al cuadrado (usando pitagoras)
        perpendicular_distance_squared = np.dot(origin_to_center, origin_to_center) - projection_distance ** 2
        radius_squared = self.radius * self.radius

        # Si el rayo pasa mas lejos que el radio, no hay interseccion
        if perpendicular_distance_squared > radius_squared:
            return None
        
        # Distancia desde el punto de proyeccion hasta las intersecciones
        half_chord_distance = np.sqrt(radius_squared - perpendicular_distance_squared)

        # Las 2 distancias de interseccion
        near_distance = projection_distance - half_chord_distance
        far_distance = projection_distance + half_chord_distance

        # Elegir la interseccion mas cercana que este adelante del origen
        epsilon = 1e-6
        if near_distance > epsilon:
            # Calcular punto de impacto y normal
            hit_point = orig + dir * near_distance
            normal = (hit_point - np.array(self.position)) / self.radius
            # Devolver Intercept con toda la info
            return Intercept(hit_point, normal, near_distance, dir, self)
    
        if far_distance > epsilon:
            # Lo mismo para la intersección lejana
            hit_point = orig + dir * far_distance
            normal = (hit_point - np.array(self.position)) / self.radius
            return Intercept(hit_point, normal, far_distance, dir, self)
        
        # Ambas están detrás del origen
        return None

class Plane(Shape):
    def __init__(self, position, normal, material):
        super().__init__(position, material)
        self.normal = np.array(normal, dtype=float)
        self.normal = self.normal / np.linalg.norm(self.normal)  # Normalizar
        self.type = "Plane"
    
    def ray_intersect(self, orig, dir):
        orig = np.array(orig, dtype=float)
        dir = np.array(dir, dtype=float)
        
        # Normalizar dirección
        dir_length = np.linalg.norm(dir)
        if dir_length == 0:
            return None
        dir = dir / dir_length
        
        # Verificar si el rayo es paralelo al plano
        denom = np.dot(dir, self.normal)
        if abs(denom) < 1e-6:
            return None
        
        # Calcular distancia al plano
        plane_point = np.array(self.position, dtype=float)
        t = np.dot((plane_point - orig), self.normal) / denom
        
        # Verificar que la intersección esté adelante del origen
        if t < 1e-6:
            return None
        
        # Calcular punto de intersección
        hit_point = orig + t * dir
        
        # La normal apunta hacia el lado desde el que viene el rayo
        normal = self.normal if denom < 0 else -self.normal
        
        return Intercept(hit_point, normal, t, dir, self)

class Disk(Shape):
    def __init__(self, position, normal, radius, material):
        super().__init__(position, material)
        self.normal = np.array(normal, dtype=float)
        self.normal = self.normal / np.linalg.norm(self.normal)
        self.radius = radius
        self.type = "Disk"
    
    def ray_intersect(self, orig, dir):
        orig = np.array(orig, dtype=float)
        dir = np.array(dir, dtype=float)
        
        # Normalizar dirección
        dir_length = np.linalg.norm(dir)
        if dir_length == 0:
            return None
        dir = dir / dir_length
        
        # Verificar intersección con el plano del disco
        denom = np.dot(dir, self.normal)
        if abs(denom) < 1e-6:
            return None
        
        plane_point = np.array(self.position, dtype=float)
        t = np.dot((plane_point - orig), self.normal) / denom
        
        if t < 1e-6:
            return None
        
        # Calcular punto de intersección
        hit_point = orig + t * dir
        
        # Verificar si el punto está dentro del radio del disco
        distance_from_center = np.linalg.norm(hit_point - plane_point)
        if distance_from_center > self.radius:
            return None
        
        # La normal apunta hacia el lado desde el que viene el rayo
        normal = self.normal if denom < 0 else -self.normal
        
        return Intercept(hit_point, normal, t, dir, self)

class Triangle(Shape):
    def __init__(self, v0, v1, v2, material):
        # Posición es el centroide del triángulo
        super().__init__([(v0[i] + v1[i] + v2[i])/3 for i in range(3)], material)
        self.v0 = np.array(v0, dtype=float)
        self.v1 = np.array(v1, dtype=float)
        self.v2 = np.array(v2, dtype=float)
        
        # Calcular normal usando producto cruzado
        edge1 = self.v1 - self.v0
        edge2 = self.v2 - self.v0
        self.normal = np.cross(edge1, edge2)
        self.normal = self.normal / np.linalg.norm(self.normal)
        self.type = "Triangle"
    
    def ray_intersect(self, orig, dir):
        orig = np.array(orig, dtype=float)
        dir = np.array(dir, dtype=float)
        
        # Normalizar dirección
        dir_length = np.linalg.norm(dir)
        if dir_length == 0:
            return None
        dir = dir / dir_length
        
        # Algoritmo de Möller-Trumbore para intersección rayo-triángulo
        edge1 = self.v1 - self.v0
        edge2 = self.v2 - self.v0
        
        h = np.cross(dir, edge2)
        a = np.dot(edge1, h)
        
        if abs(a) < 1e-6:
            return None
        
        f = 1.0 / a
        s = orig - self.v0
        u = f * np.dot(s, h)
        
        if u < 0.0 or u > 1.0:
            return None
        
        q = np.cross(s, edge1)
        v = f * np.dot(dir, q)
        
        if v < 0.0 or u + v > 1.0:
            return None
        
        t = f * np.dot(edge2, q)
        
        if t < 1e-6:
            return None
        
        # Calcular punto de intersección
        hit_point = orig + t * dir
        
        # Determinar orientación de la normal
        normal = self.normal if np.dot(dir, self.normal) < 0 else -self.normal
        
        return Intercept(hit_point, normal, t, dir, self)

class Cube(Shape):
    def __init__(self, position, size, material):
        super().__init__(position, material)
        self.size = size
        self.type = "Cube"
        
        # Definir las 6 caras del cubo como planos
        pos = np.array(position, dtype=float)
        half_size = size / 2
        
        # Crear los 6 planos que forman el cubo
        self.faces = [
            # Cara frontal (z+)
            (pos + [0, 0, half_size], [0, 0, 1]),
            # Cara trasera (z-)
            (pos + [0, 0, -half_size], [0, 0, -1]),
            # Cara derecha (x+)
            (pos + [half_size, 0, 0], [1, 0, 0]),
            # Cara izquierda (x-)
            (pos + [-half_size, 0, 0], [-1, 0, 0]),
            # Cara superior (y+)
            (pos + [0, half_size, 0], [0, 1, 0]),
            # Cara inferior (y-)
            (pos + [0, -half_size, 0], [0, -1, 0])
        ]
    
    def ray_intersect(self, orig, dir):
        orig = np.array(orig, dtype=float)
        dir = np.array(dir, dtype=float)
        
        # Normalizar dirección
        dir_length = np.linalg.norm(dir)
        if dir_length == 0:
            return None
        dir = dir / dir_length
        
        closest_hit = None
        min_distance = float('inf')
        
        pos = np.array(self.position, dtype=float)
        half_size = self.size / 2
        
        # Verificar intersección con cada cara del cubo
        for face_center, face_normal in self.faces:
            face_normal = np.array(face_normal, dtype=float)
            
            # Intersección con el plano de la cara
            denom = np.dot(dir, face_normal)
            if abs(denom) < 1e-6:
                continue
            
            t = np.dot((face_center - orig), face_normal) / denom
            if t < 1e-6:
                continue
            
            # Punto de intersección
            hit_point = orig + t * dir
            
            # Verificar si el punto está dentro de los límites de la cara
            local_point = hit_point - pos
            
            # Determinar qué coordenadas verificar según la normal de la cara
            if abs(face_normal[0]) > 0.5:  # Cara X
                if abs(local_point[1]) <= half_size and abs(local_point[2]) <= half_size:
                    if t < min_distance:
                        min_distance = t
                        normal = face_normal if denom < 0 else -face_normal
                        closest_hit = Intercept(hit_point, normal, t, dir, self)
            elif abs(face_normal[1]) > 0.5:  # Cara Y
                if abs(local_point[0]) <= half_size and abs(local_point[2]) <= half_size:
                    if t < min_distance:
                        min_distance = t
                        normal = face_normal if denom < 0 else -face_normal
                        closest_hit = Intercept(hit_point, normal, t, dir, self)
            elif abs(face_normal[2]) > 0.5:  # Cara Z
                if abs(local_point[0]) <= half_size and abs(local_point[1]) <= half_size:
                    if t < min_distance:
                        min_distance = t
                        normal = face_normal if denom < 0 else -face_normal
                        closest_hit = Intercept(hit_point, normal, t, dir, self)
        
        return closest_hit