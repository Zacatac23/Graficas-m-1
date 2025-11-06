import glm
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import pygame
import ctypes

# Envmap using a single equirectangular 2D texture (different approach than cube-map skybox)
env_vertex_shader = '''
#version 450 core
layout (location = 0) in vec3 inPosition;

out vec3 vDir;

uniform mat4 viewMatrix;
uniform mat4 projectionMatrix;

void main() {
    // Pass direction vector to fragment shader
    vDir = inPosition;
    // Remove translation from view matrix
    mat4 vm = mat4(mat3(viewMatrix));
    gl_Position = projectionMatrix * vm * vec4(inPosition, 1.0);
}
'''

env_fragment_shader = '''
#version 450 core
in vec3 vDir;
uniform sampler2D envMap; // equirectangular map
out vec4 fragColor;

void main() {
    vec3 dir = normalize(vDir);
    float u = 0.5 + atan(dir.z, dir.x) / (2.0 * 3.141592653589793);
    float v = 0.5 - asin(dir.y) / 3.141592653589793;
    vec3 color = texture(envMap, vec2(u, v)).rgb;
    fragColor = vec4(color, 1.0);
}
'''

class EnvMap(object):
    def __init__(self, textureFile):
        self.cameraRef = None
        # Cube vertices (same positions as a cube skybox) but shader samples equirectangular map
        self.vertices = [
            -1.0,  1.0, -1.0,
            -1.0, -1.0, -1.0,
             1.0, -1.0, -1.0,
             1.0, -1.0, -1.0,
             1.0,  1.0, -1.0,
            -1.0,  1.0, -1.0,
            
            -1.0, -1.0,  1.0,
            -1.0, -1.0, -1.0,
            -1.0,  1.0, -1.0,
            -1.0,  1.0, -1.0,
            -1.0,  1.0,  1.0,
            -1.0, -1.0,  1.0,
            
             1.0, -1.0, -1.0,
             1.0, -1.0,  1.0,
             1.0,  1.0,  1.0,
             1.0,  1.0,  1.0,
             1.0,  1.0, -1.0,
             1.0, -1.0, -1.0,
            
            -1.0, -1.0,  1.0,
            -1.0,  1.0,  1.0,
             1.0,  1.0,  1.0,
             1.0,  1.0,  1.0,
             1.0, -1.0,  1.0,
            -1.0, -1.0,  1.0,
            
            -1.0,  1.0, -1.0,
             1.0,  1.0, -1.0,
             1.0,  1.0,  1.0,
             1.0,  1.0,  1.0,
            -1.0,  1.0,  1.0,
            -1.0,  1.0, -1.0,
            
            -1.0, -1.0, -1.0,
            -1.0, -1.0,  1.0,
             1.0, -1.0, -1.0,
             1.0, -1.0, -1.0,
            -1.0, -1.0,  1.0,
             1.0, -1.0,  1.0
        ]

        import numpy as np
        self.vertexBuffer = (np.array(self.vertices, dtype=np.float32))

        self.VBO = glGenBuffers(1)
        self.shaders = compileProgram(compileShader(env_vertex_shader, GL_VERTEX_SHADER),
                                      compileShader(env_fragment_shader, GL_FRAGMENT_SHADER))

        # Load equirectangular texture
        surface = pygame.image.load(textureFile)
        surface = pygame.transform.flip(surface, False, True)
        texData = pygame.image.tostring(surface, "RGB", True)

        self.texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, surface.get_width(), surface.get_height(), 0, GL_RGB, GL_UNSIGNED_BYTE, texData)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glBindTexture(GL_TEXTURE_2D, 0)

    def Render(self):
        if self.shaders is None:
            return

        glUseProgram(self.shaders)

        if self.cameraRef is not None:
            glUniformMatrix4fv(glGetUniformLocation(self.shaders, "viewMatrix"), 1, GL_FALSE, glm.value_ptr(self.cameraRef.viewMatrix))
            glUniformMatrix4fv(glGetUniformLocation(self.shaders, "projectionMatrix"), 1, GL_FALSE, glm.value_ptr(self.cameraRef.projectionMatrix))

        glDepthMask(GL_FALSE)

        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glUniform1i(glGetUniformLocation(self.shaders, "envMap"), 0)

        glBindBuffer(GL_ARRAY_BUFFER, self.VBO)
        glBufferData(GL_ARRAY_BUFFER, self.vertexBuffer.nbytes, self.vertexBuffer, GL_STATIC_DRAW)

        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 3 * 4, ctypes.c_void_p(0))

        glDrawArrays(GL_TRIANGLES, 0, 36)

        glDisableVertexAttribArray(0)
        glDepthMask(GL_TRUE)
