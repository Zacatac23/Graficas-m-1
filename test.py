# Test simple para verificar imports
print("Testing imports...")

try:
    print("1. Testing gl import...")
    import gl
    print("   ✅ gl imported successfully")
    
    print("2. Checking what's available in gl module...")
    print("   Available items:", dir(gl))
    
    print("3. Testing Renderer class...")
    if hasattr(gl, 'Renderer'):
        print("   ✅ Renderer class found!")
        renderer_class = gl.Renderer
        print(f"   Renderer class: {renderer_class}")
    else:
        print("   ❌ Renderer class NOT found!")
        print("   Available classes:", [item for item in dir(gl) if item[0].isupper()])
    
    print("4. Testing other imports...")
    from figures import Sphere
    print("   ✅ figures imported successfully")
    
    from lights import AmbientLight, DirectionalLight
    print("   ✅ lights imported successfully")
    
    from material import Material
    print("   ✅ material imported successfully")
    
    from BMP_Writer import GenerateBMP
    print("   ✅ BMP_Writer imported successfully")
    
except Exception as e:
    print(f"❌ Import error: {e}")
    import traceback
    traceback.print_exc()

print("Import test complete!")