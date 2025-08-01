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

class PsychedelicFragmentShader(FragmentShader):
    """Fragment shader psicodélico con colores animados"""
    
    def __init__(self):
        super().__init__("Psychedelic Fragment Shader")
    
    def execute(self, fragment_input, uniforms, texture_loader):
        # Generar colores basados en posición y tiempo
        x = fragment_input.world_pos.x
        y = fragment_input.world_pos.y
        z = fragment_input.world_pos.z
        t = uniforms.time
        
        # Múltiples capas de ondas sinusoidales
        r = (math.sin(x * 3.0 + t * 2.0) + 
             math.cos(y * 2.5 + t * 1.7) + 
             math.sin(z * 4.0 + t * 2.3)) / 3.0
        
        g = (math.cos(x * 2.7 + t * 1.8) + 
             math.sin(y * 3.2 + t * 2.1) + 
             math.cos(z * 2.1 + t * 1.9)) / 3.0
        
        b = (math.sin(x * 3.5 + t * 2.4) + 
             math.cos(y * 1.8 + t * 1.6) + 
             math.sin(z * 2.9 + t * 2.2)) / 3.0
        
        # Normalizar a [0,1] y intensificar
        r = (r + 1.0) / 2.0 * 0.9 + 0.1
        g = (g + 1.0) / 2.0 * 0.9 + 0.1
        b = (b + 1.0) / 2.0 * 0.9 + 0.1
        
        final_color = Vec3(r, g, b)
        return ShaderUtils.vec3_to_rgb(final_color)

class RimLightFragmentShader(FragmentShader):
    """Fragment shader con efecto de rim lighting"""
    
    def __init__(self):
        super().__init__("Rim Light Fragment Shader")
    
    def execute(self, fragment_input, uniforms, texture_loader):
        # Color base
        if texture_loader and texture_loader.texture:
            base_color = Vec3(*texture_loader.sample_texture(fragment_input.uv.u, fragment_input.uv.v))
            base_color = Vec3(base_color.x/255.0, base_color.y/255.0, base_color.z/255.0)
        else:
            base_color = Vec3(0.2, 0.4, 0.8)
        
        # Calcular rim lighting
        normal = fragment_input.normal.normalize()
        view_dir = (uniforms.camera_pos - fragment_input.world_pos).normalize()
        
        # Rim factor - más fuerte en los bordes
        rim = 1.0 - max(0, normal.dot(view_dir))
        rim = rim ** uniforms.rim_power
        
        # Color de rim (azul brillante)
        rim_color = Vec3(0.3, 0.7, 1.0) * rim * 0.8
        
        # Iluminación básica
        light_dir = (uniforms.light_pos - fragment_input.world_pos).normalize()
        diff = max(0.3, normal.dot(light_dir))  # Mínimo de iluminación
        
        # Combinar colores
        final_color = base_color * diff + rim_color
        
        return ShaderUtils.vec3_to_rgb(final_color)

class HologramFragmentShader(FragmentShader):
    """Fragment shader de efecto holograma"""
    
    def __init__(self):
        super().__init__("Hologram Fragment Shader")
    
    def execute(self, fragment_input, uniforms, texture_loader):
        # Color base cyan/azul del holograma
        holo_color = Vec3(0.2, 0.8, 1.0)
        
        # Efecto de líneas horizontales
        y_screen = fragment_input.screen_pos.y
        line_pattern = math.sin(y_screen * 0.3 + uniforms.time * 8.0)
        line_intensity = (line_pattern + 1) / 2  # [0,1]
        
        # Efecto de fresnel para transparencia en bordes
        normal = fragment_input.normal.normalize()
        view_dir = (uniforms.camera_pos - fragment_input.world_pos).normalize()
        fresnel = (1.0 - normal.dot(view_dir)) ** uniforms.fresnel_power
        
        # Parpadeo temporal
        flicker = 0.7 + 0.3 * math.sin(uniforms.time * 12.0)
        
        # Efecto de ruido para variación
        noise_pos = Vec3(
            fragment_input.world_pos.x * 5.0,
            fragment_input.world_pos.y * 5.0 + uniforms.time,
            fragment_input.world_pos.z * 5.0
        )
        noise = ShaderUtils.noise_3d(noise_pos)
        
        # Combinar efectos
        intensity = line_intensity * fresnel * flicker * (0.5 + noise * 0.5) * 0.8
        final_color = holo_color * intensity
        
        return ShaderUtils.vec3_to_rgb(final_color)

class StainedGlassFragmentShader(FragmentShader):
    """Fragment shader de efecto vitral"""
    
    def __init__(self):
        super().__init__("Stained Glass Fragment Shader")
    
    def execute(self, fragment_input, uniforms, texture_loader):
        # Usar coordenadas UV para crear patrón de vitral
        u, v = fragment_input.uv.u, fragment_input.uv.v
        
        # Crear celdas de Voronoi simplificadas
        cell_u = math.floor(u * 8.0) / 8.0
        cell_v = math.floor(v * 8.0) / 8.0
        
        # Color base de cada celda usando hash
        cell_hash = ShaderUtils.noise_3d(Vec3(cell_u * 100, cell_v * 100, 0))
        
        # Generar colores vibrantes
        hue = cell_hash * 6.28  # 0 a 2π
        saturation = 0.8
        value = 0.9
        
        # Conversión HSV a RGB simplificada
        c = value * saturation
        x = c * (1 - abs((hue / 1.047) % 2 - 1))  # 1.047 ≈ π/3
        m = value - c
        
        if hue < 1.047:      # 0 a 60°
            r, g, b = c, x, 0
        elif hue < 2.094:    # 60 a 120°
            r, g, b = x, c, 0
        elif hue < 3.141:    # 120 a 180°
            r, g, b = 0, c, x
        elif hue < 4.188:    # 180 a 240°
            r, g, b = 0, x, c
        elif hue < 5.235:    # 240 a 300°
            r, g, b = x, 0, c
        else:                # 300 a 360°
            r, g, b = c, 0, x
        
        final_color = Vec3(r + m, g + m, b + m)
        
        # Añadir bordes oscuros entre celdas
        edge_u = abs(u * 8.0 - math.floor(u * 8.0 + 0.5))
        edge_v = abs(v * 8.0 - math.floor(v * 8.0 + 0.5))
        edge_factor = ShaderUtils.smoothstep(0.4, 0.5, min(edge_u, edge_v))
        
        final_color = final_color * edge_factor
        
        return ShaderUtils.vec3_to_rgb(final_color)

class MetallicFragmentShader(FragmentShader):
    """Fragment shader con efecto metálico"""
    
    def __init__(self):
        super().__init__("Metallic Fragment Shader")
    
    def execute(self, fragment_input, uniforms, texture_loader):
        # Color base metálico
        metallic_color = Vec3(0.7, 0.7, 0.8)
        
        # Iluminación especular intensa
        normal = fragment_input.normal.normalize()
        light_dir = (uniforms.light_pos - fragment_input.world_pos).normalize()
        view_dir = (uniforms.camera_pos - fragment_input.world_pos).normalize()
        
        # Reflexión perfecta
        reflect_dir = light_dir * -1 + normal * (2 * normal.dot(light_dir))
        spec = max(0, view_dir.dot(reflect_dir)) ** 64.0  # Especular muy concentrado
        
        # Fresnel para reflexión en bordes
        fresnel = (1.0 - normal.dot(view_dir)) ** 2.0
        
        # Ambiente mínimo
        ambient = metallic_color * 0.1
        
        # Combinar efectos
        final_color = ambient + metallic_color * spec + Vec3(1, 1, 1) * fresnel * 0.3
        
        return ShaderUtils.vec3_to_rgb(final_color)