import glfw
from OpenGL.GL import *  # pylint: disable=W0614
from OpenGL.GLU import *  # pylint: disable=W0614

import glm
from utils.shaderLoader import Shader

g_vertex_buffer_data = [
        -1.0,-1.0,-1.0,
        -1.0,-1.0, 1.0,
        -1.0, 1.0, 1.0,
         1.0, 1.0,-1.0,
        -1.0,-1.0,-1.0,
        -1.0, 1.0,-1.0,
         1.0,-1.0, 1.0,
        -1.0,-1.0,-1.0,
         1.0,-1.0,-1.0,
         1.0, 1.0,-1.0,
         1.0,-1.0,-1.0,
        -1.0,-1.0,-1.0,
        -1.0,-1.0,-1.0,
        -1.0, 1.0, 1.0,
        -1.0, 1.0,-1.0,
         1.0,-1.0, 1.0,
        -1.0,-1.0, 1.0,
        -1.0,-1.0,-1.0,
        -1.0, 1.0, 1.0,
        -1.0,-1.0, 1.0,
         1.0,-1.0, 1.0,
         1.0, 1.0, 1.0,
         1.0,-1.0,-1.0,
         1.0, 1.0,-1.0,
         1.0,-1.0,-1.0,
         1.0, 1.0, 1.0,
         1.0,-1.0, 1.0,
         1.0, 1.0, 1.0,
         1.0, 1.0,-1.0,
        -1.0, 1.0,-1.0,
         1.0, 1.0, 1.0,
        -1.0, 1.0,-1.0,
        -1.0, 1.0, 1.0,
         1.0, 1.0, 1.0,
        -1.0, 1.0, 1.0,
         1.0,-1.0, 1.0]
g_uv_buffer_data = [
        0.000059, 1.0-0.000004, 
        0.000103, 1.0-0.336048, 
        0.335973, 1.0-0.335903, 
        1.000023, 1.0-0.000013, 
        0.667979, 1.0-0.335851, 
        0.999958, 1.0-0.336064, 
        0.667979, 1.0-0.335851, 
        0.336024, 1.0-0.671877, 
        0.667969, 1.0-0.671889, 
        1.000023, 1.0-0.000013, 
        0.668104, 1.0-0.000013, 
        0.667979, 1.0-0.335851, 
        0.000059, 1.0-0.000004, 
        0.335973, 1.0-0.335903, 
        0.336098, 1.0-0.000071, 
        0.667979, 1.0-0.335851, 
        0.335973, 1.0-0.335903, 
        0.336024, 1.0-0.671877, 
        1.000004, 1.0-0.671847, 
        0.999958, 1.0-0.336064, 
        0.667979, 1.0-0.335851, 
        0.668104, 1.0-0.000013, 
        0.335973, 1.0-0.335903, 
        0.667979, 1.0-0.335851, 
        0.335973, 1.0-0.335903, 
        0.668104, 1.0-0.000013, 
        0.336098, 1.0-0.000071, 
        0.000103, 1.0-0.336048, 
        0.000004, 1.0-0.671870, 
        0.336024, 1.0-0.671877, 
        0.000103, 1.0-0.336048, 
        0.336024, 1.0-0.671877, 
        0.335973, 1.0-0.335903, 
        0.667969, 1.0-0.671889, 
        1.000004, 1.0-0.671847, 
        0.667979, 1.0-0.335851
    ]


glfw.init()
glfw.window_hint(glfw.SAMPLES, 4)
glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

window  = glfw.create_window(800, 400, "title of the window", None, None)

glfw.make_context_current(window)

glClearColor(0.0, 0.0, 0.05, 0.0)
glDepthFunc(GL_LESS)
glEnable(GL_DEPTH_TEST)

vertex = glGenVertexArrays(1) # pylint: disable=W0612
glBindVertexArray(vertex)

shader = Shader()
shader.initShaderFromGLSL(["glsl/tu02/vertex.glsl"],["glsl/tu02/fragment.glsl"])


# Init uniform variable MVP.
UNIFORM_LOC_MVP = glGetUniformLocation(shader.program, "MVP")

Projection = glm.perspective(glm.radians(45.0), 800.0 / 400.0, 0.1, 100.0)
View = glm.lookAt(
    glm.vec3(4,  3, -3), # Camera is at (4,3,-3), in World Space
    glm.vec3(0,  0,  0), # and looks at the (0.0.0))
    glm.vec3(0,  1,  0)
) # Head is up (set to 0,-1,0 to look upside-down)

Model = glm.mat4(1.0)
MVP = Projection * View * Model


# Init uniform variable Texture.
from utils.textureLoader import textureLoader
UNIFORM_LOC_TEXTURE = glGetUniformLocation(shader.program, "myTextureSampler")
texture = textureLoader("resources/tu02/uvtemplate.tga")
#texture = textureLoader("resources/tu02/uvtemplate.dds")

# Setup data of vertex buffer.
vertexbuffer  = glGenBuffers(1)
glBindBuffer(GL_ARRAY_BUFFER, vertexbuffer)
glBufferData(GL_ARRAY_BUFFER, len(g_vertex_buffer_data) * 4,(GLfloat * len(g_vertex_buffer_data))(*g_vertex_buffer_data), GL_STATIC_DRAW)

# colorbuffer  = glGenBuffers(1)
# glBindBuffer(GL_ARRAY_BUFFER, colorbuffer)
# glBufferData(GL_ARRAY_BUFFER, len(g_color_buffer_data) * 4,(GLfloat * len(g_color_buffer_data))(*g_color_buffer_data), GL_STATIC_DRAW)

# Setup data of UV buffer.
if (texture.inversedVCoords):
    for index in range(0, len(g_uv_buffer_data)):
        if(index % 2):
            g_uv_buffer_data[index] = 1.0 - g_uv_buffer_data[index]

uvbuffer  = glGenBuffers(1)
glBindBuffer(GL_ARRAY_BUFFER, uvbuffer)
glBufferData(GL_ARRAY_BUFFER, len(g_uv_buffer_data) * 4, (GLfloat * len(g_uv_buffer_data))(*g_uv_buffer_data), GL_STATIC_DRAW)

while (not glfw.window_should_close(window)):
    # print(self.context.MVP)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    # shader.begin()
    glUseProgram(shader.program)
    glUniformMatrix4fv(UNIFORM_LOC_MVP, 1, GL_FALSE, glm.value_ptr(MVP))
    
    glActiveTexture(GL_TEXTURE0)
    glBindTexture(GL_TEXTURE_2D, texture.textureGLID)
    glUniform1i(UNIFORM_LOC_TEXTURE, 0) # 0 means GL_TEXTURE0

    glEnableVertexAttribArray(0) # 0 is the location of layout in GLSL.
    glBindBuffer(GL_ARRAY_BUFFER, vertexbuffer)
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None) # None means ctypes.c_voidp(0)

    glEnableVertexAttribArray(1) # 1 is the location of layout in GLSL.
    glBindBuffer(GL_ARRAY_BUFFER, uvbuffer)
    glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 0, ctypes.c_voidp(0))

    glDrawArrays(GL_TRIANGLES, 0, 12 * 3) # 12*3 indices starting at 0 -> 12 triangles

    glDisableVertexAttribArray(0)
    glDisableVertexAttribArray(1)
    # shader.end()
    glfw.swap_buffers(window)

    glfw.poll_events()
