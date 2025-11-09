from OpenGL.GL import *
from obj import Obj
from buffer import Buffer

import glm

import pygame

# module-level cached 1x1 white texture used as a fallback when a model has no textures
_DEFAULT_WHITE_TEXTURE = None

def _get_default_white_texture():
	global _DEFAULT_WHITE_TEXTURE
	if _DEFAULT_WHITE_TEXTURE is not None:
		return _DEFAULT_WHITE_TEXTURE

	# create a 1x1 white texture
	tex = glGenTextures(1)
	glBindTexture(GL_TEXTURE_2D, tex)
	white_pixel = (GLubyte * 3)(255, 255, 255)
	glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, 1, 1, 0, GL_RGB, GL_UNSIGNED_BYTE, white_pixel)
	glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
	glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)

	_DEFAULT_WHITE_TEXTURE = tex
	return _DEFAULT_WHITE_TEXTURE


def CreateColorTexture(rgb):
	"""Create and return a 1x1 GL texture filled with RGB tuple (0..1 floats).
	Returns the GL texture handle.
	"""
	r = int(max(0, min(1, rgb[0])) * 255)
	g = int(max(0, min(1, rgb[1])) * 255)
	b = int(max(0, min(1, rgb[2])) * 255)
	tex = glGenTextures(1)
	glBindTexture(GL_TEXTURE_2D, tex)
	pixel = (GLubyte * 3)(r, g, b)
	glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, 1, 1, 0, GL_RGB, GL_UNSIGNED_BYTE, pixel)
	glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
	glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
	return tex




class Model(object):
	def __init__(self, filename):
		self.objFile = Obj(filename)

		self.position = glm.vec3(0,0,0)
		self.rotation = glm.vec3(0,0,0)
		self.scale = glm.vec3(1,1,1)

		self.BuildBuffers()

		self.textures = []

		# textures start empty; models can be populated explicitly by the caller

		self.visible = True

		# shader program assigned to this model (GL program handle). If None, renderer uses its activeShader.
		self.shaderProgram = None


	def GetModelMatrix(self):

		identity = glm.mat4(1)

		translateMat = glm.translate(identity, self.position)

		pitchMat = glm.rotate(identity, glm.radians(self.rotation.x), glm.vec3(1,0,0))
		yawMat =   glm.rotate(identity, glm.radians(self.rotation.y), glm.vec3(0,1,0))
		rollMat =  glm.rotate(identity, glm.radians(self.rotation.z), glm.vec3(0,0,1))

		rotationMat = pitchMat * yawMat * rollMat

		scaleMat = glm.scale(identity, self.scale)

		return translateMat * rotationMat * scaleMat


	def BuildBuffers(self):

		positions = []
		texCoords = []
		normals = []

		self.vertexCount = 0

		# precompute vertex bounds for fallback planar UVs (X,Z projection)
		if len(self.objFile.vertices) > 0:
			xs = [v[0] for v in self.objFile.vertices]
			zs = [v[2] for v in self.objFile.vertices]
			minx = min(xs); maxx = max(xs)
			minz = min(zs); maxz = max(zs)
			range_x = maxx - minx if (maxx - minx) != 0 else 1.0
			range_z = maxz - minz if (maxz - minz) != 0 else 1.0
		else:
			minx = minz = 0.0
			range_x = range_z = 1.0

		for face in self.objFile.faces:
			facePositions = []
			faceTexCoords = []
			faceNormals = []

			# helper to resolve obj indices (handles negative indices)
			def resolve_index(container, idx):
				if idx == 0:
					return None
				if idx > 0:
					i = idx - 1
				else:
					# negative index: relative to end
					i = len(container) + idx
				if i < 0 or i >= len(container):
					return None
				return container[i]

			for j in range(len(face)):
				v_idx, vt_idx, vn_idx = face[j][0], face[j][1], face[j][2]
				pos = resolve_index(self.objFile.vertices, v_idx)
				if pos is None:
					pos = [0.0, 0.0, 0.0]
				facePositions.append(pos)

				tex = resolve_index(self.objFile.texCoords, vt_idx)
				if tex is None:
					# Fallback: generate planar UVs from X/Z coordinates
					tex = [ (pos[0] - minx) / range_x, (pos[2] - minz) / range_z ]
				faceTexCoords.append(tex)

				norm = resolve_index(self.objFile.normals, vn_idx)
				if norm is None:
					norm = [0.0, 0.0, 1.0]
				faceNormals.append(norm)


			# push triangle vertices (first three)
			for value in facePositions[0]: positions.append(value)
			for value in facePositions[1]: positions.append(value)
			for value in facePositions[2]: positions.append(value)

			for value in faceTexCoords[0]: texCoords.append(value)
			for value in faceTexCoords[1]: texCoords.append(value)
			for value in faceTexCoords[2]: texCoords.append(value)

			for value in faceNormals[0]: normals.append(value)
			for value in faceNormals[1]: normals.append(value)
			for value in faceNormals[2]: normals.append(value)

			self.vertexCount += 3

			if len(face) == 4:
				for value in facePositions[0]: positions.append(value)
				for value in facePositions[2]: positions.append(value)
				for value in facePositions[3]: positions.append(value)

				for value in faceTexCoords[0]: texCoords.append(value)
				for value in faceTexCoords[2]: texCoords.append(value)
				for value in faceTexCoords[3]: texCoords.append(value)

				for value in faceNormals[0]: normals.append(value)
				for value in faceNormals[2]: normals.append(value)
				for value in faceNormals[3]: normals.append(value)

				self.vertexCount += 3

		self.posBuffer = Buffer(positions)
		self.texCoordsBuffer = Buffer(texCoords)
		self.normalsBuffer = Buffer(normals)


	def AddTexture(self, filename):
		# Try to load with Pillow to avoid libpng iCCP warnings on some PNGs
		# If Pillow is not available, fall back to pygame.image.load
		try:
			from PIL import Image
			im = Image.open(filename).convert('RGB')
			width, height = im.size
			# Pillow returns top-to-bottom; match previous pygame behavior which flipped vertically
			im = im.transpose(Image.FLIP_TOP_BOTTOM)
			# Pillow returns bytes in row-major RGB order
			textureData = im.tobytes('raw', 'RGB')
		except Exception:
			# fallback to pygame (existing behavior)
			textureSurface = pygame.image.load(filename)
			width = textureSurface.get_width()
			height = textureSurface.get_height()
			textureData = pygame.image.tostring(textureSurface, "RGB", True)

		texture = glGenTextures(1)
		glBindTexture(GL_TEXTURE_2D, texture)

		glTexImage2D(GL_TEXTURE_2D,
				  0,
				  GL_RGB,
				  width,
				  height,
				  0,
				  GL_RGB,
				  GL_UNSIGNED_BYTE,
				  textureData)

		glGenerateMipmap(GL_TEXTURE_2D)

		self.textures.append(texture)


	def Render(self):

		if not self.visible:
			return

		# Dar la textura
		# Bind textures with sensible fallbacks so fragment shaders that expect
		# tex0 and tex1 always have something bound.
		default_tex = _get_default_white_texture()
		if len(self.textures) == 0:
			# no textures: bind white to both tex0 and tex1
			glActiveTexture(GL_TEXTURE0)
			glBindTexture(GL_TEXTURE_2D, default_tex)
			glActiveTexture(GL_TEXTURE1)
			glBindTexture(GL_TEXTURE_2D, default_tex)
		elif len(self.textures) == 1:
			# one texture: bind it to tex0 and white to tex1
			glActiveTexture(GL_TEXTURE0)
			glBindTexture(GL_TEXTURE_2D, self.textures[0])
			glActiveTexture(GL_TEXTURE1)
			glBindTexture(GL_TEXTURE_2D, default_tex)
		else:
			# two or more textures: bind them to successive units
			for i in range(len(self.textures)):
				glActiveTexture(GL_TEXTURE0 + i)
				glBindTexture(GL_TEXTURE_2D, self.textures[i])


		self.posBuffer.Use(0, 3)
		self.texCoordsBuffer.Use(1, 2)
		self.normalsBuffer.Use(2, 3)


		glDrawArrays(GL_TRIANGLES, 0, self.vertexCount)

		glDisableVertexAttribArray(0)
		glDisableVertexAttribArray(1)
		glDisableVertexAttribArray(2)




