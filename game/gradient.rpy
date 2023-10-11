init python:
    renpy.register_shader(
        "vgradient",
        variables="""
        uniform vec4 u_top_color;
        uniform vec4 u_bottom_color;
        uniform vec2 u_model_size;
        attribute vec4 a_position;
        varying float v_gradient_done;
    """, vertex_300="""
        v_gradient_done = a_position.y / u_model_size.y;
    """, fragment_300="""
        gl_FragColor = mix(u_top_color, u_bottom_color, v_gradient_done);
    """)

transform vgradient(top_color, bottom_color):
    "black"
    shader "vgradient"
    u_top_color Color(top_color).rgba
    u_bottom_color Color(bottom_color).rgba
