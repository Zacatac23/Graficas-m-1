"""
emergency_scale_fix.py
Arreglo rápido para modelos que se ven muy pequeños
"""

from math_utils import Vec3

def apply_emergency_scale_fix(scene):
    """Aplicar arreglo de emergencia para modelos pequeños"""
    print("\n🚨 APLICANDO ARREGLO DE EMERGENCIA PARA MODELOS PEQUEÑOS")
    print("="*60)
    
    fixed_count = 0
    
    for model in scene.models:
        original_scale = model.scale.x
        
        # Si la escala actual es menor a 2.0, aumentarla significativamente
        if original_scale < 2.0:
            # Para modelos muy pequeños como t.obj (2234 vértices)
            if original_scale < 1.0:
                new_scale = 5.0  # Aumentar MUCHO
            elif original_scale < 1.5:
                new_scale = 4.0  # Aumentar bastante
            else:
                new_scale = 3.0  # Aumentar moderadamente
            
            # Aplicar nueva escala
            model.scale = Vec3(new_scale, new_scale, new_scale)
            
            # También acercar un poco el modelo
            model.position = Vec3(
                model.position.x * 0.8,  # Acercar 20%
                model.position.y + 0.5,  # Elevar ligeramente
                model.position.z * 0.8   # Acercar en Z también
            )
            
            print(f"🔧 ARREGLADO: {model.name}")
            print(f"   📏 Escala: {original_scale:.1f}x → {new_scale:.1f}x")
            print(f"   📍 Nueva posición: ({model.position.x:.1f}, {model.position.y:.1f}, {model.position.z:.1f})")
            
            fixed_count += 1
    
    if fixed_count > 0:
        print(f"\n✅ ARREGLO COMPLETADO: {fixed_count} modelos ajustados")
        
        # Ajustar cámara para los nuevos tamaños
        if scene.models:
            # Calcular nuevos límites
            min_x = min(m.position.x - m.scale.x for m in scene.models)
            max_x = max(m.position.x + m.scale.x for m in scene.models)
            min_z = min(m.position.z - m.scale.z for m in scene.models)
            max_z = max(m.position.z + m.scale.z for m in scene.models)
            
            center_x = (min_x + max_x) / 2
            center_z = (min_z + max_z) / 2
            scene_size = max(max_x - min_x, max_z - min_z)
            
            # Cámara más cerca para modelos pequeños aumentados
            camera_distance = scene_size * 0.6 + 6
            camera_height = scene_size * 0.4 + 4
            
            scene.camera_position = Vec3(
                center_x - camera_distance * 0.3,
                camera_height,
                center_z + camera_distance
            )
            scene.camera_target = Vec3(center_x, 2, center_z)
            
            print(f"📷 CÁMARA REAJUSTADA:")
            print(f"   📍 Nueva posición: ({scene.camera_position.x:.1f}, {scene.camera_position.y:.1f}, {scene.camera_position.z:.1f})")
    else:
        print("ℹ️  No se necesitaron ajustes de emergencia")
    
    return fixed_count > 0

def quick_scale_multiplier_fix(scene, multiplier=2.0):
    """Aplicar multiplicador rápido a todos los modelos"""
    print(f"\n⚡ APLICANDO MULTIPLICADOR RÁPIDO: {multiplier}x")
    
    for model in scene.models:
        original_scale = model.scale.x
        new_scale = original_scale * multiplier
        model.scale = Vec3(new_scale, new_scale, new_scale)
        
        print(f"📏 {model.name}: {original_scale:.1f}x → {new_scale:.1f}x")
    
    print("✅ Multiplicador aplicado a todos los modelos")
    return True