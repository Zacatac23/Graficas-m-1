import numpy as np

class Light(object):
    def __init__(self, color = [1, 1, 1], intensity = 1.0, lightType = "None"):
        self.color = color
        self.intensity = intensity
        self.type = lightType

    
    def GetLightColor(self, intercept = None):
        return [(i * self.intensity) for i in self.color]

class AmbientLight(Light):
    def __init__(self, color = [1, 1, 1], intensity = 0.1):
        super().__init__(color, intensity, "Ambient")

class DirectionalLight(Light):
    def __init__(self, color = [1, 1, 1], intensity = 1.0, direction = [0,  -1, 0]):
        super().__init__(color, intensity, "Directional")
        self.direction = direction / np.linalg.norm(direction)

    def GetLightColor(self, intercept = None):
        lightColor =super().GetLightColor()

        if intercept:
            # SurfaceIntensity = NORMAL(de la superficie) producto punto con la -DIRECCION DE LA LUZ
            dir = [(i * -1) for i in self.direction]
            surfaceIntensity = np.dot(intercept.normal, dir)
            surfaceIntensity = max(0, min(1, surfaceIntensity))
            lightColor = [(i * surfaceIntensity) for i in lightColor]


        return lightColor