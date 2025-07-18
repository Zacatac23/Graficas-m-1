import numpy as np
import random
import math
from PIL import Image

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

class Triangle:
    def __init__(self, v1, v2, v3):
        self.v1 = v1
        self.v2 = v2
        self.v3 = v3
        # Color aleatorio para cada triángulo como lo requiere la tarea
        self.color = (
            random.randint(50, 255),
            random.randint(50, 255), 
            random.randint(50, 255)
        )
    
    def is_degenerate(self):
        """Verificar si el triángulo es degenerado"""
        edge1 = self.v2 - self.v1
        edge2 = self.v3 - self.v1
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
    
    def transform_point(self, point):
        """Transformar un punto 3D"""
        point_array = np.array([point.x, point.y, point.z, 1.0])
        transformed = self.m @ point_array
        return Vec3(transformed[0], transformed[1], transformed[2])
    
    def __mul__(self, other):
        return Matrix4x4(self.m @ other.m)

class OBJLoader:
    def __init__(self):
        self.vertices = []
        self.triangles = []
    
    def load_obj(self, filename):
        """Cargar archivo OBJ"""
        vertices = []
        triangles = []
        
        try:
            with open(filename, 'r') as file:
                line_number = 0
                for line in file:
                    line_number += 1
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
                    
                    elif line.startswith('f '):
                        # Parsear cara
                        face_triangles = self.parse_face(line, vertices, line_number)
                        triangles.extend(face_triangles)
            
            # Filtrar triángulos degenerados
            valid_triangles = [t for t in triangles if not t.is_degenerate()]
            
            self.vertices = vertices
            self.triangles = valid_triangles
            
            print(f"Modelo cargado exitosamente:")
            print(f"  - {len(vertices)} vértices")
            print(f"  - {len(self.triangles)} triángulos válidos")
            return True
            
        except FileNotFoundError:
            print(f"Error: No se encontró el archivo '{filename}'")
            return False
        except Exception as e:
            print(f"Error al cargar archivo: {e}")
            return False
    
    def parse_face(self, line, vertices, line_number):
        """Parsear una cara y convertirla en triángulos"""
        parts = line.split()
        if len(parts) < 4:
            return []
        
        # Extraer índices de vértices
        vertex_indices = []
        for i in range(1, len(parts)):
            vertex_part = parts[i].split('/')[0]
            try:
                vertex_index = int(vertex_part) - 1
                if 0 <= vertex_index < len(vertices):
                    vertex_indices.append(vertex_index)
            except ValueError:
                continue
        
        # Triangular la cara (fan triangulation)
        triangles = []
        for i in range(1, len(vertex_indices) - 1):
            triangle = Triangle(
                vertices[vertex_indices[0]],
                vertices[vertex_indices[i]],
                vertices[vertex_indices[i + 1]]
            )
            triangles.append(triangle)
        
        return triangles

class BMPRasterizer:
    def __init__(self, width=800, height=600):
        self.width = width
        self.height = height
        # Crear imagen RGB
        self.image = Image.new('RGB', (width, height), (0, 0, 0))
        self.pixels = self.image.load()
        
        self.obj_loader = OBJLoader()
        
    def load_model(self, obj_filename):
        """Cargar modelo OBJ"""
        return self.obj_loader.load_obj(obj_filename)
    
    def calculate_model_bounds(self):
        """Calcular límites del modelo para centrarlo y escalarlo"""
        if not self.obj_loader.vertices:
            return Vec3(), Vec3()
        
        min_x = min(v.x for v in self.obj_loader.vertices)
        max_x = max(v.x for v in self.obj_loader.vertices)
        min_y = min(v.y for v in self.obj_loader.vertices)
        max_y = max(v.y for v in self.obj_loader.vertices)
        min_z = min(v.z for v in self.obj_loader.vertices)
        max_z = max(v.z for v in self.obj_loader.vertices)
        
        return Vec3(min_x, min_y, min_z), Vec3(max_x, max_y, max_z)
    
    def create_object_matrix(self):
        """Crear matriz de objeto para centrar y escalar el modelo"""
        min_bound, max_bound = self.calculate_model_bounds()
        
        # Centrar el modelo
        center_x = (min_bound.x + max_bound.x) / 2
        center_y = (min_bound.y + max_bound.y) / 2
        center_z = (min_bound.z + max_bound.z) / 2
        
        # Calcular escala para que quepa en pantalla
        size_x = max_bound.x - min_bound.x
        size_y = max_bound.y - min_bound.y
        size_z = max_bound.z - min_bound.z
        max_size = max(size_x, size_y, size_z)
        
        # Escala para que el modelo ocupe aproximadamente 60% de la pantalla
        target_size = min(self.width, self.height) * 0.6
        scale_factor = target_size / max_size if max_size > 0 else 1.0
        
        print(f"Información del modelo:")
        print(f"  - Dimensiones: {size_x:.2f} x {size_y:.2f} x {size_z:.2f}")
        print(f"  - Centro: ({center_x:.2f}, {center_y:.2f}, {center_z:.2f})")
        print(f"  - Factor de escala: {scale_factor:.2f}")
        
        # Crear matriz de objeto: Traslación -> Escala -> Rotación -> Posición final
        translation_to_origin = Matrix4x4.translation(-center_x, -center_y, -center_z)
        scaling = Matrix4x4.scale(scale_factor, scale_factor, scale_factor)
        rotation_x = Matrix4x4.rotation_x(0.3)  # Rotación ligera para mejor vista
        rotation_y = Matrix4x4.rotation_y(0.5)
        final_translation = Matrix4x4.translation(0, 0, 0)  # Mantener en origen para proyección
        
        # Combinar transformaciones
        object_matrix = final_translation * rotation_y * rotation_x * scaling * translation_to_origin
        
        return object_matrix
    
    def project_point(self, point):
        """Proyección ortográfica simple"""
        # Convertir coordenadas 3D a 2D (proyección ortográfica)
        x_screen = int(self.width / 2 + point.x)
        y_screen = int(self.height / 2 - point.y)  # Invertir Y para que +Y sea hacia arriba
        
        return x_screen, y_screen
    
    def draw_pixel(self, x, y, color):
        """Dibujar un pixel en la imagen"""
        if 0 <= x < self.width and 0 <= y < self.height:
            self.pixels[x, y] = color
    
    def draw_line(self, x1, y1, x2, y2, color):
        """Dibujar línea usando algoritmo de Bresenham"""
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx - dy
        
        x, y = x1, y1
        while True:
            self.draw_pixel(x, y, color)
            
            if x == x2 and y == y2:
                break
            
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy
    
    def fill_triangle(self, x1, y1, x2, y2, x3, y3, color):
        """Rellenar triángulo usando scan line"""
        # Ordenar vértices por Y
        if y1 > y2:
            x1, y1, x2, y2 = x2, y2, x1, y1
        if y1 > y3:
            x1, y1, x3, y3 = x3, y3, x1, y1
        if y2 > y3:
            x2, y2, x3, y3 = x3, y3, x2, y2
        
        # Evitar división por cero
        if y3 == y1:
            return
        
        # Scan line fill
        for y in range(max(0, int(y1)), min(self.height, int(y3) + 1)):
            if y1 != y3:
                # Interpolación en lado izquierdo/derecho
                if y <= y2:
                    # Parte superior del triángulo
                    if y2 != y1:
                        x_left = x1 + (x2 - x1) * (y - y1) / (y2 - y1)
                    else:
                        x_left = x1
                    x_right = x1 + (x3 - x1) * (y - y1) / (y3 - y1)
                else:
                    # Parte inferior del triángulo
                    if y3 != y2:
                        x_left = x2 + (x3 - x2) * (y - y2) / (y3 - y2)
                    else:
                        x_left = x2
                    x_right = x1 + (x3 - x1) * (y - y1) / (y3 - y1)
                
                # Asegurar que x_left <= x_right
                if x_left > x_right:
                    x_left, x_right = x_right, x_left
                
                # Dibujar línea horizontal
                for x in range(max(0, int(x_left)), min(self.width, int(x_right) + 1)):
                    self.draw_pixel(x, y, color)
    
    def render_model(self):
        """Renderizar el modelo completo"""
        if not self.obj_loader.triangles:
            print("No hay triángulos para renderizar")
            return
        
        # Crear matriz de objeto
        object_matrix = self.create_object_matrix()
        
        print(f"Renderizando {len(self.obj_loader.triangles)} triángulos...")
        
        triangles_rendered = 0
        
        for triangle in self.obj_loader.triangles:
            # Transformar vértices usando la matriz de objeto
            v1 = object_matrix.transform_point(triangle.v1)
            v2 = object_matrix.transform_point(triangle.v2)
            v3 = object_matrix.transform_point(triangle.v3)
            
            # Proyectar a 2D
            p1 = self.project_point(v1)
            p2 = self.project_point(v2)
            p3 = self.project_point(v3)
            
            # Verificar que el triángulo esté en pantalla
            if (0 <= p1[0] < self.width and 0 <= p1[1] < self.height or
                0 <= p2[0] < self.width and 0 <= p2[1] < self.height or
                0 <= p3[0] < self.width and 0 <= p3[1] < self.height):
                
                # Rellenar triángulo con color aleatorio
                self.fill_triangle(p1[0], p1[1], p2[0], p2[1], p3[0], p3[1], triangle.color)
                triangles_rendered += 1
        
        print(f"Triángulos renderizados: {triangles_rendered}")
    
    def save_bmp(self, filename):
        """Guardar imagen como BMP"""
        try:
            # Convertir a BMP y guardar
            self.image.save(filename, 'BMP')
            print(f"✅ Imagen guardada como {filename}")
            return True
        except Exception as e:
            print(f"❌ Error al guardar BMP: {e}")
            return False
    
    def save_png(self, filename):
        """Guardar imagen como PNG (opcional para visualización)"""
        try:
            self.image.save(filename, 'PNG')
            print(f"✅ Imagen PNG guardada como {filename}")
            return True
        except Exception as e:
            print(f"❌ Error al guardar PNG: {e}")
            return False

def main():
    print("=== 🎨 Rasterizador 3D para BMP ===")
    print("Características implementadas:")
    print("✅ Creación y escritura de archivos BMP")
    print("✅ Cargador de modelos OBJ personalizado")
    print("✅ Rasterización de triángulos rellenos")
    print("✅ Colores aleatorios por triángulo")
    print("✅ Matriz de objeto (Traslación, Rotación, Escala)")
    print("✅ Auto-centrado y escalado del modelo")
    print()
    
    # Crear rasterizador
    rasterizer = BMPRasterizer(800, 600)
    
    # Solicitar nombre del archivo OBJ
    obj_filename = input("Ingresa el nombre del archivo OBJ (por ejemplo: modelo.obj): ").strip()
    
    if not obj_filename:
        obj_filename = "M.obj"  # Archivo por defecto
    
    # Cargar modelo
    if rasterizer.load_model(obj_filename):
        print(f"🎉 {obj_filename} cargado exitosamente!")
        
        # Renderizar modelo
        rasterizer.render_model()
        
        # Guardar como BMP (requisito principal)
        bmp_filename = obj_filename.replace('.obj', '_render.bmp')
        rasterizer.save_bmp(bmp_filename)
        
        # Guardar también como PNG para fácil visualización
        png_filename = obj_filename.replace('.obj', '_render.png')
        rasterizer.save_png(png_filename)
        
        print(f"\n🎨 Renderización completada!")
        print(f"📁 Archivos generados:")
        print(f"   - {bmp_filename} (archivo BMP requerido)")
        print(f"   - {png_filename} (para visualización)")
        
    else:
        print(f"❌ No se pudo cargar {obj_filename}")
        print("Verifica que:")
        print("  1. El archivo existe en esta carpeta")
        print("  2. El archivo tiene formato OBJ válido")
        print("  3. Tienes permisos de lectura")

if __name__ == "__main__":
    main()