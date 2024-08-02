
import glfw
from OpenGL.GL import *  # pylint: disable=W0614
from OpenGL.GLU import *  # pylint: disable=W0614
import math

import glm
from utils.shaderLoader import Shader

import torch
import smplx
import numpy
import cv2
import ffmpeg
def get_smplx_model(path_smplx_model, device):
    smplx_model_params = dict(
        model_path=path_smplx_model,
        model_type='smplx',
        create_global_orient=True,
        create_body_pose=True,
        create_betas=True,
        num_betas=300,
        create_left_hand_pose=True,
        create_right_hand_pose=True,
        use_pca=False,
        flat_hand_mean=False,
        create_expression=True,
        num_expression_coeffs=100,
        num_pca_comps=12,
        create_jaw_pose=True,
        create_leye_pose=True,
        create_reye_pose=True,
        create_transl=False,
        # gender='ne',
        dtype=torch.float64,
    )
    return smplx.create(**smplx_model_params).to(device)

def get_smplx_data(npz, smplx_model, frame, device):
    # Convert data to tensor.
    betas = torch.tensor(npz["betas"]).to(device)
    poses = torch.tensor(npz["poses"][frame]).to(device)
    expressions = torch.tensor(npz["expressions"][frame]).to(device)

    # https://files.is.tue.mpg.de/black/talks/SMPL-made-simple-FAQs.pdf
    verts = smplx_model(
        betas=betas.unsqueeze(0),
        expression=expressions.unsqueeze(0),
        global_orient=poses[:3].unsqueeze(0),
        body_pose=poses[3:66].unsqueeze(0),
        jaw_pose=poses[66:69].unsqueeze(0),
        leye_pose=poses[69:72].unsqueeze(0),
        reye_pose=poses[72:75].unsqueeze(0),
        left_hand_pose=poses[75:120].unsqueeze(0),
        right_hand_pose=poses[120:165].unsqueeze(0),
        return_verts=True
    ).vertices.detach()
    verts = verts[0]
    verts[:, 1] = -verts[:, 1]
    # verts[:, 2] = -verts[:, 2]

    # return verts, smplx_model.faces

    verts_0 = verts[smplx_model.faces[:,0],:]
    verts_1 = verts[smplx_model.faces[:,1],:]
    verts_2 = verts[smplx_model.faces[:,2],:]
    norms = torch.linalg.cross(verts_0 - verts_1, verts_0 - verts_2)
    norms = torch.stack((norms, norms, norms), dim=1)
    verts = torch.stack((verts_0, verts_1, verts_2), dim=1)
    return verts.detach(), norms.detach()

class glfwWindow:
    def __init__(self):
        glfw.init()
        glfw.window_hint(glfw.SAMPLES, 4)
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

        self.window_size_x = 640
        self.window_size_y = 1080
        self.window = glfw.create_window(self.window_size_x, self.window_size_y, "title of the window", None, None)

        self.camera_pos = glm.vec3(0, -0.25, 0)
        self.camera_radius_x = 0
        self.camera_radius_y = 0
        self.camera_scale = 480

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
        self.shader.initShaderFromGLSL(["glsl/tnx3/vert.glsl"], ["glsl/tnx3/frag.glsl"])
        self.loc_window_size_x = glGetUniformLocation(self.shader.program, "screenX")
        self.loc_window_size_y = glGetUniformLocation(self.shader.program, "screenY")
        self.loc_camera_scale = glGetUniformLocation(self.shader.program, "scale")
        self.loc_rotation = glGetUniformLocation(self.shader.program, "rotation")
        self.loc_position = glGetUniformLocation(self.shader.program, "position_offset")
        
        self.loc_color_ambient = glGetUniformLocation(self.shader.program, "color_ambient")
        self.loc_light_1_position = glGetUniformLocation(self.shader.program, "light_1_position")
        self.loc_light_1_color = glGetUniformLocation(self.shader.program, "light_1_color")
        self.loc_light_2_position = glGetUniformLocation(self.shader.program, "light_2_position")
        self.loc_light_2_color = glGetUniformLocation(self.shader.program, "light_2_color")

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
            
    def run(self, path_smplx_model, path_npz, path_output):
        device = 'cuda'
        smplx_model = get_smplx_model(path_smplx_model, device)
        npz = numpy.load(path_npz)

        frame_index = 0
        frame_count = npz["poses"].shape[0]

        glClearColor(0.0, 0.0, 0.0, 0.0)
        glDepthFunc(GL_LESS)
        glEnable(GL_DEPTH_TEST)

        vao = glGenVertexArrays(1) # pylint: disable=W0612
        glBindVertexArray(vao)

        vbo_vertex = glGenBuffers(1)
        vbo_normal = glGenBuffers(1)

        # # Construct opengl FBO
        # fbo = glGenFramebuffers(1)
        # fbo_color, _ = glGenTextures(2)
        # fbo_depth = glGenRenderbuffers(1)

        # glBindFramebuffer(GL_FRAMEBUFFER, fbo)
        # glBindTexture(GL_TEXTURE_2D, fbo_color)
        # glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, self.window_size_x, self.window_size_y, 0, GL_RGBA, GL_UNSIGNED_BYTE, None)

        # glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        # glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        # glFramebufferTexture2D(GL_DRAW_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, fbo_color, 0)

        # glBindRenderbuffer(GL_RENDERBUFFER, fbo_depth)
        # glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH_COMPONENT24, self.window_size_x, self.window_size_y)
        # glFramebufferRenderbuffer(GL_DRAW_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_RENDERBUFFER, fbo_depth)

        # Create video writer.
        writer = None
        image = numpy.zeros((self.window_size_y, self.window_size_x, 4), numpy.uint8)
        if int(cv2.__version__[0]) < 3:
            # print('cv2 < 3')
            writer = cv2.VideoWriter(path_output, cv2.cv.CV_FOURCC(*'mp4v'), float(npz["mocap_frame_rate"]), (self.window_size_x, self.window_size_y), True)
        else:
            # print('cv2 >= 3')
            writer = cv2.VideoWriter(path_output, cv2.VideoWriter_fourcc(*'mp4v'), float(npz["mocap_frame_rate"]), (self.window_size_x, self.window_size_y), True)

        while frame_index < frame_count:
            glfw.poll_events()

            # print(self.context.MVP)
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

            self.shader.begin()
            glUseProgram(self.shader.program)
            glUniform1f(self.loc_camera_scale, self.camera_scale)
            glUniform1f(self.loc_window_size_x, self.window_size_x)
            glUniform1f(self.loc_window_size_y, self.window_size_y)
            rotation = glm.mat3_cast(glm.conjugate(self.find_curr_rotation()))
            glUniformMatrix3fv(self.loc_rotation, 1, GL_FALSE, glm.value_ptr(rotation))
            glUniform3fv(self.loc_position, 1, glm.value_ptr(self.camera_pos))
            # glUniformMatrix4fv(self.MVP_ID, 1, GL_FALSE, glm.value_ptr(MVP))

            glUniform3f(self.loc_color_ambient, 0.1, 0.1, 0.1)
            glUniform3f(self.loc_light_1_position, 1.0, 1.0, 1.0) # Left, Up, Front
            glUniform3f(self.loc_light_1_color, 0.8, 0.4, 0.0)
            glUniform3f(self.loc_light_2_position, -1.0, 1.0, 1.0) # Left, Up, Front
            glUniform3f(self.loc_light_2_color, 0.0, 0.4, 0.8)

            verts, norms = get_smplx_data(npz, smplx_model, frame_index, device)
            data_vertex = verts.flatten().detach().cpu().numpy().astype(GLfloat)
            data_normal = norms.flatten().detach().cpu().numpy().astype(GLfloat)
            del norms
            del verts

            glEnableVertexAttribArray(0)
            glBindBuffer(GL_ARRAY_BUFFER, vbo_vertex)
            glBufferData(GL_ARRAY_BUFFER, data_vertex, GL_DYNAMIC_DRAW)
            glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None) # None means ctypes.c_voidp(0)

            glEnableVertexAttribArray(1)
            glBindBuffer(GL_ARRAY_BUFFER, vbo_normal)
            glBufferData(GL_ARRAY_BUFFER, data_normal, GL_DYNAMIC_DRAW)
            glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 0, None) # None means ctypes.c_voidp(0)

            # glBindTexture(GL_TEXTURE_2D, 0)
            # glEnable(GL_TEXTURE_2D)
            # glBindFramebuffer(GL_FRAMEBUFFER, fbo)

            glDrawArrays(GL_TRIANGLES, 0, len(data_vertex) // 3)

            # glBindFramebuffer(GL_FRAMEBUFFER, 0)

            glDisableVertexAttribArray(0)
            glDisableVertexAttribArray(1)
            self.shader.end()
            glfw.swap_buffers(self.window)

            frame_index = frame_index + 1
            print("{0:6d}/{1:6d}".format(frame_index, frame_count))

            glReadPixels(0, 0, self.window_size_x, self.window_size_y, GL_RGBA, GL_UNSIGNED_BYTE, image)
            writer.write(cv2.flip(image[:,:,:-1], 0))
        writer.release()

if __name__ == "__main__":
    glfwWindow().run(R"C:\liuchengming\桌面\testGL\visualise", R"C:\liuchengming\桌面\testGL\testdata\npz\00.npz", R"C:\liuchengming\桌面\testGL\testdata\mp4\00.mp4")