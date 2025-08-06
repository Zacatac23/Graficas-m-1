"""
vertex_shaders.py
Implementaciones de vertex shaders - VERSIÓN SIMPLIFICADA
"""

import math
from math_utils import Vec2, Vec3
from shader_core import VertexShader, VertexShaderOutput, ShaderUtils

class DisplacementVertexShader(VertexShader):
    """Vertex shader con desplazamiento procedural dinámico"""
    
    def __init__(self):
        super().__init__("Procedural Displacement")
    
    def execute(self, vertex, uniforms):
        output = VertexShaderOutput()
        
        # Generar ruido procedural complejo
        pos = vertex.position
        time = uniforms.time
        
        # Múltiples capas de ruido con diferentes escalas
        noise1 = ShaderUtils.fbm_noise(pos.x * 2.0, pos.z * 2.0) 
        noise2 = ShaderUtils.fbm_noise(pos.y * 3.0 + time, pos.x * 1.5)
        noise3 = ShaderUtils.fbm_noise(pos.z * 4.0, pos.y * 2.5 + time * 0.7)
        
        # Combinar ruidos con pesos diferentes
        combined_noise = noise1 * 0.5 + noise2 * 0.3 + noise3 * 0.2
        
        # Modulación temporal para animación
        time_modulation = math.sin(time * 0.8) * 0.5 + 0.5
        displacement_strength = 0.2 * time_modulation
        
        # Desplazamiento direccional inteligente
        # Mezclar desplazamiento normal y tangencial
        normal_displacement = combined_noise * displacement_strength
        
        # Desplazamiento tangencial para efectos orgánicos
        tangent = Vec3(1, 0, 0)
        if abs(vertex.normal.dot(tangent)) > 0.9:
            tangent = Vec3(0, 1, 0)
        
        bitangent = vertex.normal.cross(tangent).normalize()
        tangent = bitangent.cross(vertex.normal).normalize()
        
        tangent_noise = ShaderUtils.noise(pos.x + time * 0.5, pos.z + time * 0.3)
        bitangent_noise = ShaderUtils.noise(pos.y + time * 0.4, pos.x + time * 0.6)
        
        # Aplicar desplazamiento complejo
        displaced_pos = Vec3(
            pos.x + vertex.normal.x * normal_displacement + tangent.x * tangent_noise * 0.1,
            pos.y + vertex.normal.y * normal_displacement + tangent.y * tangent_noise * 0.1,  
            pos.z + vertex.normal.z * normal_displacement + tangent.z * tangent_noise * 0.1
        )
        
        # Transformar posición desplazada
        world_pos, _ = uniforms.model_matrix.transform_point(displaced_pos)
        view_pos, _ = uniforms.view_matrix.transform_point(world_pos)
        clip_pos, w = uniforms.projection_matrix.transform_point(view_pos)
        
        output.position = clip_pos
        output.w = w
        output.world_pos = world_pos
        
        # Recalcular normal perturbada
        epsilon = 0.01
        
        # Calcular gradientes para normal correcta
        noise_dx = ShaderUtils.fbm_noise((pos.x + epsilon) * 2.0, pos.z * 2.0) - noise1
        noise_dy = ShaderUtils.fbm_noise(pos.x * 2.0, (pos.z + epsilon) * 2.0) - noise1
        
        # Crear normal perturbada
        perturbed_normal = Vec3(
            vertex.normal.x - noise_dx * 2.0,
            vertex.normal.y,
            vertex.normal.z - noise_dy * 2.0
        ).normalize()
        
        # Mezclar normal original con perturbada
        final_normal = (vertex.normal * 0.4 + perturbed_normal * 0.6).normalize()
        output.normal = uniforms.model_matrix.transform_vector(final_normal).normalize()
        
        output.uv = vertex.uv
        
        # Color que refleja la intensidad del desplazamiento
        displacement_intensity = abs(combined_noise) + time_modulation * 0.5
        
        # Paleta de colores orgánica
        r = int(120 + 135 * displacement_intensity)  # Rojo terra cotta
        g = int(80 + 100 * displacement_intensity)   # Verde musgo  
        b = int(60 + 80 * displacement_intensity)    # Azul profundo
        
        output.color = (
            min(255, max(0, r)),
            min(255, max(0, g)), 
            min(255, max(0, b))
        )
        
        return output

class WaveVertexShader(VertexShader):
    """Vertex shader con ondas oceánicas dinámicas"""
    
    def __init__(self):
        super().__init__("Dynamic Wave")
    
    def execute(self, vertex, uniforms):
        output = VertexShaderOutput()
        
        # Ondas múltiples realistas
        wave_x = math.sin(vertex.position.x * uniforms.wave_frequency + uniforms.time * 2.0) * uniforms.wave_amplitude
        wave_z = math.cos(vertex.position.z * uniforms.wave_frequency * 1.3 + uniforms.time * 1.7) * uniforms.wave_amplitude * 0.8
        wave_y = math.sin((vertex.position.x + vertex.position.z) * uniforms.wave_frequency * 0.7 + uniforms.time * 2.5) * uniforms.wave_amplitude * 0.6
        
        # Aplicar deformación
        modified_pos = Vec3(
            vertex.position.x + wave_x * 0.3,
            vertex.position.y + wave_y,
            vertex.position.z + wave_z * 0.3
        )
        
        # Transformar posición modificada
        world_pos, _ = uniforms.model_matrix.transform_point(modified_pos)
        view_pos, _ = uniforms.view_matrix.transform_point(world_pos)
        clip_pos, w = uniforms.projection_matrix.transform_point(view_pos)
        
        output.position = clip_pos
        output.w = w
        output.world_pos = world_pos
        
        # Calcular normal basada en gradiente de ondas
        dx = math.cos(vertex.position.x * uniforms.wave_frequency + uniforms.time * 2.0) * uniforms.wave_amplitude * uniforms.wave_frequency
        dz = -math.sin(vertex.position.z * uniforms.wave_frequency * 1.3 + uniforms.time * 1.7) * uniforms.wave_amplitude * uniforms.wave_frequency * 1.3
        
        # Crear vectores tangentes
        tangent_x = Vec3(1 + dx * 0.3, 0, 0).normalize()
        tangent_z = Vec3(0, 0, 1 + dz * 0.3).normalize()
        wave_normal = tangent_x.cross(tangent_z).normalize()
        
        # Mezclar normal original con normal de onda
        combined_normal = (vertex.normal * 0.6 + wave_normal * 0.4).normalize()
        output.normal = uniforms.model_matrix.transform_vector(combined_normal).normalize()
        
        output.uv = vertex.uv
        
        # Color oceánico que refleja el movimiento
        wave_intensity = (wave_x + wave_y + wave_z) / (uniforms.wave_amplitude * 3) + 1
        wave_intensity *= 0.5
        
        output.color = (
            int(30 + 100 * wave_intensity),   # Azul verdoso
            int(120 + 135 * wave_intensity),  # Verde agua
            int(180 + 75 * wave_intensity)    # Azul océano
        )
        
        return output