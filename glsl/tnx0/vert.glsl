#version 150
in vec3 position;
in vec3 color_vert;
out vec3 color_frag;
out float depth_frag;

uniform float screenX;
uniform float screenY;
uniform float scale;

uniform mat3 rotation;
uniform vec3 position_offset;

void main()
{
    vec3 p = rotation * (position + position_offset);
    // vec3 p = position;
    p = p * 2 * scale;
    gl_Position = vec4(p.x / screenX, p.y / screenY, 0.0, 1.0);

    if (p.z >= 0)
        depth_frag = (p.z + 1) / (p.z + 2);
    else
        depth_frag = 1 / (2 - p.z);

    color_frag = color_vert;
}