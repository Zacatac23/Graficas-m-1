"""
main.py
Programa principal del sistema de renderizado 3D - VERSIÓN SIMPLIFICADA
"""

import os
import sys
from resterizer import ShaderRasterizer

def print_header():
    """Imprimir cabecera del programa"""
    print("🎨" + "="*58 + "🎨")
    print("    RENDERIZADOR 3D CON SHADERS SIMPLIFICADO")
    print("🎨" + "="*58 + "🎨")
    print("\n✨ CARACTERÍSTICAS:")
    print("   🎨 2 Vertex Shaders únicos")
    print("   🎭 2 Fragment Shaders avanzados")
    print("   📷 6 Ángulos de cámara diferentes")
    print("   📁 Exportación en BMP y PNG")
    print("   ⚙️  Parámetros configurables")

def get_model_files():
    """Solicitar archivos de modelo y textura"""
    print("\n📂 CONFIGURACIÓN DE ARCHIVOS:")
    
    # Archivo OBJ
    obj_filename = input("📝 Nombre del archivo OBJ: ").strip()
    if not obj_filename:
        print("⚠️  Usando archivo por defecto: model.obj")
        obj_filename = "model.obj"
    
    # Verificar existencia del archivo OBJ
    if not os.path.exists(obj_filename):
        print(f"❌ Archivo '{obj_filename}' no encontrado")
        return None, None
    
    # Archivo de textura (opcional)
    texture_filename = None
    texture_input = input("🖼️  Archivo de textura (opcional, Enter para omitir): ").strip()
    if texture_input:
        if os.path.exists(texture_input):
            texture_filename = texture_input
            print(f"✅ Textura encontrada: {texture_filename}")
        else:
            print(f"⚠️  Archivo de textura '{texture_input}' no encontrado - continuando sin textura")
    
    return obj_filename, texture_filename

def show_main_menu():
    """Mostrar menú principal"""
    print("\n🎯 OPCIONES DE RENDERIZADO:")
    print("1. 🎨 Renderizar shader específico")
    print("2. 🔧 Test básico (Metallic)")
    print("3. 📊 Comparación de todos los shaders")
    print("4. 📚 Ver información de shaders")
    print("5. ❌ Salir")

def render_specific_shader(obj_filename, texture_filename):
    """Renderizar un shader específico"""
    rasterizer = ShaderRasterizer(800, 600)
    
    if not rasterizer.load_model(obj_filename, texture_filename):
        print("❌ Error cargando modelo")
        return
    
    available = rasterizer.get_available_shaders()
    
    # Modo de configuración simplificado
    print("\n🎛️  MODO DE CONFIGURACIÓN:")
    print("   1. Solo Fragment Shader (Vertex = standard)")
    print("   2. Solo Vertex Shader (Fragment = metallic)")  
    print("   3. Configuración completa")
    
    mode_choice = input("Selecciona modo (1-3, Enter para completa): ").strip()
    
    vertex_shader = "displacement"  # NUEVO SHADER POR DEFECTO
    fragment_shader = "metallic"  # Por defecto metálico
    
    if mode_choice == "1":
        # Solo Fragment Shader
        print("\n🎨 FRAGMENT SHADERS:")
        print("   1. metallic - Superficie metálica avanzada")
        print("   2. psychedelic - Colores psicodélicos dinámicos")
        
        fs_choice = input("Selecciona fragment shader (1-2): ").strip()
        if fs_choice == "2":
            fragment_shader = "psychedelic"
        print(f"✅ Usando: Displacement Vertex + {fragment_shader.title()} Fragment")
        
    elif mode_choice == "2":
        # Solo Vertex Shader
        print("\n🎨 VERTEX SHADERS:")
        print("   1. displacement - Deformación procedural orgánica")
        print("   2. wave - Ondas oceánicas dinámicas")
        
        vs_choice = input("Selecciona vertex shader (1-2): ").strip()
        if vs_choice == "2":
            vertex_shader = "wave"
        print(f"✅ Usando: {vertex_shader.title()} Vertex + Metallic Fragment")
        
    else:
        # Configuración completa
        print("\n🎨 VERTEX SHADERS:")
        print("   1. displacement - Deformación procedural orgánica")
        print("   2. wave - Ondas oceánicas dinámicas")
        
        vs_choice = input("Selecciona vertex shader (1-2, Enter para displacement): ").strip()
        if vs_choice == "2":
            vertex_shader = "wave"
        
        print("\n🎨 FRAGMENT SHADERS:")
        print("   1. metallic - Superficie metálica avanzada")
        print("   2. psychedelic - Colores psicodélicos dinámicos")
        
        fs_choice = input("Selecciona fragment shader (1-2, Enter para metallic): ").strip()
        if fs_choice == "2":
            fragment_shader = "psychedelic"
        
        print(f"✅ Usando: {vertex_shader.title()} Vertex + {fragment_shader.title()} Fragment")

    try:
        # Configurar shaders
        rasterizer.set_shaders(vertex_shader, fragment_shader)
        
        # Configurar parámetros específicos
        print("\n⚙️  CONFIGURAR PARÁMETROS (Enter para usar valores por defecto):")
        
        if vertex_shader == "wave":
            frequency = input("   🌊 Wave frequency (2.5): ").strip()
            if frequency: 
                rasterizer.configure_shader_parameters(wave_frequency=float(frequency))
            
            amplitude = input("   📏 Wave amplitude (0.1): ").strip()
            if amplitude:
                rasterizer.configure_shader_parameters(wave_amplitude=float(amplitude))
        
        if fragment_shader == "psychedelic":
            noise = input("   🎨 Noise scale (5.0): ").strip()
            if noise:
                rasterizer.configure_shader_parameters(noise_scale=float(noise))
        
        # Seleccionar ángulo de cámara
        print("\n📷 ÁNGULOS DE CÁMARA:")
        angles = ["medium", "low_angle", "high_angle", "dutch", "close_up", "orbit"]
        angle_descriptions = [
            "Medium - Vista equilibrada estándar",
            "Low Angle - Vista desde abajo (dramática)",
            "High Angle - Vista desde arriba (overview)",
            "Dutch - Vista inclinada (artística)",
            "Close Up - Acercamiento detallado",
            "Orbit - Rotación automática (animada)"
        ]
        
        for i, (angle, desc) in enumerate(zip(angles, angle_descriptions), 1):
            print(f"   {i}. {desc}")
        
        angle_choice = input(f"Selecciona ángulo (1-{len(angles)}, Enter para medium): ").strip()
        camera_angle = angles[int(angle_choice) - 1] if angle_choice and angle_choice.isdigit() else "medium"
        
        # Renderizar
        print(f"\n🎬 Renderizando: {vertex_shader} + {fragment_shader} ({camera_angle})")
        rasterizer.render_model(camera_angle)
        
        # Guardar
        base_name = os.path.splitext(os.path.basename(obj_filename))[0]
        filename = f"{base_name}_{vertex_shader}_{fragment_shader}_{camera_angle}"
        
        rasterizer.save_image(filename + ".bmp")
        rasterizer.save_image(filename + ".png")
        
        print(f"✅ Renderizado completado: {filename}")
        
    except (ValueError, IndexError) as e:
        print(f"❌ Error en selección: {e}")

def test_basic_render(obj_filename, texture_filename):
    """Test básico con shader metálico"""
    print("\n🔧 EJECUTANDO TEST BÁSICO CON SHADER METÁLICO...")
    
    rasterizer = ShaderRasterizer(400, 300)
    
    if not rasterizer.load_model(obj_filename, texture_filename):
        print("❌ Error cargando modelo")
        return
    
    # Usar shaders por defecto (displacement + metallic)
    rasterizer.set_shaders("displacement", "metallic")
    
    # Renderizar con cámara medium
    rasterizer.render_model("medium")
    
    # Guardar resultado
    rasterizer.save_image("test_metallic.png")
    print("✅ Test completado: test_metallic.png")

def render_all_combinations(obj_filename, texture_filename):
    """Renderizar todas las combinaciones posibles"""
    print("\n🎨 GENERANDO TODAS LAS COMBINACIONES DE SHADERS...")
    print("📊 Total: 2 vertex × 2 fragment = 4 combinaciones")
    
    rasterizer = ShaderRasterizer(600, 450)
    
    if not rasterizer.load_model(obj_filename, texture_filename):
        print("❌ Error cargando modelo")
        return
    
    vertex_shaders = ["displacement", "wave"]
    fragment_shaders = ["metallic", "psychedelic"]
    base_name = os.path.splitext(os.path.basename(obj_filename))[0]
    
    combination_count = 0
    
    for vs in vertex_shaders:
        for fs in fragment_shaders:
            combination_count += 1
            print(f"\n🎬 Combinación {combination_count}/4: {vs} + {fs}")
            
            # Configurar shaders
            rasterizer.set_shaders(vs, fs)
            
            # Configurar parámetros por defecto
            if vs == "wave":
                rasterizer.configure_shader_parameters(wave_frequency=2.5, wave_amplitude=0.1)
            if fs == "psychedelic":
                rasterizer.configure_shader_parameters(noise_scale=5.0)
            
            # Renderizar
            rasterizer.render_model("medium")
            
            # Guardar
            filename = f"{base_name}_combo_{vs}_{fs}"
            rasterizer.save_image(filename + ".bmp")
            rasterizer.save_image(filename + ".png")
            print(f"✅ Guardado: {filename}")
    
    print(f"\n🎉 ¡Todas las {combination_count} combinaciones completadas!")

def show_shader_info(obj_filename, texture_filename):
    """Mostrar información detallada de shaders"""
    rasterizer = ShaderRasterizer(800, 600)
    
    if obj_filename and rasterizer.load_model(obj_filename, texture_filename):
        print("✅ Modelo cargado correctamente")
    else:
        print("⚠️  Trabajando sin modelo")
    
    available = rasterizer.get_available_shaders()
    
    print("\n📊 INFORMACIÓN DEL SISTEMA DE SHADERS SIMPLIFICADO:")
    
    print(f"\n🎨 VERTEX SHADERS ({len(available['vertex'])}):")
    print("   • displacement - Deformación procedural orgánica")
    print("     └ Iluminación: Sí")
    print("     └ Animación: Sí (ruido temporal)")
    print("     └ Deformación: Sí (múltiples capas de ruido)")
    print("     └ Efectos: Normal perturbada, tangencial")
    
    print("   • wave - Ondas oceánicas dinámicas")
    print("     └ Iluminación: Sí")
    print("     └ Animación: Sí (temporal)")
    print("     └ Deformación: Sí (ondas múltiples)")
    print("     └ Parámetros: wave_frequency, wave_amplitude")
    
    print(f"\n🎭 FRAGMENT SHADERS ({len(available['fragment'])}):")
    print("   • metallic - Superficie metálica avanzada (PRINCIPAL)")
    print("     └ Iluminación: Múltiple (3 luces)")
    print("     └ Efectos: Fresnel, reflexión especular")
    print("     └ Colores: Plata → Dorado")
    
    print("   • psychedelic - Colores psicodélicos dinámicos")
    print("     └ Iluminación: Básica")
    print("     └ Efectos: Ondas de color, ruido procedural")
    print("     └ Animación: Pulsación temporal")
    print("     └ Parámetros: noise_scale")
    
    print("\n⚙️  COMBINACIONES RECOMENDADAS:")
    print("   🏆 displacement + metallic - Metal orgánico deformado")
    print("   🌊 wave + metallic - Metal líquido oceánico")
    print("   🎨 displacement + psychedelic - Caos orgánico psicodélico")
    print("   🌈 wave + psychedelic - Océano psicodélico (EXTREMO)")

    
    # Mostrar información técnica
    try:
        info = rasterizer.get_shader_info()
        print(f"\n🔧 CONFIGURACIÓN ACTUAL:")
        print(f"   Vertex: {info['current_vertex']}")
        print(f"   Fragment: {info['current_fragment']}")
        print("   Parámetros disponibles:")
        for key, value in info['uniforms'].items():
            print(f"     • {key}: {value}")
    except Exception as e:
        print(f"ℹ️  Información detallada no disponible: {e}")

def main():
    """Función principal"""
    try:
        print_header()
        
        # Obtener archivos
        obj_filename, texture_filename = get_model_files()
        
        while True:
            show_main_menu()
            
            try:
                choice = input("\nSelecciona una opción (1-5): ").strip()
                
                if choice == "1":
                    if not obj_filename:
                        print("❌ Se requiere un archivo OBJ válido")
                        continue
                    render_specific_shader(obj_filename, texture_filename)
                
                elif choice == "2":
                    if not obj_filename:
                        print("❌ Se requiere un archivo OBJ válido")
                        continue
                    test_basic_render(obj_filename, texture_filename)
                
                elif choice == "3":
                    if not obj_filename:
                        print("❌ Se requiere un archivo OBJ válido")
                        continue
                    render_all_combinations(obj_filename, texture_filename)
                
                elif choice == "4":
                    show_shader_info(obj_filename, texture_filename)
                
                elif choice == "5":
                    print("\n👋 ¡Gracias por usar el renderizador de shaders!")
                    break
                
                else:
                    print("❌ Opción inválida. Por favor selecciona 1-5.")
                
                if choice in ["1", "2", "3"]:
                    print(f"\n✅ Operación completada exitosamente!")
                    continue_choice = input("¿Realizar otra operación? (s/n): ").lower()
                    if continue_choice != 's':
                        break
                    
            except KeyboardInterrupt:
                print("\n\n👋 Programa interrumpido por el usuario")
                break
            except Exception as e:
                print(f"\n❌ Error inesperado: {e}")
                continue
        
    except Exception as e:
        print(f"❌ Error crítico: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🎓 RENDERIZADOR 3D SIMPLIFICADO")
    print("="*60)
    
    # Ejecutar programa principal
    exit_code = main()
    
    print("\n" + "="*60)
    print("🎉 ¡PROGRAMA FINALIZADO!")
    print("="*60)
    print("\n🎨 CARACTERÍSTICAS IMPLEMENTADAS:")
    print("   • 2 Vertex Shaders únicos")
    print("   • 2 Fragment Shaders avanzados") 
    print("   • 4 Combinaciones totales posibles")
    print("   • Superficie metálica como estándar")
    print("   • Efectos oceánicos y psicodélicos")
    print("   • Sistema simplificado y eficiente")
    
    sys.exit(exit_code)