import glm

class Camera(object):
    def __init__(self, width, height):
        self.screenWidth = width
        self.screenHeight = height
        
        self.position = glm.vec3(0,0,0)

        # Angulos de Euler
        self.rotation = glm.vec3(0,0,0)

        self.viewMatrix = None

        # LookAt support (when using orbit camera)
        self.target = None
        self.useLookAt = False
        
        # Valores predeterminados mejorados para evitar problemas de clipping
        self.CreateProjectionMatrix(60, 0.5, 1000)
        
        # Propiedades para control mejorado de la cámara
        self.minDistance = 1.0    # Distancia mínima al objetivo para evitar entrar en objetos
        self.maxDistance = 100.0  # Distancia máxima para limitar el zoom
        self.distance = 10.0      # Distancia actual al objetivo (para modo orbital)
        self.orbitCenter = glm.vec3(0,0,0)  # Centro de órbita
        
        # Colisión simple (para evitar entrar en objetos)
        self.collisionEnabled = True


    def Update(self):
        # If lookAt mode is enabled, compute view from position->target
        if hasattr(self, 'useLookAt') and self.useLookAt and self.target is not None:
            self.viewMatrix = glm.lookAt(self.position, self.target, glm.vec3(0,1,0))
            return

        # M = T * R
        # R = pitchMat * yawMat * rollMat

        identity = glm.mat4(1)

        translateMat = glm.translate(identity, self.position)

        pitchMat = glm.rotate(identity, glm.radians(self.rotation.x), glm.vec3(1,0,0))
        yawMat =   glm.rotate(identity, glm.radians(self.rotation.y), glm.vec3(0,1,0))
        rollMat =  glm.rotate(identity, glm.radians(self.rotation.z), glm.vec3(0,0,1))

        rotationMat = pitchMat * yawMat * rollMat

        camMat = translateMat * rotationMat

        self.viewMatrix = glm.inverse(camMat)

    def LookAt(self, target):
        """Enable look-at mode and set the target point (glm.vec3)."""
        self.target = target
        self.useLookAt = True
        self.orbitCenter = target  # También actualizar el centro de órbita
        
        # Calcular la distancia actual para referencia
        if hasattr(self, 'position'):
            self.distance = glm.distance(self.position, target)

    def StopLookAt(self):
        self.target = None
        self.useLookAt = False


    def CreateProjectionMatrix(self, fov, nearPlane, farPlane):
        """Create a perspective projection matrix with the given parameters.
        
        Args:
            fov: Field of view in degrees
            nearPlane: Distance to near clipping plane (debe ser >0)
            farPlane: Distance to far clipping plane
        """
        # Asegurar que el nearPlane nunca sea demasiado pequeño para evitar problemas
        nearPlane = max(0.1, nearPlane)
        self.projectionMatrix = glm.perspective(
            glm.radians(fov),
            self.screenWidth / self.screenHeight,
            nearPlane,
            farPlane
        )
        
    def SetOrbitDistance(self, distance):
        """Set the camera distance from orbit center with limits to prevent
        getting too close to objects or too far away.
        
        Args:
            distance: Desired distance to orbit center
        """
        self.distance = max(self.minDistance, min(self.maxDistance, distance))
        if self.useLookAt and self.target is not None:
            # Calcular la dirección normalizada desde el target a la cámara
            direction = glm.normalize(self.position - self.target)
            # Establecer la nueva posición basada en la dirección y la nueva distancia
            self.position = self.target + direction * self.distance
            
    def ZoomIn(self, amount):
        """Zoom in by decreasing orbit distance.
        
        Args:
            amount: Amount to zoom in
        """
        self.SetOrbitDistance(self.distance - amount)
        
    def ZoomOut(self, amount):
        """Zoom out by increasing orbit distance.
        
        Args:
            amount: Amount to zoom out
        """
        self.SetOrbitDistance(self.distance + amount)
    
    def SetOrbitLimits(self, minDist, maxDist):
        """Set minimum and maximum orbit distances.
        
        Args:
            minDist: Minimum allowed distance (to prevent entering objects)
            maxDist: Maximum allowed distance
        """
        self.minDistance = max(0.1, minDist)  # Siempre al menos 0.1
        self.maxDistance = max(self.minDistance + 1.0, maxDist)  # Siempre mayor que minDistance
        
        # Ajustar la distancia actual si está fuera de los límites
        if self.useLookAt and self.target is not None:
            self.distance = max(self.minDistance, min(self.maxDistance, self.distance))
            direction = glm.normalize(self.position - self.target)
            self.position = self.target + direction * self.distance
            
    def UpdateOrbitPosition(self, phi, theta):
        """Update camera position based on spherical coordinates around orbit center.
        
        Args:
            phi: Elevation angle in radians
            theta: Azimuth angle in radians
        """
        if self.useLookAt and self.target is not None:
            # Calcular posición usando coordenadas esféricas
            horiz = self.distance * glm.cos(phi)
            x = self.target.x + horiz * glm.sin(theta)
            y = self.target.y + self.distance * glm.sin(phi)
            z = self.target.z + horiz * glm.cos(theta)
            
            self.position = glm.vec3(x, y, z)
            
    def SetSafeStartPosition(self, target, radius, theta=0.0, phi=0.5):
        """Set a safe initial camera position based on object bounding sphere.
        
        Args:
            target: Center of the bounding sphere
            radius: Radius of the bounding sphere
            theta: Initial azimuth angle in radians
            phi: Initial elevation angle in radians
        """
        # Establecer una distancia segura (3 veces el radio)
        safe_distance = radius * 3.0
        
        # Configurar límites basados en el radio del objeto
        self.SetOrbitLimits(radius * 1.5, radius * 15.0)
        
        # Establecer el target y actualizar la posición orbital
        self.LookAt(target)
        self.distance = safe_distance
        self.UpdateOrbitPosition(phi, theta)