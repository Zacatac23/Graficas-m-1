
class Obj(object):
	def __init__(self, filename):
		# Asumiendo que el archivo es un formato .obj
		with open(filename, "r") as file:
			lines = file.read().splitlines()

		self.vertices = []
		self.texCoords = []
		self.normals = []
		self.faces = []

		for line in lines:
			# Si la linea no cuenta con un prefijo y un valor,
			# seguimos a la siguiente la linea

			line = line.rstrip()

			try:
				prefix, value = line.split(" ", 1)
			except:
				continue
			
			# Dependiendo del prefijo, parseamos y guardamos
			# la informacion en el contenedor correcto
			
			if prefix == "v": # Vertices
				vert = list(map(float, value.split()))
				self.vertices.append(vert)
				
			elif prefix == "vt": # Coordenadas de textura
				vts = list(map(float, value.split()))
				# keep only u,v
				if len(vts) >= 2:
					self.texCoords.append([vts[0], vts[1]])
				elif len(vts) == 1:
					self.texCoords.append([vts[0], 0.0])
				else:
					self.texCoords.append([0.0, 0.0])
				
			elif prefix == "vn": # Normales
				norm = list(map(float, value.split()))
				# ensure 3 components
				if len(norm) >= 3:
					self.normals.append([norm[0], norm[1], norm[2]])
				elif len(norm) == 2:
					self.normals.append([norm[0], norm[1], 0.0])
				elif len(norm) == 1:
					self.normals.append([norm[0], 0.0, 0.0])
				else:
					self.normals.append([0.0, 0.0, 1.0])
				
			elif prefix == "f": # Caras
				face = []
				verts = value.split()
				for vert in verts:
					parts = vert.split('/')
					# parse v/vt/vn with missing fields allowed
					try:
						v = int(parts[0]) if parts[0] != '' else 0
					except:
						v = 0
					vt = 0
					vn = 0
					if len(parts) > 1 and parts[1] != '':
						try:
							vt = int(parts[1])
						except:
							vt = 0
					if len(parts) > 2 and parts[2] != '':
						try:
							vn = int(parts[2])
						except:
							vn = 0
					face.append([v, vt, vn])
				self.faces.append(face)