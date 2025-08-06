"""
shader_core.py
Sistema core de shaders con clases base y utilidades
"""

import math
import time
from math_utils import Vec2, Vec3, Matrix4x4

class VertexShaderOutput:
    """Salida del vertex shader"""
    def __init__(self):
        self.position = Vec3(0, 0, 0)  # Posición en espacio de clip
        self.w = 1.0  # Coordenada homogénea
        self.world_pos = Vec3(0, 0, 0)
        self.normal = Vec3(0, 1, 0)
        self.uv = Vec2(0, 0)
        self.color = (255, 255, 255)
        self.screen_pos = Vec2(0, 0)

class FragmentShaderInput:
    """Entrada del fragment shader (interpolada)"""
    def __init__(self):
        self.world_pos = Vec3(0, 0, 0)
        self.normal = Vec3(0, 1, 0)
        self.uv = Vec2(0, 0)
        self.color = (255, 255, 255)
        self.screen_pos = Vec2(0, 0)

class ShaderUniforms:
    """Variables uniformes compartidas entre shaders"""
    def __init__(self):
        # Matrices de transformación
        self.model_matrix = Matrix4x4.identity()
        self.view_matrix = Matrix4x4.identity()
        self.projection_matrix = Matrix4x4.identity()
        self.mvp_matrix = Matrix4x4.identity()
        
        # Información de tiempo y animación
        self.time = 0.0
        self.start_time = time.time()
        
        # Parámetros de efectos
        self.wave_frequency = 2.0
        self.wave_amplitude = 0.1
        self.rim_power = 2.0
        self.fresnel_power = 3.0
        self.pulse_speed = 2.0
        self.pulse_strength = 0.3
        self.noise_scale = 5.0
        
        # Información de cámara y luz
        self.camera_pos = Vec3(0, 0, 5)
        self.light_dir = Vec3(0.5, 1.0, 0.5).normalize()
    
    def update_time(self):
        """Actualizar tiempo para animaciones"""
        self.time = time.time() - self.start_time

class VertexShader:
    """Clase base para vertex shaders"""
    def __init__(self, name="Base Vertex Shader"):
        self.name = name
    
    def execute(self, vertex, uniforms):
        """Ejecutar vertex shader - debe ser implementado por subclases"""
        raise NotImplementedError("Subclases deben implementar execute()")

class FragmentShader:
    """Clase base para fragment shaders"""
    def __init__(self, name="Base Fragment Shader"):
        self.name = name
    
    def execute(self, fragment_input, uniforms, geometry_data=None):
        """Ejecutar fragment shader - debe ser implementado por subclases"""
        raise NotImplementedError("Subclases deben implementar execute()")

class ShaderInterpolator:
    """Utilidades para interpolación de atributos entre vértices"""
    
    @staticmethod
    def interpolate_shader_output(w1, w2, w3, out1, out2, out3):
        """Interpolar salidas de vertex shader usando coordenadas baricéntricas"""
        result = FragmentShaderInput()
        
        # Interpolar posición mundial
        result.world_pos = Vec3(
            w1 * out1.world_pos.x + w2 * out2.world_pos.x + w3 * out3.world_pos.x,
            w1 * out1.world_pos.y + w2 * out2.world_pos.y + w3 * out3.world_pos.y,
            w1 * out1.world_pos.z + w2 * out2.world_pos.z + w3 * out3.world_pos.z
        )
        
        # Interpolar normal
        result.normal = Vec3(
            w1 * out1.normal.x + w2 * out2.normal.x + w3 * out3.normal.x,
            w1 * out1.normal.y + w2 * out2.normal.y + w3 * out3.normal.y,
            w1 * out1.normal.z + w2 * out2.normal.z + w3 * out3.normal.z
        ).normalize()
        
        # Interpolar coordenadas UV
        result.uv = Vec2(
            w1 * out1.uv.x + w2 * out2.uv.x + w3 * out3.uv.x,
            w1 * out1.uv.y + w2 * out2.uv.y + w3 * out3.uv.y
        )
        
        # Interpolar color
        r = int(w1 * out1.color[0] + w2 * out2.color[0] + w3 * out3.color[0])
        g = int(w1 * out1.color[1] + w2 * out2.color[1] + w3 * out3.color[1])
        b = int(w1 * out1.color[2] + w2 * out2.color[2] + w3 * out3.color[2])
        result.color = (r, g, b)
        
        return result

class ShaderUtils:
    """Utilidades matemáticas para shaders"""
    
    @staticmethod
    def clamp(value, min_val=0.0, max_val=1.0):
        """Limitar valor entre min y max"""
        return max(min_val, min(max_val, value))
    
    @staticmethod
    def saturate(value):
        """Limitar valor entre 0 y 1"""
        return ShaderUtils.clamp(value, 0.0, 1.0)
    
    @staticmethod
    def lerp(a, b, t):
        """Interpolación lineal"""
        return a + (b - a) * t
    
    @staticmethod
    def smoothstep(edge0, edge1, x):
        """Interpolación suave"""
        t = ShaderUtils.clamp((x - edge0) / (edge1 - edge0))
        return t * t * (3.0 - 2.0 * t)
    
    @staticmethod
    def noise(x, y):
        """Ruido pseudo-aleatorio simple"""
        n = int(x * 57.0 + y * 113.0) & 0x7FFFFFFF
        n = (n << 13) ^ n
        return (1.0 - ((n * (n * n * 15731 + 789221) + 1376312589) & 0x7FFFFFFF) / 1073741824.0)
    
    @staticmethod
    def fbm_noise(x, y, octaves=4):
        """Fractal Brownian Motion noise"""
        value = 0.0
        amplitude = 0.5
        frequency = 1.0
        
        for i in range(octaves):
            value += amplitude * ShaderUtils.noise(x * frequency, y * frequency)
            amplitude *= 0.5
            frequency *= 2.0
        
        return value
    
    @staticmethod
    def rgb_to_tuple(r, g, b):
        """Convertir valores RGB float a tupla de enteros"""
        return (
            int(ShaderUtils.clamp(r, 0, 1) * 255),
            int(ShaderUtils.clamp(g, 0, 1) * 255),
            int(ShaderUtils.clamp(b, 0, 1) * 255)
        )