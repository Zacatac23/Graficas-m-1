
from numpy import array, float32
import glm
from OpenGL.GL import * 
from OpenGL.GL.shaders import compileProgram, compileShader
import pygame


skybox_vertex_shader = '''
#version 450 core

layout (location = 0) in vec3 inPosition;

uniform mat4 viewMatrix;
uniform mat4 projectionMatrix;


out vec3 texCoords;

void main()
{
    texCoords = inPosition;
    mat4 vm = mat4(mat3(viewMatrix));
    gl_Position = projectionMatrix * vm * vec4(inPosition, 1.0);
}

'''


skybox_fragment_shader = '''
#version 450 core

uniform samplerCube skybox;

in vec3 texCoords;

out vec4 fragColor;

void main()
{
    fragColor = texture(skybox, texCoords);
}

'''


class Skybox(object):
	def __init__(self, textureList):
		self.cameraRef = None
		
		skyboxVertices = [-1.0,  1.0, -1.0,
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
						   1.0, -1.0,  1.0 ]
		
		self.vertexBuffer = array(skyboxVertices, dtype = float32 )
		self.VBO = glGenBuffers(1)
		
		self.shaders = compileProgram(compileShader(skybox_vertex_shader, GL_VERTEX_SHADER),
									  compileShader(skybox_fragment_shader, GL_FRAGMENT_SHADER) )
		
		self.texture = glGenTextures(1)
		glBindTexture(GL_TEXTURE_CUBE_MAP, self.texture)
		
		for i in range(len(textureList)):
			texture = pygame.image.load(textureList[i])
			
			# Detectar si la imagen tiene canal alfa (PNG con transparencia)
			if texture.get_alpha() or texture.get_flags() & pygame.SRCALPHA:
				textureData = pygame.image.tostring(texture, "RGBA", False)
				format = GL_RGBA
			else:
				textureData = pygame.image.tostring(texture, "RGB", False)
				format = GL_RGB
			
			glTexImage2D(GL_TEXTURE_CUBE_MAP_POSITIVE_X + i,
						 0,
						 format,
						 texture.get_width(),
						 texture.get_height(),
						 0,
						 format,
						 GL_UNSIGNED_BYTE,
						 textureData)
			
		glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
		glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
		glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
		glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
		glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_R, GL_CLAMP_TO_EDGE)
		

	def Render(self):
		if self.shaders == None:
			return
		
		glUseProgram(self.shaders)
		
		if self.cameraRef is not None:
			glUniformMatrix4fv( glGetUniformLocation(self.shaders, "viewMatrix"),
								1, GL_FALSE, glm.value_ptr( self.cameraRef.viewMatrix) )
			
			glUniformMatrix4fv( glGetUniformLocation(self.shaders, "projectionMatrix"),
								1, GL_FALSE, glm.value_ptr( self.cameraRef.projectionMatrix) )
		
		# Deshabilitar escritura en el depth buffer
		glDepthMask(GL_FALSE)
		# Cambiar la función de profundidad para que el skybox siempre esté atrás
		glDepthFunc(GL_LEQUAL)
		
		glBindTexture(GL_TEXTURE_CUBE_MAP, self.texture)
		
		glBindBuffer(GL_ARRAY_BUFFER, self.VBO)
		
		glBufferData(GL_ARRAY_BUFFER,
					 self.vertexBuffer.nbytes,
					 self.vertexBuffer,
					 GL_STATIC_DRAW)
		
		glEnableVertexAttribArray(0)
		
		glVertexAttribPointer(0,
							  3,
							  GL_FLOAT,
							  GL_FALSE,
							  4 * 3,
							  ctypes.c_void_p(0) )
		
		
		glDrawArrays(GL_TRIANGLES, 0, 36)
		
		glDisableVertexAttribArray(0)

		# Restaurar configuración de profundidad
		glDepthFunc(GL_LESS)
		glDepthMask(GL_TRUE)
		
