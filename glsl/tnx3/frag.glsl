#version 150

in float depth_frag;
in vec3 normal_frag;
in vec3 vertex_frag;

out vec4 color_out;

uniform vec3 color_ambient;
uniform vec3 light_1_position;
uniform vec3 light_1_color;
uniform vec3 light_2_position;
uniform vec3 light_2_color;

float light_percent(vec3 v1, vec3 v2) {
    float val = dot(v1, v2) / sqrt(dot(v1, v1) * dot(v2, v2));
    if (val < 0) return 0;
    return val;
}

void main()
{
    vec3 color
        = color_ambient
        + light_percent(normal_frag, light_1_position - vertex_frag) * light_1_color
        + light_percent(normal_frag, light_2_position - vertex_frag) * light_2_color
    ;
    color_out = vec4(color, 1.0);
    gl_FragDepth = depth_frag;
}