
import glfw
from OpenGL.GL import *  # pylint: disable=W0614
from OpenGL.GLU import *  # pylint: disable=W0614
import math

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
     1.0,-1.0, 1.0
]
g_color_buffer_data = [ 
    0.583,  0.771,  0.014,
    0.609,  0.115,  0.436,
    0.327,  0.483,  0.844,
    0.822,  0.569,  0.201,
    0.435,  0.602,  0.223,
    0.310,  0.747,  0.185,
    0.597,  0.770,  0.761,
    0.559,  0.436,  0.730,
    0.359,  0.583,  0.152,
    0.483,  0.596,  0.789,
    0.559,  0.861,  0.639,
    0.195,  0.548,  0.859,
    0.014,  0.184,  0.576,
    0.771,  0.328,  0.970,
    0.406,  0.615,  0.116,
    0.676,  0.977,  0.133,
    0.971,  0.572,  0.833,
    0.140,  0.616,  0.489,
    0.997,  0.513,  0.064,
    0.945,  0.719,  0.592,
    0.543,  0.021,  0.978,
    0.279,  0.317,  0.505,
    0.167,  0.620,  0.077,
    0.347,  0.857,  0.137,
    0.055,  0.953,  0.042,
    0.714,  0.505,  0.345,
    0.783,  0.290,  0.734,
    0.722,  0.645,  0.174,
    0.302,  0.455,  0.848,
    0.225,  0.587,  0.040,
    0.517,  0.713,  0.338,
    0.053,  0.959,  0.120,
    0.393,  0.621,  0.362,
    0.673,  0.211,  0.457,
    0.820,  0.883,  0.371,
    0.982,  0.099,  0.879
]

class glfwWindow:
    def __init__(self):
        glfw.init()
        glfw.window_hint(glfw.SAMPLES, 4)
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

        self.window_size_x = 960
        self.window_size_y = 540
        self.window = glfw.create_window(self.window_size_x, self.window_size_y, "title of the window", None, None)

        self.camera_pos = glm.vec3(0,  0, -10)
        self.camera_radius_x = 0
        self.camera_radius_y = 0
        self.camera_scale = 100

        self.mouse_Lp = False
        self.mouse_Lr = False
        self.mouse_Lx = 0
        self.mouse_Ly = 0
        self.mouse_Rp = False
        self.mouse_Rr = False
        self.mouse_Rx = 0
        self.mouse_Ry = 0

        def callback_mouse_pos(window, mouse_x, mouse_y):
            self.callback_mouse_pos(window, mouse_x, mouse_y)
        glfw.set_cursor_pos_callback(self.window, callback_mouse_pos)
        
        def callback_mouse_button(window, button, action, mods):
            self.callback_mouse_button(window, button, action, mods)
        glfw.set_mouse_button_callback(self.window, callback_mouse_button)
        
        def callback_mouse_scroll(window, offset_x, offset_y):
            self.callback_mouse_scroll(window, offset_x, offset_y)
        glfw.set_scroll_callback(self.window, callback_mouse_scroll)

        glfw.make_context_current(self.window)

        self.shader = Shader()
        self.shader.initShaderFromGLSL(["glsl/tnx0/vert.glsl"], ["glsl/tnx0/frag.glsl"])
        self.loc_window_size_x = glGetUniformLocation(self.shader.program, "screenX")
        self.loc_window_size_y = glGetUniformLocation(self.shader.program, "screenY")
        self.loc_camera_scale = glGetUniformLocation(self.shader.program, "scale")
        self.loc_rotation = glGetUniformLocation(self.shader.program, "rotation")
        self.loc_position = glGetUniformLocation(self.shader.program, "position_offset")

    def find_curr_rotation(self):
        quaternion_x = glm.angleAxis(self.camera_radius_x, glm.vec3(0, 1, 0))
        quaternion_y = glm.angleAxis(self.camera_radius_y, quaternion_x * glm.vec3(1, 0, 0))
        return quaternion_y * quaternion_x

    def callback_mouse_pos(self, window, mouse_x, mouse_y):
        # if window != self.window:
        #     return
        if self.mouse_Lp:
            if self.mouse_Lr:
                delta_x = mouse_x - self.mouse_Lx
                delta_y = mouse_y - self.mouse_Ly

                delta = glm.vec3(delta_x, -delta_y, 0) / self.camera_scale
                self.camera_pos = self.camera_pos + self.find_curr_rotation() * delta
            self.mouse_Lx = mouse_x
            self.mouse_Ly = mouse_y
            self.mouse_Lr = True
        else:
            self.mouse_Lr = False
            
        if self.mouse_Rp:
            if self.mouse_Rr:
                delta_x = mouse_x - self.mouse_Rx
                delta_y = mouse_y - self.mouse_Ry

                self.camera_radius_x = self.camera_radius_x + (delta_x / 180 * 0.5) # 100 pixel for 0.5 degree rotation.
                self.camera_radius_y = self.camera_radius_y + (delta_y / 180 * 0.5)
                # wrap x
                if self.camera_radius_x > math.pi:
                    self.camera_radius_x = self.camera_radius_x - math.pi - math.pi
                if self.camera_radius_x < -math.pi:
                    self.camera_radius_x = self.camera_radius_x + math.pi + math.pi
                # clamp y
                if self.camera_radius_y > math.pi / 2:
                    self.camera_radius_y = math.pi / 2
                if self.camera_radius_y < -math.pi / 2:
                    self.camera_radius_y = -math.pi / 2
            self.mouse_Rx = mouse_x
            self.mouse_Ry = mouse_y
            self.mouse_Rr = True
        else:
            self.mouse_Rr = False
        # print("({0},({1},{2}))".format(self.camera_pos, self.camera_radius_x, self.camera_radius_y))

    def callback_mouse_button(self, window, button, action, mods):
        # if window != self.window:
        #     print("{} != {}".format(window, self.window))
        #     return
        if (button == glfw.MOUSE_BUTTON_LEFT) and (action == glfw.RELEASE):
            self.mouse_Lp = False
        if (button == glfw.MOUSE_BUTTON_RIGHT) and (action == glfw.RELEASE):
            self.mouse_Rp = False
        if (button == glfw.MOUSE_BUTTON_LEFT) and (action == glfw.PRESS):
            self.mouse_Lp = True
        if (button == glfw.MOUSE_BUTTON_RIGHT) and (action == glfw.PRESS):
            self.mouse_Rp = True

    def callback_mouse_scroll(self, window, offset_x, offset_y):
        # if window != self.window:
        #     print("{} != {}".format(window, self.window))
        #     return
        self.camera_scale = self.camera_scale * math.pow(1.05, offset_y)
            
    def run(self):
        glClearColor(0.0, 0.0, 0.4, 0.0)
        glDepthFunc(GL_LESS)
        glEnable(GL_DEPTH_TEST)

        vertex = glGenVertexArrays(1) # pylint: disable=W0612
        glBindVertexArray(vertex)

        vertexbuffer  = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER,vertexbuffer)
        glBufferData(GL_ARRAY_BUFFER,len(g_vertex_buffer_data) * 4,(GLfloat * len(g_vertex_buffer_data))(*g_vertex_buffer_data), GL_STATIC_DRAW)

        colorbuffer  = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER,colorbuffer)
        glBufferData(GL_ARRAY_BUFFER,len(g_color_buffer_data) * 4,(GLfloat * len(g_color_buffer_data))(*g_color_buffer_data), GL_STATIC_DRAW)

        while (not glfw.window_should_close(self.window)):
            glfw.poll_events()

            # print(self.context.MVP)
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

            # shader.begin()
            glUseProgram(self.shader.program)
            glUniform1f(self.loc_camera_scale, self.camera_scale)
            glUniform1f(self.loc_window_size_x, self.window_size_x)
            glUniform1f(self.loc_window_size_y, self.window_size_y)
            rotation = glm.mat3_cast(glm.conjugate(self.find_curr_rotation()))
            glUniformMatrix3fv(self.loc_rotation, 1, GL_FALSE, glm.value_ptr(rotation))
            glUniform3fv(self.loc_position, 1, glm.value_ptr(self.camera_pos))
            # glUniformMatrix4fv(self.MVP_ID, 1, GL_FALSE, glm.value_ptr(MVP))

            glEnableVertexAttribArray(0)
            glBindBuffer(GL_ARRAY_BUFFER, vertexbuffer)

            glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None) # None means ctypes.c_voidp(0)

            glEnableVertexAttribArray(1)
            glBindBuffer(GL_ARRAY_BUFFER, colorbuffer)
            glVertexAttribPointer(1, 3, GL_FLOAT,GL_FALSE, 0, ctypes.c_voidp(0))

            glDrawArrays(GL_TRIANGLES, 0, 12 * 3) # 12*3 indices starting at 0 -> 12 triangles

            glDisableVertexAttribArray(0)
            glDisableVertexAttribArray(1)
            # shader.end()
            glfw.swap_buffers(self.window)

glfwWindow().run()