#version 150

in vec3 vertex_vert;
in vec3 normal_vert;

out float depth_frag;
out vec3 normal_frag;
out vec3 vertex_frag;

uniform float screenX;
uniform float screenY;
uniform float scale;

uniform mat3 rotation;
uniform vec3 position_offset;

void main()
{
    vec3 p = rotation * (vertex_vert + position_offset);
    p = p * 2 * scale;
    gl_Position = vec4(p.x / screenX, p.y / screenY, 0.0, 1.0);

    if (p.z >= 0)
        depth_frag = (p.z + 1) / (p.z + 2);
    else
        depth_frag = 1 / (2 - p.z);

    normal_frag = normal_vert;
    vertex_frag = vertex_vert;
}