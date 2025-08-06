"""
fragment_shaders.py
Implementaciones de fragment shaders - VERSIÓN SIMPLIFICADA
"""

import math
from math_utils import Vec3
from shader_core import FragmentShader, ShaderUtils

class MetallicFragmentShader(FragmentShader):
    """Fragment shader metálico avanzado - SHADER PRINCIPAL"""
    
    def __init__(self):
        super().__init__("Enhanced Metallic")
    
    def execute(self, fragment_input, uniforms, geometry_data=None):
        normal = fragment_input.normal
        view_dir = (uniforms.camera_pos - fragment_input.world_pos).normalize()
        light_dir = uniforms.light_dir
        
        # Sistema de iluminación múltiple
        light2_dir = Vec3(-0.4, 0.8, -0.5).normalize()
        light3_dir = Vec3(0.6, 0.3, 0.7).normalize()
        
        # Componente difusa con múltiples luces
        diffuse1 = max(0, normal.dot(light_dir)) * 0.5
        diffuse2 = max(0, normal.dot(light2_dir)) * 0.3
        diffuse3 = max(0, normal.dot(light3_dir)) * 0.2
        total_diffuse = diffuse1 + diffuse2 + diffuse3
        
        # Reflexión especular de alta calidad
        reflect_dir = (-light_dir).reflect(normal)
        spec_strength = max(0, view_dir.dot(reflect_dir))
        specular1 = pow(spec_strength, 128) * 1.5
        
        # Especular secundario
        reflect_dir2 = (-light2_dir).reflect(normal)
        spec_strength2 = max(0, view_dir.dot(reflect_dir2))
        specular2 = pow(spec_strength2, 64) * 0.8
        
        total_specular = specular1 + specular2
        
        # Efecto Fresnel avanzado
        fresnel = pow(1.0 - abs(normal.dot(view_dir)), 1.8)
        ambient_reflection = fresnel * 0.6
        env_reflection = fresnel * 0.4
        
        # Colores metálicos dinámicos
        base_metallic = (0.85, 0.85, 0.95)  # Plata brillante
        edge_metallic = (0.95, 0.90, 0.75)  # Dorado en bordes
        
        # Interpolación de color basada en Fresnel
        metal_r = ShaderUtils.lerp(base_metallic[0], edge_metallic[0], fresnel * 0.4)
        metal_g = ShaderUtils.lerp(base_metallic[1], edge_metallic[1], fresnel * 0.4)
        metal_b = ShaderUtils.lerp(base_metallic[2], edge_metallic[2], fresnel * 0.4)
        
        # Combinar todos los componentes de iluminación
        ambient = 0.18
        total_intensity = ambient + total_diffuse + total_specular + ambient_reflection + env_reflection
        
        # Aplicar intensidad a colores metálicos
        final_r = metal_r * total_intensity
        final_g = metal_g * total_intensity
        final_b = metal_b * total_intensity
        
        return ShaderUtils.rgb_to_tuple(final_r, final_g, final_b)

class PsychedelicFragmentShader(FragmentShader):
    """Fragment shader con colores psicodélicos dinámicos"""
    
    def __init__(self):
        super().__init__("Psychedelic Colors")
    
    def execute(self, fragment_input, uniforms, geometry_data=None):
        # Usar posición mundial y tiempo para efectos dinámicos
        x = fragment_input.world_pos.x
        y = fragment_input.world_pos.y
        z = fragment_input.world_pos.z
        t = uniforms.time
        
        # Ondas de color complejas con diferentes frecuencias
        r_wave = math.sin(x * 4 + t * 3) + math.cos(y * 2 + t * 1.5)
        g_wave = math.sin(y * 3 + t * 2.5) + math.cos(z * 4 + t * 2)
        b_wave = math.sin(z * 2 + t * 4) + math.cos(x * 3 + t * 1.8)
        
        # Normalizar ondas
        r = (r_wave + 2) * 0.25  # Rango 0-1
        g = (g_wave + 2) * 0.25
        b = (b_wave + 2) * 0.25
        
        # Añadir ruido procedural para textura
        noise_x = ShaderUtils.fbm_noise(x * uniforms.noise_scale, y * uniforms.noise_scale)
        noise_y = ShaderUtils.fbm_noise(y * uniforms.noise_scale, z * uniforms.noise_scale)
        noise_z = ShaderUtils.fbm_noise(z * uniforms.noise_scale, x * uniforms.noise_scale)
        
        # Mezclar ruido con ondas
        r += noise_x * 0.4
        g += noise_y * 0.4
        b += noise_z * 0.4
        
        # Efecto de pulsación temporal
        pulse = (math.sin(t * 2) + 1) * 0.5
        intensity_boost = 0.7 + pulse * 0.3
        
        r *= intensity_boost
        g *= intensity_boost
        b *= intensity_boost
        
        # Saturar y añadir brillo
        r = ShaderUtils.clamp(r, 0.1, 1.0)
        g = ShaderUtils.clamp(g, 0.1, 1.0)
        b = ShaderUtils.clamp(b, 0.1, 1.0)
        
        # Iluminación básica para mantener forma 3D
        normal = fragment_input.normal
        light_intensity = max(0.3, normal.dot(uniforms.light_dir))
        
        final_r = r * light_intensity
        final_g = g * light_intensity
        final_b = b * light_intensity
        
        return ShaderUtils.rgb_to_tuple(final_r, final_g, final_b)