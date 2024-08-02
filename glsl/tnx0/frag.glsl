#version 150
in vec3 color_frag;
out vec4 color_out;
in float depth_frag;
void main()
{
    color_out = vec4(color_frag, 1.0);
    gl_FragDepth = depth_frag;
}