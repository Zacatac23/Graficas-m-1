from OpenGL.GL import *
from obj import Obj
from buffer import Buffer

import glm

import pygame

class Model(object):
	def __init__(self, filename):
		self.objFile = Obj(filename)

		self.position = glm.vec3(0,0,0)
		self.rotation = glm.vec3(0,0,0)
		self.scale = glm.vec3(1,1,1)

		self.BuildBuffers()

		# Compute bounding box and bounding sphere radius from loaded vertices
		if len(self.objFile.vertices) > 0:
			xs = [v[0] for v in self.objFile.vertices]
			ys = [v[1] for v in self.objFile.vertices]
			zs = [v[2] for v in self.objFile.vertices]
			self.bounds_min = glm.vec3(min(xs), min(ys), min(zs))
			self.bounds_max = glm.vec3(max(xs), max(ys), max(zs))
			self.bounds_center = (self.bounds_min + self.bounds_max) / 2.0
			# radius: max distance from center to any vertex
			maxd = 0.0
			for v in self.objFile.vertices:
				vx = glm.vec3(v[0], v[1], v[2])
				d = glm.length(vx - self.bounds_center)
				if d > maxd:
					maxd = d
			self.bounds_radius = maxd
		else:
			self.bounds_min = glm.vec3(0,0,0)
			self.bounds_max = glm.vec3(0,0,0)
			self.bounds_center = glm.vec3(0,0,0)
			self.bounds_radius = 1.0

		self.textures = []

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

		for face in self.objFile.faces:

			facePositions = []
			faceTexCoords = []
			faceNormals = []

			for i in range(len(face)):
				facePositions.append( self.objFile.vertices [ face[i][0] - 1 ] )
				faceTexCoords.append( self.objFile.texCoords[ face[i][1] - 1 ] )
				faceNormals.append( self.objFile.normals[ face[i][2] - 1 ] )


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
		textureSurface = pygame.image.load(filename)
		textureData = pygame.image.tostring(textureSurface, "RGB", True)

		texture = glGenTextures(1)
		glBindTexture(GL_TEXTURE_2D, texture)

		glTexImage2D(GL_TEXTURE_2D,
					 0,
					 GL_RGB,
					 textureSurface.get_width(),
					 textureSurface.get_height(),
					 0,
					 GL_RGB,
					 GL_UNSIGNED_BYTE,
					 textureData)

		glGenerateMipmap(GL_TEXTURE_2D)

		self.textures.append(texture)


	def Render(self):

		# Dar la textura
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


	def GetCenter(self):
		"""Return the model's local-space center as glm.vec3."""
		return self.bounds_center

	def GetBoundingRadius(self):
		"""Return bounding sphere radius in model local units."""
		return self.bounds_radius




