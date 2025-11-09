"""
advancedVertexShaders.py — Colección de vertex shaders avanzados para el proyecto OpenGL
"""

# Vertex shader que implementa desplazamiento mediante seno
wave_vertex_shader = '''
#version 330 core

layout (location = 0) in vec3 inPosition;
layout (location = 1) in vec2 inTexCoords;
layout (location = 2) in vec3 inNormals;

out vec2 fragTexCoords;
out vec3 fragNormal;
out vec4 fragPosition;

uniform mat4 modelMatrix;
uniform mat4 viewMatrix;
uniform mat4 projectionMatrix;
uniform float time;
uniform float waveAmplitude; // Amplitud del movimiento ondulatorio

void main()
{
    // Crear efecto ondulatorio en la coordenada Y
    vec3 modPosition = inPosition;
    modPosition.y += sin(modPosition.x * 3.0 + time * 2.0) * waveAmplitude * 0.1;
    modPosition.y += cos(modPosition.z * 3.0 + time * 2.0) * waveAmplitude * 0.1;
    
    vec4 worldPos = modelMatrix * vec4(modPosition, 1.0);
    fragPosition = worldPos;
    fragNormal = normalize(mat3(modelMatrix) * inNormals);
    fragTexCoords = inTexCoords;
    gl_Position = projectionMatrix * viewMatrix * worldPos;
}
'''

# Vertex shader con rotación de objetos independiente
rotation_vertex_shader = '''
#version 330 core

layout (location = 0) in vec3 inPosition;
layout (location = 1) in vec2 inTexCoords;
layout (location = 2) in vec3 inNormals;

out vec2 fragTexCoords;
out vec3 fragNormal;
out vec4 fragPosition;

uniform mat4 modelMatrix;
uniform mat4 viewMatrix;
uniform mat4 projectionMatrix;
uniform float time;
uniform float rotationSpeed;

void main()
{
    // Crear matriz de rotación
    float angle = time * rotationSpeed;
    mat4 rotationY = mat4(
        cos(angle), 0.0, sin(angle), 0.0,
        0.0, 1.0, 0.0, 0.0,
        -sin(angle), 0.0, cos(angle), 0.0,
        0.0, 0.0, 0.0, 1.0
    );
    
    // Aplicar rotación adicional antes de la matriz del modelo
    vec4 worldPos = modelMatrix * rotationY * vec4(inPosition, 1.0);
    fragPosition = worldPos;
    
    // Rotar también las normales
    mat3 normalMatrix = mat3(transpose(inverse(modelMatrix * rotationY)));
    fragNormal = normalize(normalMatrix * inNormals);
    
    fragTexCoords = inTexCoords;
    gl_Position = projectionMatrix * viewMatrix * worldPos;
}
'''

# Vertex shader para partículas que se expanden desde el centro
explode_vertex_shader = '''
#version 330 core

layout (location = 0) in vec3 inPosition;
layout (location = 1) in vec2 inTexCoords;
layout (location = 2) in vec3 inNormals;

out vec2 fragTexCoords;
out vec3 fragNormal;
out vec4 fragPosition;

uniform mat4 modelMatrix;
uniform mat4 viewMatrix;
uniform mat4 projectionMatrix;
uniform float time;
uniform float explosionFactor;

void main()
{
    // Dirección de la explosión (desde el origen hacia afuera)
    vec3 direction = normalize(inPosition);
    
    // Posición desplazada según el factor de explosión
    vec3 displacement = direction * explosionFactor * sin(time);
    vec3 newPosition = inPosition + displacement;
    
    vec4 worldPos = modelMatrix * vec4(newPosition, 1.0);
    fragPosition = worldPos;
    fragNormal = normalize(mat3(modelMatrix) * inNormals);
    fragTexCoords = inTexCoords;
    gl_Position = projectionMatrix * viewMatrix * worldPos;
}
'''

# Vertex shader para efecto de fuego
fire_vertex_shader = '''
#version 330 core

layout (location = 0) in vec3 inPosition;
layout (location = 1) in vec2 inTexCoords;
layout (location = 2) in vec3 inNormals;

out vec2 fragTexCoords;
out vec3 fragNormal;
out vec4 fragPosition;
out float noise;

uniform mat4 modelMatrix;
uniform mat4 viewMatrix;
uniform mat4 projectionMatrix;
uniform float time;

// Función simple de ruido
float rand(vec2 co) {
    return fract(sin(dot(co.xy, vec2(12.9898, 78.233))) * 43758.5453);
}

void main()
{
    // Generar ruido para el efecto de fuego
    noise = rand(inTexCoords + vec2(time * 0.1)) * 0.2;
    
    // Desplazar vértices para simular movimiento de llamas
    vec3 modPosition = inPosition;
    modPosition.y += sin(time * 5.0 + inPosition.x * 10.0) * 0.03;
    modPosition.x += cos(time * 5.0 + inPosition.z * 10.0) * 0.03;
    
    vec4 worldPos = modelMatrix * vec4(modPosition, 1.0);
    fragPosition = worldPos;
    fragNormal = normalize(mat3(modelMatrix) * inNormals);
    fragTexCoords = inTexCoords;
    gl_Position = projectionMatrix * viewMatrix * worldPos;
}
'''

# Vertex shader para efecto de hielo/cristal
ice_vertex_shader = '''
#version 330 core

layout (location = 0) in vec3 inPosition;
layout (location = 1) in vec2 inTexCoords;
layout (location = 2) in vec3 inNormals;

out vec2 fragTexCoords;
out vec3 fragNormal;
out vec4 fragPosition;
out vec3 viewDir;

uniform mat4 modelMatrix;
uniform mat4 viewMatrix;
uniform mat4 projectionMatrix;
uniform float time;

void main()
{
    vec4 worldPos = modelMatrix * vec4(inPosition, 1.0);
    fragPosition = worldPos;
    fragNormal = normalize(mat3(modelMatrix) * inNormals);
    fragTexCoords = inTexCoords;
    
    // Dirección de vista para efecto de refracción
    viewDir = normalize(vec3(inverse(viewMatrix) * vec4(0, 0, 0, 1)) - worldPos.xyz);
    
    gl_Position = projectionMatrix * viewMatrix * worldPos;
}
'''

# Vertex shader con efecto de pulsación
pulse_vertex_shader = '''
#version 330 core

layout (location = 0) in vec3 inPosition;
layout (location = 1) in vec2 inTexCoords;
layout (location = 2) in vec3 inNormals;

out vec2 fragTexCoords;
out vec3 fragNormal;
out vec4 fragPosition;

uniform mat4 modelMatrix;
uniform mat4 viewMatrix;
uniform mat4 projectionMatrix;
uniform float time;
uniform float pulseIntensity;

void main()
{
    // Efecto de pulsación que expande/contrae el modelo
    float scale = 1.0 + sin(time * 3.0) * pulseIntensity * 0.1;
    vec3 modPosition = inPosition * scale;
    
    vec4 worldPos = modelMatrix * vec4(modPosition, 1.0);
    fragPosition = worldPos;
    fragNormal = normalize(mat3(modelMatrix) * inNormals);
    fragTexCoords = inTexCoords;
    gl_Position = projectionMatrix * viewMatrix * worldPos;
}
'''

# Vertex shader con desplazamiento basado en ruido
noise_vertex_shader = '''
#version 330 core

layout (location = 0) in vec3 inPosition;
layout (location = 1) in vec2 inTexCoords;
layout (location = 2) in vec3 inNormals;

out vec2 fragTexCoords;
out vec3 fragNormal;
out vec4 fragPosition;

uniform mat4 modelMatrix;
uniform mat4 viewMatrix;
uniform mat4 projectionMatrix;
uniform float time;
uniform float noiseIntensity;

// Función de ruido simple de Perlin-like
float noise3D(vec3 p) {
    return fract(sin(dot(p, vec3(12.9898, 78.233, 45.164))) * 43758.5453);
}

void main()
{
    // Generar desplazamiento basado en ruido
    vec3 modPosition = inPosition;
    float noise = noise3D(inPosition * 2.0 + time);
    
    // Aplicar desplazamiento a lo largo de las normales
    modPosition += inNormals * noise * noiseIntensity * 0.1;
    
    vec4 worldPos = modelMatrix * vec4(modPosition, 1.0);
    fragPosition = worldPos;
    fragNormal = normalize(mat3(modelMatrix) * inNormals);
    fragTexCoords = inTexCoords;
    gl_Position = projectionMatrix * viewMatrix * worldPos;
}
'''