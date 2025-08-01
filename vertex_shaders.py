"""
vertex_shaders.py
Implementaciones de diferentes vertex shaders
"""

import math
from shader_core import VertexShader, VertexShaderOutput, ShaderUtils
from math_utils import Vec3, Vec2

class StandardVertexShader(VertexShader):
    """Vertex shader estándar sin deformaciones"""
    
    def __init__(self):
        super().__init__("Standard Vertex Shader")
    
    def execute(self, vertex, uniforms):
        output = VertexShaderOutput()
        
        # Transformar posición al espacio de clip
        clip_pos, w = uniforms.mvp_matrix.transform_point(vertex.position)
        output.position = clip_pos
        output.w = w
        
        # Posición en espacio del mundo
        world_pos, _ = uniforms.model_matrix.transform_point(vertex.position)
        output.world_pos = world_pos
        
        # Normal en espacio del mundo (asumiendo escalado uniforme)
        output.normal = vertex.normal
        output.uv = vertex.uv
        output.color = Vec3(1, 1, 1)
        
        return output

class TwistVertexShader(VertexShader):
    """Vertex shader que aplica torsión al modelo"""
    
    def __init__(self):
        super().__init__("Twist Vertex Shader")
    
    def execute(self, vertex, uniforms):
        output = VertexShaderOutput()
        
        # Calcular ángulo de torsión basado en altura Y y tiempo
        twist_angle = vertex.position.y * uniforms.time * 0.5
        
        # Aplicar rotación en el plano XZ
        cos_twist = math.cos(twist_angle)
        sin_twist = math.sin(twist_angle)
        
        twisted_pos = Vec3(
            vertex.position.x * cos_twist - vertex.position.z * sin_twist,
            vertex.position.y,
            vertex.position.x * sin_twist + vertex.position.z * cos_twist
        )
        
        # Transformar al espacio de clip
        clip_pos, w = uniforms.mvp_matrix.transform_point(twisted_pos)
        output.position = clip_pos
        output.w = w
        
        # Posición en espacio del mundo
        world_pos, _ = uniforms.model_matrix.transform_point(twisted_pos)
        output.world_pos = world_pos
        
        # Rotar también la normal
        twisted_normal = Vec3(
            vertex.normal.x * cos_twist - vertex.normal.z * sin_twist,
            vertex.normal.y,
            vertex.normal.x * sin_twist + vertex.normal.z * cos_twist
        )
        output.normal = twisted_normal.normalize()
        
        output.uv = vertex.uv
        output.color = Vec3(1, 1, 1)
        
        return output

class ExplodeVertexShader(VertexShader):
    """Vertex shader que 'explota' los triángulos desde su centro"""
    
    def __init__(self):
        super().__init__("Explode Vertex Shader")
        self.triangle_centers = {}  # Cache para centros de triángulos
    
    def execute(self, vertex, uniforms):
        output = VertexShaderOutput()
        
        # Simular explosión moviendo vértices a lo largo de sus normales
        explosion_factor = math.sin(uniforms.time * 2.0) * 0.3
        exploded_pos = vertex.position + vertex.normal * explosion_factor
        
        # Transformar al espacio de clip
        clip_pos, w = uniforms.mvp_matrix.transform_point(exploded_pos)
        output.position = clip_pos
        output.w = w
        
        # Posición en espacio del mundo
        world_pos, _ = uniforms.model_matrix.transform_point(exploded_pos)
        output.world_pos = world_pos
        
        output.normal = vertex.normal
        output.uv = vertex.uv
        output.color = Vec3(1, 1, 1)
        
        return output

class NoiseVertexShader(VertexShader):
    """Vertex shader que aplica ruido a las posiciones"""
    
    def __init__(self):
        super().__init__("Noise Vertex Shader")
    
    def execute(self, vertex, uniforms):
        output = VertexShaderOutput()
        
        # Aplicar ruido 3D a la posición
        noise_pos = Vec3(
            vertex.position.x + uniforms.time * 0.1,
            vertex.position.y + uniforms.time * 0.15,
            vertex.position.z + uniforms.time * 0.12
        )
        
        noise_value = ShaderUtils.fbm_noise(noise_pos, octaves=3)
        noise_offset = vertex.normal * (noise_value - 0.5) * uniforms.noise_scale * 0.2
        
        noisy_pos = vertex.position + noise_offset
        
        # Transformar al espacio de clip
        clip_pos, w = uniforms.mvp_matrix.transform_point(noisy_pos)
        output.position = clip_pos
        output.w = w
        
        # Posición en espacio del mundo
        world_pos, _ = uniforms.model_matrix.transform_point(noisy_pos)
        output.world_pos = world_pos
        
        output.normal = vertex.normal
        output.uv = vertex.uv
        output.color = Vec3(1, 1, 1)
        
        return output

class WaveVertexShader(VertexShader):
    """Vertex shader que aplica ondas sinusoidales"""
    
    def __init__(self):
        super().__init__("Wave Vertex Shader")
    
    def execute(self, vertex, uniforms):
        output = VertexShaderOutput()
        
        # Aplicar ondas en Y basadas en posición X y Z + tiempo
        wave_x = math.sin(vertex.position.x * uniforms.wave_frequency + uniforms.time * 2.0)
        wave_z = math.cos(vertex.position.z * uniforms.wave_frequency + uniforms.time * 1.5)
        wave_offset = wave_x * wave_z * uniforms.wave_amplitude
        
        # Crear nueva posición con offset de onda
        new_pos = Vec3(
            vertex.position.x, 
            vertex.position.y + wave_offset, 
            vertex.position.z
        )
        
        # Transformar al espacio de clip
        clip_pos, w = uniforms.mvp_matrix.transform_point(new_pos)
        output.position = clip_pos
        output.w = w
        
        # Posición en espacio del mundo
        world_pos, _ = uniforms.model_matrix.transform_point(new_pos)
        output.world_pos = world_pos
        
        # Normal modificada para ondas (aproximación)
        # Calcular gradiente para normal más precisa
        dx = uniforms.wave_frequency * math.cos(vertex.position.x * uniforms.wave_frequency + uniforms.time * 2.0) * wave_z
        dz = -uniforms.wave_frequency * math.sin(vertex.position.z * uniforms.wave_frequency + uniforms.time * 1.5) * wave_x
        
        # Normal perturbada
        perturbed_normal = Vec3(-dx * uniforms.wave_amplitude, 1.0, -dz * uniforms.wave_amplitude).normalize()
        output.normal = perturbed_normal
        
        output.uv = vertex.uv
        output.color = Vec3(1, 1, 1)
        
        return output

class PulseVertexShader(VertexShader):
    """Vertex shader que hace pulsar el modelo"""
    
    def __init__(self):
        super().__init__("Pulse Vertex Shader")
    
    def execute(self, vertex, uniforms):
        output = VertexShaderOutput()
        
        # Factor de escala pulsante
        pulse = 1.0 + uniforms.pulse_strength * math.sin(uniforms.time * uniforms.pulse_speed)
        
        # Escalar desde el centro
        scaled_pos = vertex.position * pulse
        
        # Transformar al espacio de clip
        clip_pos, w = uniforms.mvp_matrix.transform_point(scaled_pos)
        output.position = clip_pos
        output.w = w
        
        # Posición en espacio del mundo
        world_pos, _ = uniforms.model_matrix.transform_point(scaled_pos)
        output.world_pos = world_pos
        
        output.normal = vertex.normal
        output.uv = vertex.uv
        output.color = Vec3(1, 1, 1)
        
        return output