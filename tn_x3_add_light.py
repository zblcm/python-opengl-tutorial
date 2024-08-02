
import glfw
from OpenGL.GL import *  # pylint: disable=W0614
from OpenGL.GLU import *  # pylint: disable=W0614
import math

import glm
from utils.shaderLoader import Shader

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
        self.camera_scale = 400

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
            
    def run(self, verts, norms):
        norms = norms.reshape(norms.shape[0], norms.shape[1] * norms.shape[2] * norms.shape[3])
        verts = verts.reshape(verts.shape[0], verts.shape[1] * verts.shape[2] * verts.shape[3])
        frame_index = 0
        frame_count = verts.shape[0]

        glClearColor(0.0, 0.0, 0.0, 0.0)
        glDepthFunc(GL_LESS)
        glEnable(GL_DEPTH_TEST)

        vao = glGenVertexArrays(1) # pylint: disable=W0612
        glBindVertexArray(vao)

        vbo_vertex = glGenBuffers(1)
        vbo_normal = glGenBuffers(1)

        while (not glfw.window_should_close(self.window)):
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

            data_vertex = verts[frame_index].detach().cpu().numpy().astype(GLfloat)
            data_normal = norms[frame_index].detach().cpu().numpy().astype(GLfloat)

            glEnableVertexAttribArray(0)
            glBindBuffer(GL_ARRAY_BUFFER, vbo_vertex)
            glBufferData(GL_ARRAY_BUFFER, data_vertex, GL_DYNAMIC_DRAW)
            glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None) # None means ctypes.c_voidp(0)

            glEnableVertexAttribArray(1)
            glBindBuffer(GL_ARRAY_BUFFER, vbo_normal)
            glBufferData(GL_ARRAY_BUFFER, data_normal, GL_DYNAMIC_DRAW)
            glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 0, None) # None means ctypes.c_voidp(0)

            glDrawArrays(GL_TRIANGLES, 0, len(data_vertex) // 3)

            glDisableVertexAttribArray(0)
            glDisableVertexAttribArray(1)
            self.shader.end()
            glfw.swap_buffers(self.window)

            frame_index = (frame_index + 1) % frame_count

            # del data_vertex
            # del data_normal

import torch
import smplx
import numpy
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

def get_smplx_data(path_npz, smplx_model, device):
    npz = numpy.load(path_npz)

    # Convert data to tensor.
    betas = torch.tensor(npz["betas"]).to(device)
    poses = torch.tensor(npz["poses"]).to(device)
    expressions = torch.tensor(npz["expressions"]).to(device)
    fps = float(npz["mocap_frame_rate"])

    # Get frame count.
    frame_count = poses.shape[0]
    assert poses.shape[0] == frame_count
    assert expressions.shape[0] == frame_count

    # https://files.is.tue.mpg.de/black/talks/SMPL-made-simple-FAQs.pdf
    verts = smplx_model(
        betas=betas.unsqueeze(0).expand(frame_count, betas.shape[0]),
        expression=expressions,
        global_orient=poses[:,:3],
        body_pose=poses[:,3:66],
        jaw_pose=poses[:,66:69],
        leye_pose=poses[:,69:72],
        reye_pose=poses[:,72:75],
        left_hand_pose=poses[:,75:120],
        right_hand_pose=poses[:,120:165],
        return_verts=True
    ).vertices.detach()
    verts[:, :, 1] = -verts[:, :, 1]
    # verts[:, :, 2] = -verts[:, :, 2]

    # return verts, smplx_model.faces

    verts_0 = verts[:,smplx_model.faces[:,0],:]
    verts_1 = verts[:,smplx_model.faces[:,1],:]
    verts_2 = verts[:,smplx_model.faces[:,2],:]
    norms = torch.linalg.cross(verts_0 - verts_1, verts_0 - verts_2)
    norms = torch.stack((norms, norms, norms), dim=2)
    verts = torch.stack((verts_0, verts_1, verts_2), dim=2)
    return verts.detach(), norms.detach()

if __name__ == "__main__":
    device = 'cuda'
    smplx_model = get_smplx_model(R"C:\liuchengming\桌面\testGL\visualise", device)

    verts, norms = get_smplx_data(R"C:\liuchengming\桌面\testGL\testdata\npz\00.npz", smplx_model, device)
    glfwWindow().run(verts, norms)

    pass