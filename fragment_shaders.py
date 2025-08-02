"""
fragment_shaders.py
Implementaciones de diferentes fragment shaders
"""

import math
from shader_core import FragmentShader, ShaderUtils
from math_utils import Vec3

class StandardFragmentShader(FragmentShader):
    """Fragment shader estándar con iluminación Phong"""
    
    def __init__(self):
        super().__init__("Standard Phong Fragment Shader")
    
    def execute(self, fragment_input, uniforms, texture_loader):
        # Color base de la textura
        if texture_loader and texture_loader.texture:
            base_color = Vec3(*texture_loader.sample_texture(fragment_input.uv.u, fragment_input.uv.v))
            base_color = Vec3(base_color.x/255.0, base_color.y/255.0, base_color.z/255.0)
        else:
            base_color = Vec3(0.7, 0.7, 0.7)
        
        # Iluminación Phong
        normal = fragment_input.normal.normalize()
        light_dir = (uniforms.light_pos - fragment_input.world_pos).normalize()
        view_dir = (uniforms.camera_pos - fragment_input.world_pos).normalize()
        
        # Ambiente
        ambient = base_color * uniforms.ambient_strength
        
        # Difusa
        diff = max(0, normal.dot(light_dir))
        diffuse = base_color * diff
        
        # Especular
        reflect_dir = light_dir * -1 + normal * (2 * normal.dot(light_dir))
        spec = max(0, view_dir.dot(reflect_dir)) ** uniforms.shininess
        specular = uniforms.light_color * (spec * uniforms.specular_strength)
        
        # Color final
        final_color = ambient + diffuse + specular
        
        return ShaderUtils.vec3_to_rgb(final_color)

class ToonFragmentShader(FragmentShader):
    """Fragment shader de estilo cartoon/toon"""
    
    def __init__(self):
        super().__init__("Toon Fragment Shader")
    
    def execute(self, fragment_input, uniforms, texture_loader):
        # Color base
        if texture_loader and texture_loader.texture:
            base_color = Vec3(*texture_loader.sample_texture(fragment_input.uv.u, fragment_input.uv.v))
            base_color = Vec3(base_color.x/255.0, base_color.y/255.0, base_color.z/255.0)
        else:
            base_color = Vec3(0.7, 0.3, 0.8)
        
        # Calcular iluminación
        normal = fragment_input.normal.normalize()
        light_dir = (uniforms.light_pos - fragment_input.world_pos).normalize()
        
        # Toon shading - cuantizar la iluminación
        intensity = normal.dot(light_dir)
        
        if intensity > 0.8:
            toon_intensity = 1.0
        elif intensity > 0.5:
            toon_intensity = 0.8
        elif intensity > 0.2:
            toon_intensity = 0.5
        else:
            toon_intensity = 0.3
        
        # Aplicar intensidad cuantizada
        final_color = base_color * toon_intensity
        
        return ShaderUtils.vec3_to_rgb(final_color)
