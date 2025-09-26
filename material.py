import numpy as np

class Material(object):
    def __init__(self, diffuse=[1,1,1], specular=[1,1,1], shininess=32, ambient=None, 
                 reflectivity=0.0, transparency=0.0, refractive_index=1.0):
        self.diffuse = diffuse
        self.specular = specular
        self.shininess = shininess
        self.ambient = ambient if ambient else diffuse
        self.reflectivity = reflectivity
        self.transparency = transparency
        self.refractive_index = refractive_index
    
    def GetSurfaceColor(self, intercept, renderer):
        """
        Simplified surface color calculation with basic Phong lighting.
        NO advanced reflections to avoid recursion problems.
        """
        finalColor = [0, 0, 0]
        
        # Componente ambiente
        for light in renderer.lights:
            if light.type == "Ambient":
                ambientColor = [self.ambient[i] * light.GetLightColor()[i] for i in range(3)]
                finalColor = [finalColor[i] + ambientColor[i] for i in range(3)]
        
        # Componentes difusa y especular
        for light in renderer.lights:
            if light.type == "Directional":
                lightDir = [-i for i in light.direction]
                
                # Shadow ray para verificar si hay objetos bloqueando la luz
                offset = 0.001
                shadowRayOrigin = [intercept.point[i] + intercept.normal[i] * offset for i in range(3)]
                shadowIntercept = renderer.glCastRay(shadowRayOrigin, lightDir, intercept.obj)
                
                # Solo aplicar luz si no hay sombra
                if shadowIntercept is None:
                    lightColor = light.GetLightColor(intercept)
                    
                    # Componente difusa (Lambert)
                    diffuseColor = [self.diffuse[i] * lightColor[i] for i in range(3)]
                    finalColor = [finalColor[i] + diffuseColor[i] for i in range(3)]
                    
                    # Componente especular (Phong)
                    if hasattr(renderer.camera, 'translation'):
                        viewDir = np.array(renderer.camera.translation) - np.array(intercept.point)
                        viewDir = viewDir / np.linalg.norm(viewDir)
                        
                        lightDirNorm = np.array(lightDir) / np.linalg.norm(lightDir)
                        reflectDir = 2 * np.dot(intercept.normal, lightDirNorm) * intercept.normal - lightDirNorm
                        
                        specularIntensity = max(0, np.dot(viewDir, reflectDir)) ** self.shininess
                        specularColor = [self.specular[i] * lightColor[i] * specularIntensity for i in range(3)]
                        finalColor = [finalColor[i] + specularColor[i] for i in range(3)]
        
        # REFLEXIONES SIMPLES (sin recursión profunda)
        if self.reflectivity > 0:
            reflectionColor = self._getSimpleReflection(intercept, renderer)
            if reflectionColor:
                for i in range(3):
                    finalColor[i] = finalColor[i] * (1 - self.reflectivity) + reflectionColor[i] * self.reflectivity
        
        # Clamping final a [0,1]
        finalColor = [min(1, max(0, finalColor[i])) for i in range(3)]
        return finalColor
    
    def _getSimpleReflection(self, intercept, renderer):
        """
        Reflexión simple sin recursión profunda.
        Solo 1 nivel de reflexión para evitar loops infinitos.
        """
        # Verificar si ya estamos en una reflexión (evitar recursión)
        if hasattr(renderer, 'reflection_depth'):
            if renderer.reflection_depth >= 1:  # Máximo 1 nivel
                return None
        else:
            renderer.reflection_depth = 0
        
        viewDir = np.array(intercept.rayDirection)
        normal = np.array(intercept.normal)
        
        # Calcular dirección de reflexión perfecta
        reflectDir = viewDir - 2 * np.dot(viewDir, normal) * normal
        
        # Lanzar rayo de reflexión
        offset = 0.001
        reflectOrigin = [intercept.point[i] + normal[i] * offset for i in range(3)]
        
        # Incrementar depth y lanzar rayo
        renderer.reflection_depth += 1
        reflectHit = renderer.glCastRay(reflectOrigin, reflectDir, intercept.obj)
        renderer.reflection_depth -= 1
        
        if reflectHit and reflectHit.obj.material:
            # Para objetos reflejados, usar SOLO componentes básicos (sin más reflexiones)
            return self._getBasicColor(reflectHit, renderer)
        else:
            # Color de cielo/ambiente simple
            return [0.7 + reflectDir[1] * 0.2, 0.8 + reflectDir[1] * 0.1, 0.9]
    
    def _getBasicColor(self, intercept, renderer):
        """
        Color básico sin reflexiones - para objetos en reflexiones.
        Solo diffuse + ambient + un poco de specular.
        """
        color = [0, 0, 0]
        
        # Solo ambiente y difuso básico
        for light in renderer.lights:
            if light.type == "Ambient":
                ambientColor = [self.ambient[i] * light.GetLightColor()[i] for i in range(3)]
                color = [color[i] + ambientColor[i] for i in range(3)]
            elif light.type == "Directional":
                lightDir = [-i for i in light.direction]
                lightColor = light.GetLightColor(intercept)
                diffuseColor = [intercept.obj.material.diffuse[i] * lightColor[i] for i in range(3)]
                color = [color[i] + diffuseColor[i] for i in range(3)]
        
        return [min(1, max(0, color[i])) for i in range(3)]