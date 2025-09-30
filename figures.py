import numpy as np
from intercept import Intercept

# Clase base Shape
class Shape(object):
    def __init__(self, position, material):
        self.position = position
        self.material = material
        self.type = "Shape"
    
    def ray_intersect(self, orig, dir):
        return None


# ============= FIGURAS BÁSICAS NECESARIAS =============

class Sphere(Shape):
    """Esfera básica"""
    def __init__(self, position, radius, material):
        super().__init__(position, material)
        self.radius = radius
        self.type = "Sphere"
    
    def ray_intersect(self, orig, dir):
        L = np.subtract(self.position, orig)
        tca = np.dot(L, dir)
        d = (np.linalg.norm(L) ** 2 - tca ** 2) ** 0.5
        
        if d > self.radius:
            return None
        
        thc = (self.radius ** 2 - d ** 2) ** 0.5
        t0 = tca - thc
        t1 = tca + thc
        
        if t0 < 0:
            t0 = t1
        if t0 < 0:
            return None
        
        hit = np.add(orig, t0 * np.array(dir))
        normal = np.subtract(hit, self.position)
        normal = normal / np.linalg.norm(normal)
        
        return Intercept(point=hit, normal=normal, distance=t0, rayDirection=dir, obj=self)


class Plane(Shape):
    """Plano infinito"""
    def __init__(self, position, normal, material):
        super().__init__(position, material)
        self.normal = normal / np.linalg.norm(normal)
        self.type = "Plane"
    
    def ray_intersect(self, orig, dir):
        denom = np.dot(dir, self.normal)
        
        if abs(denom) <= 0.0001:
            return None
        
        num = np.dot(np.subtract(self.position, orig), self.normal)
        t = num / denom
        
        if t < 0:
            return None
        
        hit = np.add(orig, t * np.array(dir))
        
        return Intercept(point=hit, normal=self.normal, distance=t, rayDirection=dir, obj=self)


class Triangle(Shape):
    """Triángulo - Algoritmo Möller-Trumbore"""
    def __init__(self, vertices, material):
        self.vertices = vertices
        self.material = material
        self.type = "Triangle"
        
        # Calcular normal del triángulo
        v0, v1, v2 = vertices
        edge1 = np.subtract(v1, v0)
        edge2 = np.subtract(v2, v0)
        self.normal = np.cross(edge1, edge2)
        self.normal = self.normal / np.linalg.norm(self.normal)
        self.position = v0
    
    def ray_intersect(self, orig, dir):
        v0, v1, v2 = self.vertices
        
        # Algoritmo Möller-Trumbore para intersección rayo-triángulo
        edge1 = np.subtract(v1, v0)
        edge2 = np.subtract(v2, v0)
        h = np.cross(dir, edge2)
        a = np.dot(edge1, h)
        
        # Rayo paralelo al triángulo
        if -0.00001 < a < 0.00001:
            return None
        
        f = 1.0 / a
        s = np.subtract(orig, v0)
        u = f * np.dot(s, h)
        
        # Verificar coordenadas baricéntricas
        if u < 0.0 or u > 1.0:
            return None
        
        q = np.cross(s, edge1)
        v = f * np.dot(dir, q)
        
        if v < 0.0 or u + v > 1.0:
            return None
        
        t = f * np.dot(edge2, q)
        
        if t < 0.00001:
            return None
        
        hit = np.add(orig, t * np.array(dir))
        
        return Intercept(point=hit, normal=self.normal, distance=t, rayDirection=dir, obj=self)


class Cube(Shape):
    """Cubo - Algoritmo de Axis-Aligned Bounding Box (AABB)"""
    def __init__(self, position, size, material):
        super().__init__(position, material)
        self.size = size
        self.type = "Cube"
        self.bounds_min = np.array(position) - size/2
        self.bounds_max = np.array(position) + size/2
    
    def ray_intersect(self, orig, dir):
        orig = np.array(orig)
        dir = np.array(dir)
        
        # Algoritmo AABB (slab method)
        tmin = (self.bounds_min - orig) / (dir + 1e-10)
        tmax = (self.bounds_max - orig) / (dir + 1e-10)
        
        t1 = np.minimum(tmin, tmax)
        t2 = np.maximum(tmin, tmax)
        
        tnear = np.max(t1)
        tfar = np.min(t2)
        
        if tnear > tfar or tfar < 0:
            return None
        
        t = tnear if tnear > 0 else tfar
        hit = orig + t * dir
        
        # Calcular normal basada en la cara que intersecta
        center = np.array(self.position)
        normal = hit - center
        abs_normal = np.abs(normal)
        max_component = np.max(abs_normal)
        
        normal = np.array([
            1 if abs_normal[0] == max_component else 0,
            1 if abs_normal[1] == max_component else 0,
            1 if abs_normal[2] == max_component else 0
        ]) * np.sign(normal)
        
        return Intercept(point=hit, normal=normal, distance=t, rayDirection=dir, obj=self)


class Disk(Shape):
    """Disco circular"""
    def __init__(self, position, radius, normal, material):
        super().__init__(position, material)
        self.radius = radius
        self.normal = normal / np.linalg.norm(normal)
        self.type = "Disk"
    
    def ray_intersect(self, orig, dir):
        denom = np.dot(dir, self.normal)
        
        if abs(denom) <= 0.0001:
            return None
        
        num = np.dot(np.subtract(self.position, orig), self.normal)
        t = num / denom
        
        if t < 0:
            return None
        
        hit = np.add(orig, t * np.array(dir))
        
        # Verificar si está dentro del radio
        if np.linalg.norm(np.subtract(hit, self.position)) > self.radius:
            return None
        
        return Intercept(point=hit, normal=self.normal, distance=t, rayDirection=dir, obj=self)


# ============= NUEVAS FIGURAS DEL LAB =============

class Cylinder(Shape):
    """
    NUEVA FIGURA 1: Cilindro infinito a lo largo del eje Y, con límites de altura
    """
    def __init__(self, position, radius, height, material):
        super().__init__(position, material)
        self.radius = radius
        self.height = height
        self.type = "Cylinder"
    
    def ray_intersect(self, orig, dir):
        orig = np.array(orig, dtype=float)
        dir = np.array(dir, dtype=float)
        
        # Normalizar dirección
        dir_length = np.linalg.norm(dir)
        if dir_length == 0:
            return None
        dir = dir / dir_length
        
        center = np.array(self.position, dtype=float)
        oc = orig - center
        
        # Para cilindro en eje Y, resolvemos en plano X-Z
        # Ecuación del rayo: P = orig + t * dir
        # Ecuación del cilindro: (x-cx)² + (z-cz)² = r²
        
        # Coeficientes de la ecuación cuadrática
        a = dir[0]**2 + dir[2]**2
        b = 2.0 * (oc[0] * dir[0] + oc[2] * dir[2])
        c = oc[0]**2 + oc[2]**2 - self.radius**2
        
        # Resolver ecuación cuadrática
        discriminant = b**2 - 4*a*c
        
        if discriminant < 0:
            return None  # No hay intersección
        
        if abs(a) < 1e-6:
            return None  # Rayo paralelo al eje del cilindro
        
        sqrt_disc = np.sqrt(discriminant)
        t1 = (-b - sqrt_disc) / (2*a)
        t2 = (-b + sqrt_disc) / (2*a)
        
        epsilon = 1e-6
        
        # Verificar ambos puntos de intersección
        for t in [t1, t2]:
            if t < epsilon:
                continue
            
            # Calcular punto de impacto
            hit_point = orig + t * dir
            
            # Verificar si está dentro de los límites de altura
            local_y = hit_point[1] - center[1]
            if abs(local_y) <= self.height / 2:
                # Calcular normal (perpendicular al eje Y)
                normal_vec = hit_point - center
                normal_vec[1] = 0  # Proyectar al plano X-Z
                normal = normal_vec / np.linalg.norm(normal_vec)
                
                return Intercept(hit_point, normal, t, dir, self)
        
        return None


class Ellipsoid(Shape):
    """
    NUEVA FIGURA 2: Elipsoide con diferentes radios en ejes X, Y, Z
    """
    def __init__(self, position, radii, material):
        super().__init__(position, material)
        self.radii = np.array(radii, dtype=float)  # [rx, ry, rz]
        self.type = "Ellipsoid"
    
    def ray_intersect(self, orig, dir):
        orig = np.array(orig, dtype=float)
        dir = np.array(dir, dtype=float)
        
        # Normalizar dirección
        dir_length = np.linalg.norm(dir)
        if dir_length == 0:
            return None
        dir = dir / dir_length
        
        center = np.array(self.position, dtype=float)
        
        # Transformar rayo a espacio del elipsoide
        # Escalar el espacio para que el elipsoide se convierta en esfera unitaria
        scale = 1.0 / self.radii
        
        # Transformar origen y dirección
        orig_scaled = (orig - center) * scale
        dir_scaled = dir * scale
        
        # Ahora resolver intersección rayo-esfera en espacio escalado
        # Rayo: P = orig_scaled + t * dir_scaled
        # Esfera unitaria: |P|² = 1
        
        a = np.dot(dir_scaled, dir_scaled)
        b = 2.0 * np.dot(orig_scaled, dir_scaled)
        c = np.dot(orig_scaled, orig_scaled) - 1.0
        
        discriminant = b**2 - 4*a*c
        
        if discriminant < 0:
            return None
        
        sqrt_disc = np.sqrt(discriminant)
        t1 = (-b - sqrt_disc) / (2*a)
        t2 = (-b + sqrt_disc) / (2*a)
        
        epsilon = 1e-6
        
        # Elegir la intersección positiva más cercana
        for t_scaled in [t1, t2]:
            if t_scaled < epsilon:
                continue
            
            # Transformar de vuelta al espacio mundial
            hit_point_scaled = orig_scaled + t_scaled * dir_scaled
            hit_point = hit_point_scaled / scale + center
            
            # Calcular t real en espacio mundial
            t_world = np.linalg.norm(hit_point - orig)
            
            # Calcular normal en espacio mundial
            # Normal = gradiente de la ecuación del elipsoide
            # F(x,y,z) = (x-cx)²/rx² + (y-cy)²/ry² + (z-cz)²/rz² - 1
            # ∇F = [2(x-cx)/rx², 2(y-cy)/ry², 2(z-cz)/rz²]
            
            local_point = hit_point - center
            normal = 2 * local_point / (self.radii**2)
            normal = normal / np.linalg.norm(normal)
            
            return Intercept(hit_point, normal, t_world, dir, self)
        
        return None