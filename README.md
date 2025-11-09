# Graficas-m-1 — Demo OpenGL con Shaders

Este repositorio contiene un renderer OpenGL en Python que permite probar varios vertex y fragment shaders.

## Requisitos
- Windows (probado en Windows 10/11)
- Python 3.10+ (se probó con Python 3.12)
- Un entorno virtual es recomendado.

Dependencias Python (instalarlas en el venv):
- pygame
- PyOpenGL
- PyGLM
- Pillow (opcional, recomendado para cargar PNGs sin warnings)

Ejemplo (PowerShell):
```powershell
python -m venv .venv32 ; .\.venv32\Scripts\Activate.ps1
pip install --upgrade pip
pip install pygame PyOpenGL PyGLM Pillow
```

## Cómo ejecutar
Desde la carpeta del proyecto (`Graficas-m-1`) ejecuta (PowerShell):

```powershell
.\.venv32\Scripts\python.exe .\RendererOpenGL2025.py
```

La aplicación abrirá una ventana y mostrará en consola la lista de shaders disponibles.

## Controles (teclado / ratón)
- Flechas: Mover cámara
- Mouse click izquierdo + arrastrar: mover cámara
- Mouse click derecho + arrastrar: orbitar cámara
- Rueda del ratón: zoom
- Q / E: Acercar / alejar cámara
- F: Alternar modo (relleno / líneas)
- M: Alternar entre mostrar todos los modelos o solo el seleccionado
- P / S / B: Alternar visibilidad del pico (pick) / espada (sword) / balde (buck)
- G / J / K / L: Enfocar cámara en modelo 1 / 2 / 3 / 4
- TAB: Cambiar efecto de post-procesado

Shader selection:
- Números 1-9: seleccionar shaders 1-9
- SHIFT + número + número: seleccionar shaders 10+ (ejemplo: SHIFT+1 luego 5 → shader 15)
- 0: Reasignar el shader actual al modelo seleccionado

Uniform controls (modifican parámetros de shaders activos):
- Z / X: Disminuir / aumentar `value`
- C / V: Disminuir / aumentar `waveAmplitude` (para Wave Effect)
- B / N: Disminuir / aumentar `rotationSpeed` (para Rotation)
- U / I: Disminuir / aumentar `explosionFactor` (para Explode Effect)
- O / P: Disminuir / aumentar `pulseIntensity` y `noiseIntensity`
- K / L: Disminuir / aumentar `pixelSize` (para Pixelate)
- ESC: Salir
- H: Mostrar ayuda

## Shaders disponibles (lista rápida)
La app incluye una colección de shaders. En mi ejecución se listaron los siguientes (nombres dentro de la app):

1. Fresh Shader — shader por defecto (vertex + fragment `fresh`)
2. Toon Shader
3. Phong Shader
4. Color Shift
5. Neon Effect
6. Pulse Alpha
7. Pixelate
8. X-Ray
9. Wave Effect (vertex avanz / fragment fresh)
10. Rotation (vertex avanz / fragment fresh)
11. Explode Effect (vertex avanz / fragment fresh)
12. Pulse Vertex
13. Noise Vertex
14. Fire Effect (vertex y fragment avanzados)
15. Ice Effect (vertex y fragment avanzados)

Cada entrada combina un vertex shader y un fragment shader; algunos usan los "fresh" originales y combinan con fragment shaders avanzados.

## Notas y solución de problemas
- Si obtienes errores GL al asignar uniforms, puede ser porque no se llamó `glUseProgram(prog)` antes de `glUniform*`. El renderer fue actualizado para activar el programa antes de pasar uniforms específicos por-modelo.
- Si un shader compila pero no ves el efecto esperado, revisa que las variables `out` del vertex shader y `in` del fragment shader coincidan en nombre y tipo (por ejemplo `noise` o `viewDir`). Si faltan, el fragment shader puede compilar pero no recibir esos datos.
- Si una textura PNG muestra advertencia `iCCP: known incorrect sRGB profile`, instala Pillow y se usa como loader para evitar esa advertencia.

## Ejemplo rápido
1. Activar venv e instalar dependencias (ver arriba).
2. Ejecutar el script principal:
```powershell
.\.venv32\Scripts\python.exe .\RendererOpenGL2025.py
```
3. Pulsar `H` para ver la ayuda en cualquier momento.
4. Pulsar `1`..`9` para cambiar shaders; usa SHIFT + número para seleccionar índices de shader de dos dígitos.

## Archivos importantes
- `RendererOpenGL2025.py` — script principal / demo.
- `gl.py` — implementación del renderer (compilación de shaders, render loop, uniforms comunes).
- `vertexShaders.py` / `fragmentShaders.py` — colecciones de shaders avanzados.
- `freshShader.py` — vertex y fragment shader "fresh" por defecto.
- `model.py`, `obj.py`, `buffer.py` — gestión de modelos, texturas y buffers.

---
Si quieres, puedo:
- Generar un `requirements.txt` pronto con las versiones usadas.
- Mover la lógica de uniforms por-programa dentro de `gl.py` para centralizar el código (recomendado).
- Limpiar/consolidar shaders que ya no uses.

Dime si quieres que haga alguno de esos pasos y lo añado al README y al repo.