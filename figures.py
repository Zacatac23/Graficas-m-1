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

class Cone(Shape):
    """
    Cono con vértice en la parte superior, base circular en la parte inferior
    Orientado a lo largo del eje Y
    """
    def __init__(self, position, radius, height, material):
        super().__init__(position, material)
        self.radius = radius
        self.height = height
        self.type = "Cone"
    
    def ray_intersect(self, orig, dir):
        orig = np.array(orig, dtype=float)
        dir = np.array(dir, dtype=float)
        
        # Normalizar dirección
        dir_length = np.linalg.norm(dir)
        if dir_length == 0:
            return None
        dir = dir / dir_length
        
        center = np.array(self.position, dtype=float)
        
        # El cono está centrado en 'position' con el vértice arriba
        # Vértice en: center + [0, height/2, 0]
        # Base en: center - [0, height/2, 0]
        
        apex = center + np.array([0, self.height/2, 0])
        
        # Vector desde el ápice al origen del rayo
        co = orig - apex
        
        # Ecuación del cono infinito (eje Y)
        # tan²(α) = (radius/height)²
        k = (self.radius / self.height) ** 2
        
        # Coeficientes de la ecuación cuadrática
        a = dir[0]**2 + dir[2]**2 - k * dir[1]**2
        b = 2 * (co[0] * dir[0] + co[2] * dir[2] - k * co[1] * dir[1])
        c = co[0]**2 + co[2]**2 - k * co[1]**2
        
        discriminant = b**2 - 4*a*c
        
        if discriminant < 0:
            return None
        
        if abs(a) < 1e-6:
            return None
        
        sqrt_disc = np.sqrt(discriminant)
        t1 = (-b - sqrt_disc) / (2*a)
        t2 = (-b + sqrt_disc) / (2*a)
        
        epsilon = 1e-6
        
        # Verificar ambas intersecciones
        for t in sorted([t1, t2]):
            if t < epsilon:
                continue
            
            hit_point = orig + t * dir
            
            # Verificar si está dentro de los límites de altura del cono
            local_y = hit_point[1] - apex[1]
            
            # El cono va desde apex (y=0) hasta base (y=-height)
            if local_y <= 0 and local_y >= -self.height:
                # Calcular normal
                # Para un cono, la normal es perpendicular a la superficie
                local_point = hit_point - apex
                
                # Radio en este punto
                r = np.sqrt(local_point[0]**2 + local_point[2]**2)
                
                # Normal del cono
                if r > epsilon:
                    normal_x = local_point[0] / r
                    normal_z = local_point[2] / r
                    normal_y = self.radius / self.height
                    
                    normal = np.array([normal_x, normal_y, normal_z])
                    normal = normal / np.linalg.norm(normal)
                else:
                    # En el vértice, usar normal hacia arriba
                    normal = np.array([0, 1, 0])
                
                return Intercept(hit_point, normal, t, dir, self)
        
        return None


class Rectangle(Shape):
    """
    Rectángulo plano (cuadrilátero)
    """
    def __init__(self, corner, width_vec, height_vec, material):
        """
        corner: esquina inicial del rectángulo
        width_vec: vector que define el ancho
        height_vec: vector que define la altura
        """
        super().__init__(corner, material)
        self.corner = np.array(corner, dtype=float)
        self.width_vec = np.array(width_vec, dtype=float)
        self.height_vec = np.array(height_vec, dtype=float)
        self.type = "Rectangle"
        
        # Calcular normal
        self.normal = np.cross(width_vec, height_vec)
        self.normal = self.normal / np.linalg.norm(self.normal)
    
    def ray_intersect(self, orig, dir):
        orig = np.array(orig, dtype=float)
        dir = np.array(dir, dtype=float)
        
        # Normalizar dirección
        dir_length = np.linalg.norm(dir)
        if dir_length == 0:
            return None
        dir = dir / dir_length
        
        # Intersección con el plano
        denom = np.dot(dir, self.normal)
        
        if abs(denom) <= 0.0001:
            return None
        
        num = np.dot(np.subtract(self.corner, orig), self.normal)
        t = num / denom
        
        if t < 0:
            return None
        
        hit = orig + t * dir
        
        # Verificar si está dentro del rectángulo
        # Proyectar el punto hit al plano del rectángulo
        local = hit - self.corner
        
        # Proyecciones en los vectores de ancho y altura
        proj_width = np.dot(local, self.width_vec) / np.dot(self.width_vec, self.width_vec)
        proj_height = np.dot(local, self.height_vec) / np.dot(self.height_vec, self.height_vec)
        
        # Verificar si está dentro de los límites [0, 1]
        if 0 <= proj_width <= 1 and 0 <= proj_height <= 1:
            return Intercept(hit, self.normal, t, dir, self)
        
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