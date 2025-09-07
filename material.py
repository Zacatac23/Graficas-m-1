import numpy as np
from physics_utils import refractVector, totalInternalReflection, fresnel, reflectVector

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
        # Tu código original de Phong - SIN CAMBIOS
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
                offset = 0.001
                shadowRayOrigin = [intercept.point[i] + intercept.normal[i] * offset for i in range(3)]
                shadowIntercept = renderer.glCastRay(shadowRayOrigin, lightDir, intercept.obj)
                
                if shadowIntercept is None:
                    lightColor = light.GetLightColor(intercept)
                    
                    # Componente difusa
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
        
        # NUEVAS IMPLEMENTACIONES FÍSICAMENTE AVANZADAS:
        
        # Reflexión avanzada con Fresnel
        if self.reflectivity > 0 and hasattr(renderer, 'rayDepth') and renderer.rayDepth < 3:
            reflectionColor = self._getAdvancedReflectionColor(intercept, renderer)
            if reflectionColor:
                for i in range(3):
                    finalColor[i] = finalColor[i] * (1 - self.reflectivity) + reflectionColor[i] * self.reflectivity
        
        # Transparencia avanzada con refracción física
        if self.transparency > 0 and hasattr(renderer, 'rayDepth') and renderer.rayDepth < 3:
            transmissionColor = self._getAdvancedTransmissionColor(intercept, renderer)
            if transmissionColor:
                for i in range(3):
                    finalColor[i] = finalColor[i] * (1 - self.transparency) + transmissionColor[i] * self.transparency
        
        # Clamping to [0,1]
        finalColor = [min(1, max(0, finalColor[i])) for i in range(3)]
        return finalColor
    
    def _getAdvancedReflectionColor(self, intercept, renderer):
        """Reflexión usando física avanzada con Fresnel"""
        viewDir = np.array(intercept.rayDirection)
        normal = np.array(intercept.normal)
        
        # Calcular coeficientes de Fresnel
        n1 = 1.0  # Aire
        n2 = self.refractive_index
        Kr, Kt = fresnel(normal, viewDir, n1, n2)
        
        # Reflexión perfecta
        reflectDir = reflectVector(normal, viewDir)
        
        # Lanzar rayo de reflexión
        offset = 0.001
        reflectOrigin = [intercept.point[i] + normal[i] * offset for i in range(3)]
        
        # Incrementar profundidad del rayo
        if not hasattr(renderer, 'rayDepth'):
            renderer.rayDepth = 0
        renderer.rayDepth += 1
        
        reflectHit = renderer.glCastRay(reflectOrigin, reflectDir, intercept.obj)
        
        renderer.rayDepth -= 1
        
        if reflectHit and reflectHit.obj.material:
            reflectedColor = reflectHit.obj.material.GetSurfaceColor(reflectHit, renderer)
            # Aplicar coeficiente de Fresnel
            return [c * Kr for c in reflectedColor]
        else:
            # Usar environment map si está disponible
            if hasattr(renderer, 'environmentMap') and renderer.environmentMap:
                envColor = renderer.environmentMap.getColorFromDirection(reflectDir)
                return [c * Kr for c in envColor]
            else:
                # Cielo azul simple
                skyColor = [0.5 + reflectDir[1] * 0.3, 0.7 + reflectDir[1] * 0.2, 0.9]
                return [c * Kr for c in skyColor]
    
    def _getAdvancedTransmissionColor(self, intercept, renderer):
        """Refracción usando física avanzada con Ley de Snell"""
        viewDir = np.array(intercept.rayDirection)
        normal = np.array(intercept.normal)
        
        n1 = 1.0  # Aire
        n2 = self.refractive_index
        
        # Verificar reflexión interna total
        if totalInternalReflection(normal, viewDir, n1, n2):
            # Si hay reflexión interna total, actuar como espejo perfecto
            return self._getAdvancedReflectionColor(intercept, renderer)
        
        # Calcular coeficientes de Fresnel
        Kr, Kt = fresnel(normal, viewDir, n1, n2)
        
        # Calcular dirección de refracción
        try:
            refractDir = refractVector(normal, viewDir, n1, n2)
        except:
            # Si falla el cálculo, usar reflexión
            return self._getAdvancedReflectionColor(intercept, renderer)
        
        # Lanzar rayo de refracción
        offset = 0.001
        refractOrigin = [intercept.point[i] - normal[i] * offset for i in range(3)]
        
        # Incrementar profundidad del rayo
        if not hasattr(renderer, 'rayDepth'):
            renderer.rayDepth = 0
        renderer.rayDepth += 1
        
        refractHit = renderer.glCastRay(refractOrigin, refractDir, intercept.obj)
        
        renderer.rayDepth -= 1
        
        if refractHit and refractHit.obj.material:
            refractedColor = refractHit.obj.material.GetSurfaceColor(refractHit, renderer)
            # Aplicar coeficiente de Fresnel para transmisión
            return [c * Kt for c in refractedColor]
        else:
            # Usar environment map si está disponible
            if hasattr(renderer, 'environmentMap') and renderer.environmentMap:
                envColor = renderer.environmentMap.getColorFromDirection(refractDir)
                return [c * Kt for c in envColor]
            else:
                # Color de fondo
                return [0.9 * Kt, 0.9 * Kt, 1.0 * Kt]