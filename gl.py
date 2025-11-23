import glm # pip install PyGLM
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader

from camera import Camera
from skybox import Skybox

class Renderer(object):
    def __init__(self, screen):
        self.screen = screen
        _,_, self.width, self.height = screen.get_rect()
        
        # Color de fondo más oscuro para ver mejor el skybox
        glClearColor(0.05, 0.05, 0.05, 1.0)

        glEnable(GL_DEPTH_TEST)
        glViewport(0,0, self.width, self.height)

        self.camera = Camera(self.width, self.height)

        self.scene = []
        

        self.filledMode = False
        self.ToggleFilledMode()

        self.activeShader = None
        self.active_postProcessing_Shader = None


        self.skybox = None

        self.pointLight = glm.vec3(0,0,0)
        self.ambientLight = 0.1


        self.value = 0.0;
        self.elapsedTime = 0.0;

        self.CreateFrameBuffer()



    def CreateSkybox(self, textureList):
        self.skybox = Skybox(textureList)
        self.skybox.cameraRef = self.camera


    def CreateFrameBuffer(self):
        # Crear frameBuffer
        self.FBO = glGenFramebuffers(1)
        glBindFramebuffer(GL_FRAMEBUFFER, self.FBO)

        # Crear la textura del framebuffer
        self.FBOTexture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.FBOTexture)
        glTexImage2D(GL_TEXTURE_2D,0, GL_RGBA, self.width, self.height, 0, GL_RGBA, GL_UNSIGNED_BYTE,None)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, self.FBOTexture, 0)

        # Create depthTexture/Z buffer
        self.depthTexture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.depthTexture)
        glTexImage2D(GL_TEXTURE_2D,0, GL_DEPTH_COMPONENT24, self.width, self.height, 0, GL_DEPTH_COMPONENT, GL_FLOAT ,None)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_TEXTURE_2D, self.depthTexture, 0)

        # Unbind
        glBindFramebuffer(GL_FRAMEBUFFER, 0)



    def ToggleFilledMode(self):
        self.filledMode = not self.filledMode

        if self.filledMode:
            glEnable(GL_CULL_FACE)
            glPolygonMode(GL_FRONT, GL_FILL)
        else:
            glDisable(GL_CULL_FACE)
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)


    def SetShaders(self, vertexShader, fragmentShader):
        if vertexShader is not None and fragmentShader is not None:
            self.activeShader = compileProgram( compileShader(vertexShader, GL_VERTEX_SHADER),
                                                compileShader(fragmentShader, GL_FRAGMENT_SHADER) )
        else:
            self.activeShader = None


    def CompileProgram(self, vertexShader, fragmentShader):
        """Compile and return a shader program without changing the renderer's activeShader."""
        if vertexShader is None or fragmentShader is None:
            return None
        return compileProgram( compileShader(vertexShader, GL_VERTEX_SHADER),
                               compileShader(fragmentShader, GL_FRAGMENT_SHADER) )


    def SetPostProcessingShaders(self, vertexShader, fragmentShader):
        if vertexShader is not None and fragmentShader is not None:
            self.active_postProcessing_Shader = compileProgram( compileShader(vertexShader, GL_VERTEX_SHADER),
                                                compileShader(fragmentShader, GL_FRAGMENT_SHADER) )
        else:
            self.active_postProcessing_Shader = None


    def Render(self):
        if self.active_postProcessing_Shader is not None:
            glBindFramebuffer(GL_FRAMEBUFFER, self.FBO)

        glClear( GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT )

        self.camera.Update()

        if self.skybox is not None:
            self.skybox.Render()


        for obj in self.scene:

            # choose program: per-model shader if assigned, otherwise fallback to activeShader
            program = obj.shaderProgram if hasattr(obj, 'shaderProgram') and obj.shaderProgram is not None else self.activeShader

            if program is not None:
                glUseProgram(program)

                # common uniforms
                loc = glGetUniformLocation(program, "viewMatrix")
                if loc != -1:
                    glUniformMatrix4fv(loc, 1, GL_FALSE, glm.value_ptr(self.camera.viewMatrix))

                loc = glGetUniformLocation(program, "projectionMatrix")
                if loc != -1:
                    glUniformMatrix4fv(loc, 1, GL_FALSE, glm.value_ptr(self.camera.projectionMatrix))

                loc = glGetUniformLocation(program, "pointLight")
                if loc != -1:
                    glUniform3fv(loc, 1, glm.value_ptr(self.pointLight))

                loc = glGetUniformLocation(program, "ambientLight")
                if loc != -1:
                    glUniform1f(loc, self.ambientLight)

                loc = glGetUniformLocation(program, "value")
                if loc != -1:
                    glUniform1f(loc, self.value)

                loc = glGetUniformLocation(program, "time")
                if loc != -1:
                    glUniform1f(loc, self.elapsedTime)

                # set samplers to the expected texture units if present
                loc = glGetUniformLocation(program, "tex0")
                if loc != -1:
                    glUniform1i(loc, 0)
                loc = glGetUniformLocation(program, "tex1")
                if loc != -1:
                    glUniform1i(loc, 1)

                # fresh_fragment_shader supports a baseColor and useTexture uniform.
                loc = glGetUniformLocation(program, "baseColor")
                if loc != -1:
                    # default white; per-model color can be provided by a 1x1 texture instead
                    glUniform3fv(loc, 1, glm.value_ptr(glm.vec3(1.0, 1.0, 1.0)))

                loc = glGetUniformLocation(program, "useTexture")
                if loc != -1:
                    # enable texture sampling if the model has textures
                    use_tex = 1 if (hasattr(obj, 'textures') and len(obj.textures) > 0) else 0
                    glUniform1i(loc, use_tex)

                # model matrix specific uniform
                loc = glGetUniformLocation(program, "modelMatrix")
                if loc != -1:
                    glUniformMatrix4fv(loc, 1, GL_FALSE, glm.value_ptr(obj.GetModelMatrix()))

            # Render the object (Model.Render will bind textures and vertex attribs)
            obj.Render()


        if self.active_postProcessing_Shader is not None:
            glBindFramebuffer(GL_FRAMEBUFFER, 0)
            glClear(GL_COLOR_BUFFER_BIT)

            glDisable(GL_DEPTH_TEST)

            glUseProgram(self.active_postProcessing_Shader)

            glActiveTexture(GL_TEXTURE0)
            glBindTexture(GL_TEXTURE_2D, self.FBOTexture)

            glActiveTexture(GL_TEXTURE1)
            glBindTexture(GL_TEXTURE_2D, self.depthTexture)

            glUniform1i( glGetUniformLocation(self.active_postProcessing_Shader, "frameBuffer"), 0)
            glUniform1i( glGetUniformLocation(self.active_postProcessing_Shader, "depthTexture"), 1)

            glUniform1f( glGetUniformLocation(self.active_postProcessing_Shader, "time"), self.elapsedTime )

            glDrawArrays(GL_QUADS, 0, 4)

            glEnable(GL_DEPTH_TEST)

