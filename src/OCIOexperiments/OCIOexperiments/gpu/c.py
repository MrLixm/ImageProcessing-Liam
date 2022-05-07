"""
[Licenses]

Copyright Contributors to the OpenColorIO Project.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are
met:

* Redistributions of source code must retain the above copyright
  notice, this list of conditions and the following disclaimer.
* Redistributions in binary form must reproduce the above copyright
  notice, this list of conditions and the following disclaimer in the
  documentation and/or other materials provided with the distribution.
* Neither the name of the copyright holder nor the names of its
  contributors may be used to endorse or promote products derived from
  this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

import PyOpenColorIO as ocio

from OCIOexperiments import c

ABR = c.ABR + ".gpu"

GLSL_VERT_SRC = """#version 400 core

uniform mat4 mvpMat;
in vec3 in_position;
in vec2 in_texCoord;

out vec2 vert_texCoord;

void main() {
    vert_texCoord = in_texCoord;
    gl_Position = mvpMat * vec4(in_position, 1.0);
}

"""
"""
Simple vertex shader which transforms all vertices with a 
model-view-projection matrix uniform.
"""

GLSL_FRAG_SRC = """#version 400 core

uniform sampler2D imageTex;
in vec2 vert_texCoord;

out vec4 frag_color;

void main() {{
    frag_color = texture(imageTex, vert_texCoord);
}}
"""
"""
Simple fragment shader which performs a 2D texture lookup to map an 
image texture onto UVs. This is used when OCIO is unavailable, like 
before its shader initialization.
"""

GLSL_FRAG_OCIO_SRC_FMT = """#version 400 core

uniform sampler2D imageTex;
in vec2 vert_texCoord;

out vec4 frag_color;

{ocio_src}

void main() {{
    vec4 inColor = texture(imageTex, vert_texCoord);
    vec4 outColor = OCIOMain(inColor);
    frag_color = outColor;
}}
"""
"""
Fragment shader which performs a 2D texture lookup to map an image 
texture onto UVs and processes fragments through an OCIO-provided 
shader program segment, which itself utilizes additional texture 
lookups, dynamic property uniforms, and various native GLSL op 
implementations. Note that this shader's cost will increase with 
additional LUTs in an OCIO processor, since each adds its own 
2D or 3D texture.

Call of  <.format(ocio_src="")> required.
"""
