"""
freshShaders.py — Contiene los shaders fresh originales del proyecto
"""

# Fresh vertex shader original
fresh_vertex_shader = '''
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

void main()
{
    vec4 worldPos = modelMatrix * vec4(inPosition, 1.0);
    fragPosition = worldPos;
    fragNormal = normalize( mat3(modelMatrix) * inNormals );
    fragTexCoords = inTexCoords;
    gl_Position = projectionMatrix * viewMatrix * worldPos;
}
'''

# Fresh fragment shader original
fresh_fragment_shader = '''
#version 330 core

in vec2 fragTexCoords;
in vec3 fragNormal;
in vec4 fragPosition;

out vec4 fragColor;

uniform sampler2D tex0;
uniform vec3 pointLight;
uniform float ambientLight;
uniform vec3 baseColor; // used if texture is not meaningful
uniform int useTexture; // 0 = ignore tex0, 1 = sample tex0

void main()
{
    vec3 normal = normalize(fragNormal);
    vec3 lightDir = normalize(pointLight - fragPosition.xyz);
    float intensity = max(0.0, dot(normal, lightDir)) + ambientLight;

    vec4 texCol = vec4(baseColor, 1.0);
    if (useTexture == 1) {
        texCol = texture(tex0, fragTexCoords);
    }

    fragColor = texCol * intensity;
}
'''