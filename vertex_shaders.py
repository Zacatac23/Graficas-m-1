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
