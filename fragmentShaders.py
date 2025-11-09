"""
advancedFragmentShaders.py — Colección de fragment shaders avanzados para el proyecto OpenGL
"""

# Fragment shader con efecto de cel-shading simplificado (sin textura necesaria)
toon_fragment_shader = '''
#version 330 core

in vec2 fragTexCoords;
in vec3 fragNormal;
in vec4 fragPosition;

out vec4 fragColor;

uniform sampler2D tex0;
uniform vec3 pointLight;
uniform float ambientLight;
uniform vec3 baseColor;
uniform int useTexture;

void main()
{
    // Normalización y cálculo de dirección de luz
    vec3 normal = normalize(fragNormal);
    vec3 lightDir = normalize(pointLight - fragPosition.xyz);
    
    // Cálculo de intensidad de luz con cuantización (efecto cel-shading)
    float intensity = dot(normal, lightDir);
    
    // Cuantizar la intensidad para crear el efecto cel-shading
    if (intensity > 0.95) intensity = 1.0;
    else if (intensity > 0.5) intensity = 0.6;
    else if (intensity > 0.05) intensity = 0.3;
    else intensity = 0.1;
    
    intensity += ambientLight;
    
    // Color base (desde textura o color uniforme)
    vec4 texCol = vec4(baseColor, 1.0);
    if (useTexture == 1) {
        texCol = texture(tex0, fragTexCoords);
    }
    
    // Aplicar intensidad para dar el efecto cel-shading
    fragColor = texCol * intensity;
    
    // Añadir contorno (opcional)
    // vec3 viewDir = normalize(cameraPos - fragPosition.xyz);
    // float rim = 1.0 - max(dot(viewDir, normal), 0.0);
    // rim = smoothstep(0.6, 1.0, rim);
    // fragColor.rgb = mix(fragColor.rgb, vec3(0.0), rim);
}
'''

# Fragment shader con efecto de transparencia pulsante
pulse_fragment_shader = '''
#version 330 core

in vec2 fragTexCoords;
in vec3 fragNormal;
in vec4 fragPosition;

out vec4 fragColor;

uniform sampler2D tex0;
uniform vec3 pointLight;
uniform float ambientLight;
uniform vec3 baseColor;
uniform int useTexture;
uniform float time;

void main()
{
    // Normalización y cálculo básico de iluminación
    vec3 normal = normalize(fragNormal);
    vec3 lightDir = normalize(pointLight - fragPosition.xyz);
    float intensity = max(0.0, dot(normal, lightDir)) + ambientLight;
    
    // Color base (desde textura o color uniforme)
    vec4 texCol = vec4(baseColor, 1.0);
    if (useTexture == 1) {
        texCol = texture(tex0, fragTexCoords);
    }
    
    // Efecto de transparencia pulsante
    float alpha = 0.5 + 0.5 * sin(time * 3.0);
    
    // Color final con transparencia
    fragColor = texCol * intensity;
    fragColor.a = alpha;
}
'''

# Fragment shader con efecto de coloración dinámica
color_shift_fragment_shader = '''
#version 330 core

in vec2 fragTexCoords;
in vec3 fragNormal;
in vec4 fragPosition;

out vec4 fragColor;

uniform sampler2D tex0;
uniform vec3 pointLight;
uniform float ambientLight;
uniform vec3 baseColor;
uniform int useTexture;
uniform float time;

void main()
{
    // Normalización y cálculo básico de iluminación
    vec3 normal = normalize(fragNormal);
    vec3 lightDir = normalize(pointLight - fragPosition.xyz);
    float intensity = max(0.0, dot(normal, lightDir)) + ambientLight;
    
    // Color base (desde textura o color uniforme)
    vec4 texCol = vec4(baseColor, 1.0);
    if (useTexture == 1) {
        texCol = texture(tex0, fragTexCoords);
    }
    
    // Calcular colores cambiantes basados en el tiempo
    vec3 shiftColor;
    shiftColor.r = 0.5 + 0.5 * sin(time);
    shiftColor.g = 0.5 + 0.5 * sin(time + 2.094);  // 2π/3
    shiftColor.b = 0.5 + 0.5 * sin(time + 4.189);  // 4π/3
    
    // Mezclar el color original con el color cambiante
    texCol.rgb = mix(texCol.rgb, shiftColor, 0.5);
    
    // Color final
    fragColor = texCol * intensity;
}
'''

# Fragment shader con efecto de neón (glow)
neon_fragment_shader = '''
#version 330 core

in vec2 fragTexCoords;
in vec3 fragNormal;
in vec4 fragPosition;

out vec4 fragColor;

uniform sampler2D tex0;
uniform vec3 pointLight;
uniform float ambientLight;
uniform vec3 baseColor;
uniform int useTexture;
uniform float time;

void main()
{
    // Normalización y cálculo básico de iluminación
    vec3 normal = normalize(fragNormal);
    vec3 lightDir = normalize(pointLight - fragPosition.xyz);
    float intensity = max(0.0, dot(normal, lightDir)) + ambientLight;
    
    // Color base (desde textura o color uniforme)
    vec4 texCol = vec4(baseColor, 1.0);
    if (useTexture == 1) {
        texCol = texture(tex0, fragTexCoords);
    }
    
    // Efecto de borde brillante (neón)
    vec3 viewDir = vec3(0, 0, 1); // Simplificado, idealmente sería la dirección a la cámara
    float rim = 1.0 - max(dot(viewDir, normal), 0.0);
    rim = pow(rim, 2.0); // Control de la intensidad del borde
    
    // Color del borde neón (azul por defecto, podría ser uniforme)
    vec3 neonColor = vec3(0.0, 0.5, 1.0);
    
    // Efecto pulsante para el borde neón
    float glow = 0.8 + 0.2 * sin(time * 3.0);
    
    // Aplicar el efecto neón
    vec3 finalColor = texCol.rgb * intensity;
    finalColor += rim * neonColor * glow * 2.0;
    
    fragColor = vec4(finalColor, 1.0);
}
'''

# Fragment shader con sombreado phong (sin textura requerida)
phong_fragment_shader = '''
#version 330 core

in vec2 fragTexCoords;
in vec3 fragNormal;
in vec4 fragPosition;

out vec4 fragColor;

uniform sampler2D tex0;
uniform vec3 pointLight;
uniform float ambientLight;
uniform vec3 baseColor;
uniform int useTexture;

void main()
{
    // Propiedades del material
    vec3 objectColor;
    if (useTexture == 1) {
        objectColor = texture(tex0, fragTexCoords).rgb;
    } else {
        objectColor = baseColor;
    }
    
    // Luz ambiental
    vec3 ambient = ambientLight * objectColor;
    
    // Luz difusa
    vec3 norm = normalize(fragNormal);
    vec3 lightDir = normalize(pointLight - fragPosition.xyz);
    float diff = max(dot(norm, lightDir), 0.0);
    vec3 diffuse = diff * objectColor;
    
    // Luz especular (Phong)
    vec3 viewDir = normalize(-fragPosition.xyz); // Suponiendo que la cámara está en el origen
    vec3 reflectDir = reflect(-lightDir, norm);
    float spec = pow(max(dot(viewDir, reflectDir), 0.0), 32);
    vec3 specular = 0.5 * spec * vec3(1.0, 1.0, 1.0); // Color especular blanco
    
    // Resultado final
    vec3 result = ambient + diffuse + specular;
    fragColor = vec4(result, 1.0);
}
'''

# Fragment shader para efecto de fuego
fire_fragment_shader = '''
#version 330 core

in vec2 fragTexCoords;
in vec3 fragNormal;
in vec4 fragPosition;
in float noise;

out vec4 fragColor;

uniform sampler2D tex0;
uniform vec3 pointLight;
uniform float ambientLight;
uniform vec3 baseColor;
uniform int useTexture;
uniform float time;

void main()
{
    // Colores para el fuego
    vec3 fireColor1 = vec3(1.0, 0.0, 0.0);    // Rojo
    vec3 fireColor2 = vec3(1.0, 0.5, 0.0);    // Naranja
    vec3 fireColor3 = vec3(1.0, 0.8, 0.0);    // Amarillo
    
    // Cálculos básicos para iluminación
    vec3 normal = normalize(fragNormal);
    vec3 lightDir = normalize(pointLight - fragPosition.xyz);
    float intensity = max(0.0, dot(normal, lightDir)) + ambientLight;
    
    // Factor de altura para el gradiente de color
    float heightFactor = fragPosition.y * 0.5 + 0.5;
    
    // Mezcla de colores basada en altura y tiempo
    vec3 finalColor;
    float timeFactor = sin(time * 3.0) * 0.5 + 0.5;
    
    if (heightFactor < 0.4 - timeFactor * 0.1) {
        finalColor = mix(fireColor1, fireColor2, heightFactor * 2.5 + noise);
    } else if (heightFactor < 0.7 + timeFactor * 0.1) {
        finalColor = mix(fireColor2, fireColor3, (heightFactor - 0.4) * 3.3 + noise);
    } else {
        finalColor = fireColor3;
        // Transparencia en la parte superior para efecto de desvanecimiento
        intensity *= (1.0 - (heightFactor - 0.7) * 3.3);
    }
    
    // Añadir fluctuación con ruido
    finalColor += noise * 0.2;
    
    // Resultado final
    fragColor = vec4(finalColor * intensity, intensity);
}
'''

# Fragment shader para efecto de hielo/cristal
ice_fragment_shader = '''
#version 330 core

in vec2 fragTexCoords;
in vec3 fragNormal;
in vec4 fragPosition;
in vec3 viewDir;

out vec4 fragColor;

uniform sampler2D tex0;
uniform vec3 pointLight;
uniform float ambientLight;
uniform vec3 baseColor;
uniform int useTexture;
uniform float time;

void main()
{
    // Colores base para el hielo
    vec3 iceColor = vec3(0.8, 0.9, 0.95);
    if (useTexture == 1) {
        iceColor = texture(tex0, fragTexCoords).rgb;
    } else {
        iceColor = baseColor;
    }
    
    // Normalización
    vec3 normal = normalize(fragNormal);
    vec3 lightDir = normalize(pointLight - fragPosition.xyz);
    
    // Cálculo de refracción (simplificado)
    vec3 refraction = refract(-viewDir, normal, 0.7); // 0.7 es un índice de refracción aproximado para el hielo
    
    // Efecto Fresnel (borde brillante)
    float fresnel = pow(1.0 - dot(normal, -viewDir), 5.0);
    
    // Efecto de brillo interior
    float innerGlow = pow(max(dot(normal, -viewDir), 0.0), 2.0);
    
    // Iluminación difusa
    float diffuse = max(dot(normal, lightDir), 0.0) + ambientLight;
    
    // Efecto de brillo especular (alta intensidad para cristal/hielo)
    float specular = pow(max(dot(reflect(-lightDir, normal), -viewDir), 0.0), 64.0) * 2.0;
    
    // Variación temporal para brillo cristalino
    float shimmer = 0.95 + 0.05 * sin(time * 5.0 + fragPosition.x * 10.0 + fragPosition.y * 10.0);
    
    // Combinar todos los efectos
    vec3 finalColor = iceColor * diffuse * shimmer;
    finalColor += vec3(1.0) * specular; // Añadir brillo especular
    finalColor += iceColor * innerGlow * 0.3; // Añadir brillo interior
    finalColor += vec3(0.9, 0.95, 1.0) * fresnel * 0.5; // Añadir efecto Fresnel
    
    // Resultado final
    fragColor = vec4(finalColor, 0.7 + 0.3 * fresnel); // Transparencia parcial
}
'''

# Fragment shader con efecto de pixelación
pixelate_fragment_shader = '''
#version 330 core

in vec2 fragTexCoords;
in vec3 fragNormal;
in vec4 fragPosition;

out vec4 fragColor;

uniform sampler2D tex0;
uniform vec3 pointLight;
uniform float ambientLight;
uniform vec3 baseColor;
uniform int useTexture;
uniform float pixelSize; // Tamaño de los pixeles (mayor valor = más pixelado)

void main()
{
    // Pixelación básica
    vec2 pixelCoords = floor(fragTexCoords * 100.0 / pixelSize) * pixelSize / 100.0;
    
    // Normalización y cálculo básico de iluminación
    vec3 normal = normalize(fragNormal);
    vec3 lightDir = normalize(pointLight - fragPosition.xyz);
    float intensity = max(0.0, dot(normal, lightDir)) + ambientLight;
    
    // Color base (desde textura pixelada o color uniforme)
    vec4 texCol = vec4(baseColor, 1.0);
    if (useTexture == 1) {
        texCol = texture(tex0, pixelCoords);
    }
    
    // Resultado final con iluminación aplicada
    fragColor = texCol * intensity;
}
'''

# Fragment shader con efecto de rayos X o visión térmica
xray_fragment_shader = '''
#version 330 core

in vec2 fragTexCoords;
in vec3 fragNormal;
in vec4 fragPosition;

out vec4 fragColor;

uniform sampler2D tex0;
uniform vec3 pointLight;
uniform float ambientLight;
uniform vec3 baseColor;
uniform int useTexture;
uniform float time;

void main()
{
    // Normalización y cálculo básico de iluminación
    vec3 normal = normalize(fragNormal);
    vec3 lightDir = normalize(pointLight - fragPosition.xyz);
    
    // Efecto de rayos X: más brillante cuanto más perpendicular es a la vista
    vec3 viewDir = normalize(-fragPosition.xyz);
    float edgeEffect = 1.0 - abs(dot(normal, viewDir));
    edgeEffect = pow(edgeEffect, 2.0);
    
    // Añadir pulsación temporal
    float pulse = 0.8 + 0.2 * sin(time * 2.0);
    edgeEffect *= pulse;
    
    // Colores para efecto de rayos X (azul claro brillante)
    vec3 xrayColor = vec3(0.0, 0.7, 1.0);
    
    // Aplicar color base si hay textura
    if (useTexture == 1) {
        vec4 texCol = texture(tex0, fragTexCoords);
        float brightness = dot(texCol.rgb, vec3(0.299, 0.587, 0.114));
        xrayColor = mix(xrayColor, texCol.rgb, 0.3);
    }
    
    // Resultado final
    fragColor = vec4(xrayColor * edgeEffect, 0.7);
}
'''