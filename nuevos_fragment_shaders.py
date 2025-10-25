# Nuevos Fragment Shaders para el laboratorio

# Shader 1: Holográfico
# Este shader crea un efecto holográfico con líneas de escaneo y brillo que depende del ángulo de visión
hologram_shader = '''
#version 330 core

in vec2 fragTexCoords;
in vec3 fragNormal;
in vec4 fragPosition;

out vec4 fragColor;

uniform sampler2D tex0;
uniform vec3 pointLight;
uniform float ambientLight;
uniform float time;

void main()
{
    // Color base holográfico (azul cian)
    vec3 hologramColor = vec3(0.0, 0.8, 1.0);
    
    // Efecto de líneas de escaneo
    float scanLine = sin(fragPosition.y * 50.0 + time * 2.0) * 0.15 + 0.85;
    
    // Efecto de borde basado en la normal y dirección de visión (aproximación)
    // En un shader real, utilizaríamos la posición de la cámara para el cálculo exacto
    vec3 viewDir = normalize(vec3(0.0, 0.0, 1.0)); // Asumimos que miramos desde +Z
    float rimEffect = 1.0 - max(dot(fragNormal, viewDir), 0.0);
    rimEffect = pow(rimEffect, 2.0) * 0.5 + 0.5; // Ajuste del efecto
    
    // Aplicar un patrón de fluctuación basado en el tiempo
    float fluctuation = sin(time * 3.0 + fragPosition.x * 2.0 + fragPosition.y * 2.0) * 0.1 + 0.9;
    
    // Mezclar los efectos
    vec3 baseColor = texture(tex0, fragTexCoords).rgb; // Obtener color de la textura
    vec3 finalColor = baseColor * hologramColor * scanLine * fluctuation;
    
    // Aumentar brillo en los bordes
    finalColor += hologramColor * rimEffect * 0.5;
    
    // Transparencia variable para el efecto holográfico
    float alpha = 0.7 + 0.3 * fluctuation * rimEffect;
    
    fragColor = vec4(finalColor, alpha);
}
'''

# Shader 2: Térmico
# Este shader simula un visor térmico, mapeando los valores de luminancia a una escala de colores térmicos
thermal_shader = '''
#version 330 core

in vec2 fragTexCoords;
in vec3 fragNormal;
in vec4 fragPosition;

out vec4 fragColor;

uniform sampler2D tex0;
uniform vec3 pointLight;
uniform float ambientLight;
uniform float time;

// Función para mapear una temperatura (0-1) a un color térmico
vec3 heatMapColor(float temperature) {
    // Gradiente de color: azul -> verde -> amarillo -> rojo -> blanco
    vec3 color = vec3(0.0);
    
    if (temperature < 0.2) {
        // Azul a cian
        float t = temperature / 0.2;
        color = mix(vec3(0, 0, 0.5), vec3(0, 0.5, 0.5), t);
    } else if (temperature < 0.4) {
        // Cian a verde
        float t = (temperature - 0.2) / 0.2;
        color = mix(vec3(0, 0.5, 0.5), vec3(0, 1, 0), t);
    } else if (temperature < 0.6) {
        // Verde a amarillo
        float t = (temperature - 0.4) / 0.2;
        color = mix(vec3(0, 1, 0), vec3(1, 1, 0), t);
    } else if (temperature < 0.8) {
        // Amarillo a rojo
        float t = (temperature - 0.6) / 0.2;
        color = mix(vec3(1, 1, 0), vec3(1, 0, 0), t);
    } else {
        // Rojo a blanco
        float t = (temperature - 0.8) / 0.2;
        color = mix(vec3(1, 0, 0), vec3(1, 1, 1), t);
    }
    
    return color;
}

void main()
{
    // Obtener el color base de la textura
    vec4 texColor = texture(tex0, fragTexCoords);
    
    // Calcular luminancia (brillo percibido) como aproximación a la "temperatura"
    float luminance = dot(texColor.rgb, vec3(0.299, 0.587, 0.114));
    
    // Modificar la luminancia basada en la iluminación
    vec3 lightDir = normalize(pointLight - fragPosition.xyz);
    float lightIntensity = max(0, dot(fragNormal, lightDir)) + ambientLight;
    
    // Aplicar fluctuación suave basada en el tiempo para simular ruido térmico
    float noise = sin(time * 2.0 + fragPosition.x * 10.0 + fragPosition.y * 10.0) * 0.05;
    
    // Calcular temperatura final
    float temperature = clamp(luminance * lightIntensity + noise, 0.0, 1.0);
    
    // Mapear temperatura a color
    vec3 thermalColor = heatMapColor(temperature);
    
    // Añadir patrón de escaneo sutil
    float scanLine = sin(fragTexCoords.y * 100.0 + time) * 0.05 + 0.95;
    thermalColor *= scanLine;
    
    fragColor = vec4(thermalColor, 1.0);
}
'''

# Shader 3: Efecto de Dibujo Animado (Toon + Outline)
# Este shader combina el efecto toon con contornos para crear una apariencia de dibujo animado
cartoon_shader = '''
#version 330 core

in vec2 fragTexCoords;
in vec3 fragNormal;
in vec4 fragPosition;

out vec4 fragColor;

uniform sampler2D tex0;
uniform vec3 pointLight;
uniform float ambientLight;
uniform float time;
uniform float value; // Para controlar la intensidad del contorno

void main()
{
    // 1. Calcular luz en estilo toon (discretizado)
    vec3 lightDir = normalize(pointLight - fragPosition.xyz);
    float intensity = max(0.0, dot(fragNormal, lightDir)) + ambientLight;
    
    // Discretizar la intensidad para efecto toon
    if (intensity > 0.95) intensity = 1.0;
    else if (intensity > 0.6) intensity = 0.8;
    else if (intensity > 0.3) intensity = 0.6;
    else intensity = 0.4;
    
    // 2. Aplicar colores base discretizados
    vec4 texColor = texture(tex0, fragTexCoords);
    
    // Discretizar colores para efecto de dibujo animado
    // Limitar a una paleta reducida
    const int levels = 4; // Número de niveles por canal
    vec3 toonColor;
    toonColor.r = floor(texColor.r * levels) / levels;
    toonColor.g = floor(texColor.g * levels) / levels;
    toonColor.b = floor(texColor.b * levels) / levels;
    
    // 3. Calcular contorno (edge detection basado en normales)
    // Esto simula un contorno al detectar cambios bruscos en las normales
    // En un shader más avanzado, usaríamos un post-proceso para edge detection real
    float edgeFactor = 1.0 - dot(fragNormal, lightDir);
    edgeFactor = smoothstep(0.3, 0.4, edgeFactor);
    edgeFactor *= value; // Ajustar intensidad con el parámetro value
    
    // Oscurecer áreas de contorno
    vec3 finalColor = mix(toonColor * intensity, vec3(0.0), edgeFactor * 0.7);
    
    // Opcional: Añadir un sutil brillo animado para que no se vea estático
    float highlight = max(0.0, sin(time * 1.5 + fragPosition.x + fragPosition.y)) * 0.1;
    finalColor += vec3(highlight) * max(0.0, dot(fragNormal, vec3(0, 1, 0)));
    
    fragColor = vec4(finalColor, 1.0);
}
'''

# Shader 4: Efecto Pixelado
# Este shader crea un efecto de pixelado dinámico
pixel_shader = '''
#version 330 core

in vec2 fragTexCoords;
in vec3 fragNormal;
in vec4 fragPosition;

out vec4 fragColor;

uniform sampler2D tex0;
uniform vec3 pointLight;
uniform float ambientLight;
uniform float time;
uniform float value; // Para controlar el tamaño de los píxeles

void main()
{
    // Calcular la iluminación básica
    vec3 lightDir = normalize(pointLight - fragPosition.xyz);
    float intensity = max(0.0, dot(fragNormal, lightDir)) + ambientLight;
    
    // Tamaño de los píxeles (controlado por value)
    float pixelSize = max(2.0, 30.0 * value);
    
    // Añadir animación opcional al tamaño del píxel
    pixelSize += sin(time * 2.0) * 3.0 * value;
    
    // Discretizar coordenadas de textura para crear el efecto pixelado
    vec2 pixelCoords = floor(fragTexCoords * pixelSize) / pixelSize;
    
    // Obtener color de la textura con coordenadas pixeladas
    vec4 pixelColor = texture(tex0, pixelCoords);
    
    // Aplicar iluminación y efecto de "bloque" pixelado
    // Discretizar también la intensidad
    float pixelIntensity = floor(intensity * 5.0) / 5.0;
    
    // Color final con efecto pixelado
    fragColor = pixelColor * pixelIntensity;
    
    // Agregar un sutil patrón de "ruido" para simular una pantalla antigua
    float noise = fract(sin(dot(pixelCoords, vec2(12.9898, 78.233)) + time) * 43758.5453) * 0.1;
    fragColor.rgb += vec3(noise) * value * 0.5;
}
'''