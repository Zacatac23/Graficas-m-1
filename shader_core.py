"""
shader_core.py
Sistema base de shaders: uniforms, estructuras de datos y clases base
"""

from math_utils import Vec3, Vec2
import time

class ShaderUniforms:
    """Clase para almacenar variables uniformes del shader"""
    def __init__(self):
        # Tiempo y animación
        self.time = 0.0
        
        # Cámara
        self.camera_pos = Vec3(0, 0, 5)
        
        # Iluminación
        self.light_pos = Vec3(2, 2, 2)
        self.light_color = Vec3(1, 1, 1)
        self.ambient_strength = 0.1
        self.specular_strength = 0.5
        self.shininess = 32.0
        
        # Matrices de transformación
        self.model_matrix = None
        self.view_matrix = None
        self.projection_matrix = None
        self.mvp_matrix = None
        
        # Parámetros específicos para shaders creativos
        self.noise_scale = 1.0
        self.wave_frequency = 1.0
        self.wave_amplitude = 0.1
        self.color_mix = 0.5
        self.rim_power = 2.0
        self.fresnel_power = 3.0
        self.pulse_speed = 3.0
        self.pulse_strength = 0.2
    
    def update_time(self):
        """Actualizar tiempo para animaciones"""
        self.time = time.time() % 100  # Evitar overflow

class VertexShaderOutput:
    """Salida del vertex shader"""
    def __init__(self):
        self.position = Vec3()  # Posición en espacio de clip
        self.world_pos = Vec3()  # Posición en espacio del mundo
        self.normal = Vec3()     # Normal en espacio del mundo
        self.uv = Vec2()         # Coordenadas de textura
        self.color = Vec3(1, 1, 1)  # Color del vértice
        self.w = 1.0             # Componente W para perspectiva

class FragmentShaderInput:
    """Entrada al fragment shader (datos interpolados)"""
    def __init__(self):
        self.world_pos = Vec3()
        self.normal = Vec3()
        self.uv = Vec2()
        self.color = Vec3(1, 1, 1)
        self.screen_pos = Vec2()

# ==================== CLASES BASE DE SHADERS ====================

class VertexShader:
    """Clase base para vertex shaders"""
    def __init__(self, name="Base Vertex Shader"):
        self.name = name
    
    def execute(self, vertex, uniforms):
        """Ejecutar el vertex shader
        
        Args:
            vertex: Vértice de entrada
            uniforms: Variables uniformes
            
        Returns:
            VertexShaderOutput: Datos transformados del vértice
        """
        raise NotImplementedError("Subclases deben implementar execute()")

class FragmentShader:
    """Clase base para fragment shaders"""
    def __init__(self, name="Base Fragment Shader"):
        self.name = name
    
    def execute(self, fragment_input, uniforms, texture_loader):
        """Ejecutar el fragment shader
        
        Args:
            fragment_input: Datos interpolados del fragmento
            uniforms: Variables uniformes
            texture_loader: Objeto para samplear texturas
            
        Returns:
            tuple: Color RGB (r, g, b) en rango [0, 255]
        """
        raise NotImplementedError("Subclases deben implementar execute()")

# ==================== UTILIDADES PARA SHADERS ====================

class ShaderUtils:
    """Utilidades matemáticas comunes para shaders"""
    
    @staticmethod
    def clamp(value, min_val=0.0, max_val=1.0):
        """Clampear valor entre min y max"""
        return max(min_val, min(max_val, value))
    
    @staticmethod
    def mix(a, b, t):
        """Interpolación lineal entre a y b"""
        t = ShaderUtils.clamp(t, 0.0, 1.0)
        return a * (1.0 - t) + b * t
    
    @staticmethod
    def smoothstep(edge0, edge1, x):
        """Interpolación suave entre edge0 y edge1"""
        t = ShaderUtils.clamp((x - edge0) / (edge1 - edge0), 0.0, 1.0)
        return t * t * (3.0 - 2.0 * t)
    
    @staticmethod
    def fract(x):
        """Parte fraccionaria de x"""
        return x - int(x)
    
    @staticmethod
    def vec3_to_rgb(color_vec):
        """Convertir Vec3 [0,1] a RGB [0,255]"""
        r = max(0, min(1, color_vec.x)) * 255
        g = max(0, min(1, color_vec.y)) * 255
        b = max(0, min(1, color_vec.z)) * 255
        return (int(r), int(g), int(b))
    
    @staticmethod
    def rgb_to_vec3(rgb_tuple):
        """Convertir RGB [0,255] a Vec3 [0,1]"""
        r, g, b = rgb_tuple
        return Vec3(r / 255.0, g / 255.0, b / 255.0)
    
    @staticmethod
    def noise_1d(x):
        """Función de ruido 1D simple"""
        import math
        x = ShaderUtils.fract(x * 0.1031)
        x *= x + 33.33
        x *= x + x
        return ShaderUtils.fract(x)
    
    @staticmethod
    def noise_3d(pos):
        """Función de ruido 3D pseudo-aleatoria"""
        import math
        x, y, z = pos.x, pos.y, pos.z
        
        # Función hash simple
        n = math.sin(x * 12.9898 + y * 78.233 + z * 37.719) * 43758.5453
        return ShaderUtils.fract(n)
    
    @staticmethod
    def fbm_noise(pos, octaves=4):
        """Fractal Brownian Motion noise"""
        import math
        value = 0.0
        amplitude = 0.5
        frequency = 1.0
        
        for i in range(octaves):
            scaled_pos = Vec3(pos.x * frequency, pos.y * frequency, pos.z * frequency)
            value += ShaderUtils.noise_3d(scaled_pos) * amplitude
            amplitude *= 0.5
            frequency *= 2.0
        
        return value

class ShaderInterpolator:
    """Clase para interpolar atributos entre vértices"""
    
    @staticmethod
    def interpolate_vec3(w1, w2, w3, v1, v2, v3):
        """Interpolar Vec3 usando coordenadas baricéntricas"""
        return Vec3(
            w1 * v1.x + w2 * v2.x + w3 * v3.x,
            w1 * v1.y + w2 * v2.y + w3 * v3.y,
            w1 * v1.z + w2 * v2.z + w3 * v3.z
        )
    
    @staticmethod
    def interpolate_vec2(w1, w2, w3, v1, v2, v3):
        """Interpolar Vec2 usando coordenadas baricéntricas"""
        return Vec2(
            w1 * v1.u + w2 * v2.u + w3 * v3.u,
            w1 * v1.v + w2 * v2.v + w3 * v3.v
        )
    
    @staticmethod
    def interpolate_float(w1, w2, w3, f1, f2, f3):
        """Interpolar float usando coordenadas baricéntricas"""
        return w1 * f1 + w2 * f2 + w3 * f3
    
    @staticmethod
    def interpolate_shader_output(w1, w2, w3, out1, out2, out3):
        """Interpolar salidas del vertex shader"""
        fragment_input = FragmentShaderInput()
        
        # Interpolar todos los atributos
        fragment_input.world_pos = ShaderInterpolator.interpolate_vec3(
            w1, w2, w3, out1.world_pos, out2.world_pos, out3.world_pos
        )
        
        fragment_input.normal = ShaderInterpolator.interpolate_vec3(
            w1, w2, w3, out1.normal, out2.normal, out3.normal
        )
        
        fragment_input.uv = ShaderInterpolator.interpolate_vec2(
            w1, w2, w3, out1.uv, out2.uv, out3.uv
        )
        
        fragment_input.color = ShaderInterpolator.interpolate_vec3(
            w1, w2, w3, out1.color, out2.color, out3.color
        )
        
        return fragment_input