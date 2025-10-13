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
    """Cilindro infinito a lo largo del eje Y, con límites de altura"""
    def __init__(self, position, radius, height, material):
        super().__init__(position, material)
        self.radius = radius
        self.height = height
        self.type = "Cylinder"
    
    def ray_intersect(self, orig, dir):
        orig = np.array(orig, dtype=float)
        dir = np.array(dir, dtype=float)
        
        dir_length = np.linalg.norm(dir)
        if dir_length == 0:
            return None
        dir = dir / dir_length
        
        center = np.array(self.position, dtype=float)
        oc = orig - center
        
        a = dir[0]**2 + dir[2]**2
        b = 2.0 * (oc[0] * dir[0] + oc[2] * dir[2])
        c = oc[0]**2 + oc[2]**2 - self.radius**2
        
        discriminant = b**2 - 4*a*c
        
        if discriminant < 0:
            return None
        
        if abs(a) < 1e-6:
            return None
        
        sqrt_disc = np.sqrt(discriminant)
        t1 = (-b - sqrt_disc) / (2*a)
        t2 = (-b + sqrt_disc) / (2*a)
        
        epsilon = 1e-6
        
        for t in [t1, t2]:
            if t < epsilon:
                continue
            
            hit_point = orig + t * dir
            local_y = hit_point[1] - center[1]
            
            if abs(local_y) <= self.height / 2:
                normal_vec = hit_point - center
                normal_vec[1] = 0
                normal = normal_vec / np.linalg.norm(normal_vec)
                
                return Intercept(hit_point, normal, t, dir, self)
        
        return None


class Ellipsoid(Shape):
    """Elipsoide con diferentes radios en ejes X, Y, Z"""
    def __init__(self, position, radii, material):
        super().__init__(position, material)
        self.radii = np.array(radii, dtype=float)
        self.type = "Ellipsoid"
    
    def ray_intersect(self, orig, dir):
        orig = np.array(orig, dtype=float)
        dir = np.array(dir, dtype=float)
        
        dir_length = np.linalg.norm(dir)
        if dir_length == 0:
            return None
        dir = dir / dir_length
        
        center = np.array(self.position, dtype=float)
        scale = 1.0 / self.radii
        
        orig_scaled = (orig - center) * scale
        dir_scaled = dir * scale
        
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
        
        for t_scaled in [t1, t2]:
            if t_scaled < epsilon:
                continue
            
            hit_point_scaled = orig_scaled + t_scaled * dir_scaled
            hit_point = hit_point_scaled / scale + center
            t_world = np.linalg.norm(hit_point - orig)
            
            local_point = hit_point - center
            normal = 2 * local_point / (self.radii**2)
            normal = normal / np.linalg.norm(normal)
            
            return Intercept(hit_point, normal, t_world, dir, self)
        
        return None


class Cone(Shape):
    """Cono con vértice en la parte superior"""
    def __init__(self, position, radius, height, material):
        super().__init__(position, material)
        self.radius = radius
        self.height = height
        self.type = "Cone"
    
    def ray_intersect(self, orig, dir):
        orig = np.array(orig, dtype=float)
        dir = np.array(dir, dtype=float)
        
        dir_length = np.linalg.norm(dir)
        if dir_length == 0:
            return None
        dir = dir / dir_length
        
        center = np.array(self.position, dtype=float)
        apex = center + np.array([0, self.height/2, 0])
        co = orig - apex
        
        k = (self.radius / self.height) ** 2
        
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
        
        for t in sorted([t1, t2]):
            if t < epsilon:
                continue
            
            hit_point = orig + t * dir
            local_y = hit_point[1] - apex[1]
            
            if local_y <= 0 and local_y >= -self.height:
                local_point = hit_point - apex
                r = np.sqrt(local_point[0]**2 + local_point[2]**2)
                
                if r > epsilon:
                    normal_x = local_point[0] / r
                    normal_z = local_point[2] / r
                    normal_y = self.radius / self.height
                    
                    normal = np.array([normal_x, normal_y, normal_z])
                    normal = normal / np.linalg.norm(normal)
                else:
                    normal = np.array([0, 1, 0])
                
                return Intercept(hit_point, normal, t, dir, self)
        
        return None
class Torus(Shape):
    """
    Toroide (dona) - Orientado en el plano XZ (horizontal)
    major_radius: radio del círculo central (del centro al tubo)
    minor_radius: radio del tubo
    """
    def __init__(self, position, major_radius, minor_radius, material):
        super().__init__(position, material)
        self.major_radius = major_radius  # R (radio mayor)
        self.minor_radius = minor_radius  # r (radio menor/tubo)
        self.type = "Torus"
    
    def ray_intersect(self, orig, dir):
        orig = np.array(orig, dtype=float)
        dir = np.array(dir, dtype=float)
        
        # Normalizar dirección
        dir_length = np.linalg.norm(dir)
        if dir_length == 0:
            return None
        dir = dir / dir_length
        
        center = np.array(self.position, dtype=float)
        
        # Trasladar el origen al centro del toroide
        oc = orig - center
        
        # Parámetros del toroide
        R = self.major_radius  # Radio mayor
        r = self.minor_radius  # Radio menor
        
        # Ecuación del toroide (orientado en XZ):
        # (sqrt(x² + z²) - R)² + y² = r²
        
        # Coeficientes para la ecuación cuártica
        # Expandiendo: (x² + y² + z² + R² - r²)² = 4R²(x² + z²)
        
        sum_d_sqr = np.dot(dir, dir)
        e = np.dot(oc, oc) - R*R - r*r
        f = np.dot(oc, dir)
        four_a_sqr = 4.0 * R * R
        
        # Coeficientes de la ecuación cuártica: c4*t^4 + c3*t^3 + c2*t^2 + c1*t + c0 = 0
        c4 = sum_d_sqr * sum_d_sqr
        c3 = 4.0 * sum_d_sqr * f
        c2 = 2.0 * sum_d_sqr * e + 4.0 * f * f + four_a_sqr * (dir[0]*dir[0] + dir[2]*dir[2])
        c1 = 4.0 * f * e + 2.0 * four_a_sqr * (oc[0]*dir[0] + oc[2]*dir[2])
        c0 = e * e - four_a_sqr * (r*r - oc[1]*oc[1])
        
        # Resolver ecuación cuártica usando método de Ferrari simplificado
        # o Newton-Raphson para aproximación numérica
        roots = self._solve_quartic(c4, c3, c2, c1, c0)
        
        if not roots:
            return None
        
        # Encontrar la raíz positiva más cercana
        epsilon = 1e-6
        closest_t = float('inf')
        
        for t in roots:
            if t > epsilon and t < closest_t:
                closest_t = t
        
        if closest_t == float('inf'):
            return None
        
        # Calcular punto de intersección
        hit_point = orig + closest_t * dir
        
        # Calcular normal
        hit_local = hit_point - center
        
        # Para un toroide orientado en XZ:
        # Proyectar el punto al plano XZ y encontrar el punto en el círculo mayor
        param_x = hit_local[0]
        param_z = hit_local[2]
        dist_from_y_axis = np.sqrt(param_x*param_x + param_z*param_z)
        
        if dist_from_y_axis < epsilon:
            # Punto en el eje Y
            normal = np.array([0, np.sign(hit_local[1]) if abs(hit_local[1]) > epsilon else 1, 0])
        else:
            # Punto en el círculo mayor
            circle_point = np.array([
                param_x * R / dist_from_y_axis,
                0,
                param_z * R / dist_from_y_axis
            ])
            
            # Normal apunta desde el círculo mayor hacia el punto
            normal = hit_local - circle_point
            normal = normal / np.linalg.norm(normal)
        
        return Intercept(hit_point, normal, closest_t, dir, self)
    
    def _solve_quartic(self, c4, c3, c2, c1, c0):
        """
        Resuelve ecuación cuártica: c4*t^4 + c3*t^3 + c2*t^2 + c1*t + c0 = 0
        Usando método numérico de Ferrari simplificado
        """
        if abs(c4) < 1e-10:
            return []
        
        # Normalizar
        c3 /= c4
        c2 /= c4
        c1 /= c4
        c0 /= c4
        
        # Usar método de Newton-Raphson para encontrar raíces
        # Simplificación: buscar raíces en intervalos
        roots = []
        
        # Evaluar la función y su derivada
        def f(t):
            return ((((t + c3) * t + c2) * t + c1) * t + c0)
        
        def df(t):
            return (((4*t + 3*c3) * t + 2*c2) * t + c1)
        
        # Buscar hasta 4 raíces usando diferentes valores iniciales
        test_points = [-10, -1, 0, 1, 10, 20, 50]
        
        for start in test_points:
            t = start
            for _ in range(50):  # Iteraciones de Newton-Raphson
                ft = f(t)
                dft = df(t)
                
                if abs(dft) < 1e-10:
                    break
                
                t_new = t - ft / dft
                
                if abs(t_new - t) < 1e-6:
                    # Verificar si es una raíz real
                    if abs(f(t_new)) < 1e-4:
                        # Verificar si ya tenemos esta raíz
                        is_duplicate = False
                        for existing in roots:
                            if abs(t_new - existing) < 1e-3:
                                is_duplicate = True
                                break
                        
                        if not is_duplicate and t_new > 0:
                            roots.append(t_new)
                    break
                
                t = t_new
        
        return sorted(roots)

class Rectangle(Shape):
    """Paralelepípedo 3D (caja rectangular sólida)"""
    def __init__(self, corner, width_vec, height_vec, depth_vec, material):
        super().__init__(corner, material)
        self.corner = np.array(corner, dtype=float)
        self.width_vec = np.array(width_vec, dtype=float)
        self.height_vec = np.array(height_vec, dtype=float)
        self.depth_vec = np.array(depth_vec, dtype=float)
        self.type = "Rectangle3D"
        
        # Calcular los 8 vértices del paralelepípedo
        self.vertices = [
            self.corner,  # 0: corner
            self.corner + self.width_vec,  # 1: corner + width
            self.corner + self.height_vec,  # 2: corner + height
            self.corner + self.depth_vec,  # 3: corner + depth
            self.corner + self.width_vec + self.height_vec,  # 4: corner + width + height
            self.corner + self.width_vec + self.depth_vec,  # 5: corner + width + depth
            self.corner + self.height_vec + self.depth_vec,  # 6: corner + height + depth
            self.corner + self.width_vec + self.height_vec + self.depth_vec  # 7: esquina opuesta
        ]
        
        # Definir las 6 caras como planos (con verificación de vectores cero)
        self.faces = []
        
        # Verificar que los vectores no sean cero
        width_norm = np.linalg.norm(self.width_vec)
        height_norm = np.linalg.norm(self.height_vec) 
        depth_norm = np.linalg.norm(self.depth_vec)
        
        if width_norm > 0 and height_norm > 0 and depth_norm > 0:
            self.faces = [
                # Cara frontal (normal hacia -depth)
                {"normal": -self.depth_vec / depth_norm, "point": self.corner, "u_vec": self.width_vec, "v_vec": self.height_vec},
                # Cara trasera (normal hacia +depth)  
                {"normal": self.depth_vec / depth_norm, "point": self.corner + self.depth_vec, "u_vec": self.width_vec, "v_vec": self.height_vec},
                # Cara izquierda (normal hacia -width)
                {"normal": -self.width_vec / width_norm, "point": self.corner, "u_vec": self.depth_vec, "v_vec": self.height_vec},
                # Cara derecha (normal hacia +width)
                {"normal": self.width_vec / width_norm, "point": self.corner + self.width_vec, "u_vec": self.depth_vec, "v_vec": self.height_vec},
                # Cara inferior (normal hacia -height)
                {"normal": -self.height_vec / height_norm, "point": self.corner, "u_vec": self.width_vec, "v_vec": self.depth_vec},
                # Cara superior (normal hacia +height)
                {"normal": self.height_vec / height_norm, "point": self.corner + self.height_vec, "u_vec": self.width_vec, "v_vec": self.depth_vec}
            ]
    
    def ray_intersect(self, orig, dir):
        orig = np.array(orig, dtype=float)
        dir = np.array(dir, dtype=float)
        
        dir_length = np.linalg.norm(dir)
        if dir_length == 0:
            return None
        dir = dir / dir_length
        
        closest_t = float('inf')
        closest_normal = None
        
        # Probar intersección con cada cara
        for face in self.faces:
            normal = face["normal"]
            point = face["point"]
            u_vec = face["u_vec"]
            v_vec = face["v_vec"]
            
            denom = np.dot(dir, normal)
            
            if abs(denom) <= 0.0001:  # Rayo paralelo al plano
                continue
            
            num = np.dot(np.subtract(point, orig), normal)
            t = num / denom
            
            if t <= 0:  # Intersección detrás del origen
                continue
            
            # Calcular punto de intersección
            hit = orig + t * dir
            local = hit - point
            
            # Proyectar en las direcciones u y v de la cara
            u_len_sq = np.dot(u_vec, u_vec)
            v_len_sq = np.dot(v_vec, v_vec)
            
            if u_len_sq == 0 or v_len_sq == 0:
                continue
                
            proj_u = np.dot(local, u_vec) / u_len_sq
            proj_v = np.dot(local, v_vec) / v_len_sq
            
            # Verificar si está dentro de los límites de la cara
            if 0 <= proj_u <= 1 and 0 <= proj_v <= 1:
                if t < closest_t:
                    closest_t = t
                    closest_normal = normal
        
        if closest_t == float('inf'):
            return None
        
        hit_point = orig + closest_t * dir
        return Intercept(hit_point, closest_normal, closest_t, dir, self)