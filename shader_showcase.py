import os
import time
from rasterizer import ShaderRasterizer

class ShaderShowcase:
    """Clase para crear showcases y demostraciones de shaders"""
    
    def __init__(self):
        self.showcase_configs = self._define_showcase_configs()
    
    def _define_showcase_configs(self):
        """Definir configuraciones preestablecidas de shaders interesantes"""
        return [
            {
                "name": "phong_standard",
                "vertex": "standard",
                "fragment": "standard",
                "description": "Iluminación Phong Clásica",
                "params": {
                    "ambient_strength": 0.2,
                    "specular_strength": 0.8,
                    "shininess": 64.0
                }
            },
            {
                "name": "wave_toon",
                "vertex": "wave",
                "fragment": "toon",
                "description": "Ondas Sinusoidales + Toon Shading",
                "params": {
                    "wave_frequency": 2.5,
                    "wave_amplitude": 0.2
                }
            },
           
        ]
    
    def create_main_showcase(self, obj_filename, texture_filename=None, output_dir="output"):
        """Crear showcase principal con los 4 shaders más impresionantes"""
        print("🎨 === SHADER SHOWCASE PRINCIPAL ===")
        print("Creando demostración de 4 shaders únicos...")
        
        # Seleccionar los 4 más interesantes
        main_configs = self.showcase_configs[:4]
        
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        base_name = os.path.splitext(os.path.basename(obj_filename))[0]
        
        for i, config in enumerate(main_configs, 1):
            print(f"\n🎬 Renderizando {i}/4: {config['description']}")
            
            # Crear rasterizador
            rasterizer = ShaderRasterizer(800, 600)
            
            # Cargar modelo
            if not rasterizer.load_model(obj_filename, texture_filename):
                print(f"❌ Error cargando modelo para {config['name']}")
                continue
            
            # Configurar shaders y parámetros
            rasterizer.set_shaders(config["vertex"], config["fragment"])
            rasterizer.configure_shader_parameters(**config["params"])
            
            # Renderizar
            rasterizer.render_model("medium")
            
            # Guardar archivos
            bmp_filename = os.path.join(output_dir, f"{base_name}_{config['name']}.bmp")
            png_filename = os.path.join(output_dir, f"{base_name}_{config['name']}.png")
            
            rasterizer.save_image(bmp_filename)
            rasterizer.save_image(png_filename)
            
            print(f"✅ Shader completado: {config['name']}")
        
        print(f"\n🎉 SHOWCASE PRINCIPAL COMPLETADO!")
        print(f"📁 Archivos generados en '{output_dir}':")
        for config in main_configs:
            print(f"   - {base_name}_{config['name']}.bmp")
            print(f"   - {base_name}_{config['name']}.png")
    
    def create_full_comparison(self, obj_filename, texture_filename=None, output_dir="comparison"):
        """Crear comparación completa de todos los shaders"""
        print("🎯 === COMPARACIÓN COMPLETA DE SHADERS ===")
        
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        base_name = os.path.splitext(os.path.basename(obj_filename))[0]
        
        for i, config in enumerate(self.showcase_configs, 1):
            print(f"📊 Renderizando {i}/{len(self.showcase_configs)}: {config['description']}")
            
            rasterizer = ShaderRasterizer(600, 600)  # Más pequeño para comparación
            
            if rasterizer.load_model(obj_filename, texture_filename):
                rasterizer.set_shaders(config["vertex"], config["fragment"])
                rasterizer.configure_shader_parameters(**config["params"])
                rasterizer.render_model("medium")
                
                filename = os.path.join(output_dir, f"{base_name}_{config['name']}.png")
                rasterizer.save_image(filename)
        
        print(f"✅ Comparación completada: {len(self.showcase_configs)} shaders generados")
    
    def create_animation_sequence(self, obj_filename, texture_filename=None, 
                                frames=12, output_dir="animation"):
        """Crear secuencia de animación con shaders animados"""
        print("🎬 === SECUENCIA DE ANIMACIÓN ===")
        
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        base_name = os.path.splitext(os.path.basename(obj_filename))[0]
        
        # Usar shaders animados
        animated_configs = [
            ("wave", "psychedelic", {"wave_frequency": 2.0, "wave_amplitude": 0.15}),
            ("pulse", "hologram", {"pulse_speed": 3.0, "fresnel_power": 2.5}),
            ("twist", "rim", {"rim_power": 2.0}),
            ("noise", "toon", {"noise_scale": 1.0})
        ]
        
        for config_idx, (vertex, fragment, params) in enumerate(animated_configs):
            print(f"\n🎞️  Secuencia {config_idx + 1}: {vertex} + {fragment}")
            
            for frame in range(frames):
                print(f"📽️  Frame {frame + 1}/{frames}")
                
                rasterizer = ShaderRasterizer(400, 400)
                
                if rasterizer.load_model(obj_filename, texture_filename):
                    rasterizer.set_shaders(vertex, fragment)
                    rasterizer.configure_shader_parameters(**params)
                    
                    # Simular tiempo para animación
                    rasterizer.uniforms.time = frame * 0.3
                    
                    rasterizer.render_model("medium")
                    
                    filename = os.path.join(output_dir, 
                                          f"{base_name}_{vertex}_{fragment}_frame_{frame:02d}.png")
                    rasterizer.save_image(filename)
        
        print("🎞️  Secuencias de animación completadas!")
    
    def create_camera_angles_showcase(self, obj_filename, texture_filename=None, 
                                    shader_config=None, output_dir="camera_angles"):
        """Crear showcase con diferentes ángulos de cámara"""
        print("📷 === SHOWCASE DE ÁNGULOS DE CÁMARA ===")
        
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        base_name = os.path.splitext(os.path.basename(obj_filename))[0]
        
        # Usar configuración de shader específica o la primera por defecto
        if shader_config is None:
            shader_config = self.showcase_configs[1]  # Wave + Toon
        
        camera_angles = ["medium", "low_angle", "high_angle", "dutch", "close_up"]
        
        for angle in camera_angles:
            print(f"📸 Renderizando ángulo: {angle}")
            
            rasterizer = ShaderRasterizer(800, 600)
            
            if rasterizer.load_model(obj_filename, texture_filename):
                rasterizer.set_shaders(shader_config["vertex"], shader_config["fragment"])
                rasterizer.configure_shader_parameters(**shader_config["params"])
                rasterizer.render_model(angle)
                
                filename = os.path.join(output_dir, f"{base_name}_{angle}_{shader_config['name']}.png")
                rasterizer.save_image(filename)
        
        print("📷 Showcase de ángulos completado!")
    
    def interactive_shader_builder(self, obj_filename, texture_filename=None):
        """Constructor interactivo de shaders"""
        print("🔧 === CONSTRUCTOR INTERACTIVO DE SHADERS ===")
        
        rasterizer = ShaderRasterizer(800, 600)
        
        if not rasterizer.load_model(obj_filename, texture_filename):
            print("❌ Error cargando modelo")
            return
        
        available = rasterizer.get_available_shaders()
        
        while True:
            print("\n🎨 VERTEX SHADERS DISPONIBLES:")
            for i, vs in enumerate(available["vertex"], 1):
                print(f"   {i}. {vs}")
            
            print("\n🎨 FRAGMENT SHADERS DISPONIBLES:")
            for i, fs in enumerate(available["fragment"], 1):
                print(f"   {i}. {fs}")
            
            # Seleccionar shaders
            try:
                vs_choice = int(input("\nSelecciona vertex shader (número): ")) - 1
                fs_choice = int(input("Selecciona fragment shader (número): ")) - 1
                
                vertex_shader = available["vertex"][vs_choice]
                fragment_shader = available["fragment"][fs_choice]
                
                # Configurar y renderizar
                rasterizer.clear_buffers()
                rasterizer.set_shaders(vertex_shader, fragment_shader)
                rasterizer.render_model("medium")
                
                # Guardar
                filename = f"interactive_{vertex_shader}_{fragment_shader}"
                rasterizer.save_image(filename + ".png")
                rasterizer.save_image(filename + ".bmp")
                
                print(f"✅ Renderizado guardado: {filename}")
                
                if input("\n¿Continuar? (s/n): ").lower() != 's':
                    break
                    
            except (ValueError, IndexError):
                print("❌ Selección inválida")
            except KeyboardInterrupt:
                print("\n👋 Saliendo...")
                break
    
    def print_shader_documentation(self):
        """Imprimir documentación completa de shaders"""
        print("\n" + "="*60)
        print("📚 DOCUMENTACIÓN COMPLETA DE SHADERS")
        print("="*60)
        
        print("\n🔧 VERTEX SHADERS:")
        vertex_docs = {
            "standard": "Transformación MVP estándar sin deformaciones",
            "wave": "Deforma vértices con ondas sinusoidales animadas",
            "pulse": "Escala el modelo con pulsación temporal",
            "twist": "Aplica torsión progresiva basada en altura",
            "explode": "Desplaza vértices a lo largo de sus normales",
            "noise": "Perturba posiciones con ruido fractal 3D"
        }
        
        for name, desc in vertex_docs.items():
            print(f"   • {name.upper()}: {desc}")
        
        print("\n🎨 FRAGMENT SHADERS:")
        fragment_docs = {
            "standard": "Iluminación Phong completa (ambiente + difusa + especular)",
            "toon": "Shading cuantizado estilo cartoon/anime",
            "psychedelic": "Colores animados basados en ruido temporal",
            "rim": "Iluminación en bordes basada en ángulo de vista",
            "hologram": "Efecto holograma con líneas y fresnel",
            "stained_glass": "Patrón de vitral con celdas de color",
            "metallic": "Superficie metálica con reflexiones intensas"
        }
        
        for name, desc in fragment_docs.items():
            print(f"   • {name.upper()}: {desc}")
        
        print("\n⚙️  PARÁMETROS CONFIGURABLES:")
        params_docs = {
            "wave_frequency": "Frecuencia de las ondas (1.0 - 5.0)",
            "wave_amplitude": "Amplitud de las ondas (0.1 - 0.5)",
            "pulse_speed": "Velocidad de pulsación (1.0 - 8.0)",
            "pulse_strength": "Intensidad de pulsación (0.1 - 0.5)",
            "rim_power": "Concentración del rim light (1.0 - 5.0)",
            "fresnel_power": "Intensidad del efecto fresnel (1.0 - 5.0)",
            "noise_scale": "Escala del ruido (0.5 - 3.0)",
            "ambient_strength": "Intensidad de luz ambiente (0.1 - 0.5)",
            "specular_strength": "Intensidad especular (0.5 - 2.0)"
        }
        
        for param, desc in params_docs.items():
            print(f"   • {param}: {desc}")
        
        print("\n🎬 COMBINACIONES RECOMENDADAS:")
        for config in self.showcase_configs[:4]:
            print(f"   • {config['vertex'].upper()} + {config['fragment'].upper()}: {config['description']}")
        
        print("\n💡 CONSEJOS DE USO:")
        print("   • Cada vertex shader es compatible con cualquier fragment shader")
        print("   • Los shaders animados funcionan mejor con modelos complejos")
        print("   • Ajusta los parámetros para diferentes efectos visuales")
        print("   • Combina diferentes ángulos de cámara para mejores resultados")
        print("="*60)