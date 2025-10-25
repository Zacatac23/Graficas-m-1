# Nuevos Vertex Shaders para el laboratorio

# Shader 1: Pulso Vertex Shader
# Este shader crea un efecto de pulso que hace que el modelo parezca latir
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

uniform float time; // Tiempo para la animación

void main()
{
    // Crea un efecto de pulso usando la función seno
    float pulseIntensity = 0.2; // Intensidad máxima del pulso
    float pulseSpeed = 3.0; // Velocidad del pulso
    float scale = 1.0 + pulseIntensity * abs(sin(time * pulseSpeed));
    
    // Escalamos desde el centro del modelo
    vec3 scaledPosition = inPosition * scale;
    
    fragPosition = modelMatrix * vec4(scaledPosition, 1.0);
    gl_Position = projectionMatrix * viewMatrix * fragPosition;
    
    // Las normales deben ser recalculadas para el objeto escalado
    fragNormal = normalize(vec3(modelMatrix * vec4(inNormals, 0.0)));
    
    fragTexCoords = inTexCoords;
}
'''

# Shader 2: Twist Vertex Shader
# Este shader causa una rotación que tuerce el modelo alrededor del eje Y
twist_vertex_shader = '''
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

uniform float value; // Controlado por el usuario (0.0-1.0)
uniform float time;

void main()
{
    // Calcula el ángulo de torsión basado en la altura (Y) y un modificador de tiempo
    float twistFactor = value * 5.0; // Controla la intensidad de la torsión
    float angle = inPosition.y * twistFactor + time;
    
    // Matriz de rotación alrededor del eje Y
    float cosAngle = cos(angle);
    float sinAngle = sin(angle);
    
    // Aplica la torsión
    vec3 twistedPosition = vec3(
        inPosition.x * cosAngle - inPosition.z * sinAngle,
        inPosition.y,
        inPosition.x * sinAngle + inPosition.z * cosAngle
    );
    
    // Calcula transformaciones de posición y normal
    fragPosition = modelMatrix * vec4(twistedPosition, 1.0);
    gl_Position = projectionMatrix * viewMatrix * fragPosition;
    
    // Transformación de normales para torsión
    // Esto es una aproximación simplificada
    vec3 twistedNormal = vec3(
        inNormals.x * cosAngle - inNormals.z * sinAngle,
        inNormals.y,
        inNormals.x * sinAngle + inNormals.z * cosAngle
    );
    
    fragNormal = normalize(vec3(modelMatrix * vec4(twistedNormal, 0.0)));
    
    fragTexCoords = inTexCoords;
}
'''

# Shader 3: Noise Displacement Vertex Shader
# Crea un efecto de desplazamiento de vértices basado en un patrón de ruido
noise_displacement_vertex_shader = '''
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
uniform float value; // Intensidad controlada por usuario

// Función de ruido simple (Perlin-like)
float noise(vec3 p) {
    vec3 i = floor(p);
    vec3 f = fract(p);
    f = f * f * (3.0 - 2.0 * f); // Interpolación suave
    
    vec2 uv = i.xy + f.xy + i.z * vec2(197.0, 199.0);
    vec2 rg = vec2(
        sin(uv.x * 0.1 + time),
        sin(uv.y * 0.1 - time)
    ) * 0.5 + 0.5;
    
    return mix(rg.x, rg.y, f.z);
}

void main()
{
    // Calcula el desplazamiento de ruido
    float noiseFreq = 2.0; // Frecuencia del ruido
    float noiseAmp = value * 0.3; // Amplitud del ruido, controlada por value
    
    // Generar valor de ruido basado en la posición y tiempo
    float noiseValue = noise(inPosition * noiseFreq + time * 0.5);
    
    // Aplicar desplazamiento a lo largo de la normal
    vec3 displacedPosition = inPosition + inNormals * noiseValue * noiseAmp;
    
    // Transformar al espacio de proyección
    fragPosition = modelMatrix * vec4(displacedPosition, 1.0);
    gl_Position = projectionMatrix * viewMatrix * fragPosition;
    
    // Pasar atributos adicionales al fragment shader
    fragNormal = normalize(vec3(modelMatrix * vec4(inNormals, 0.0)));
    fragTexCoords = inTexCoords;
}
'''