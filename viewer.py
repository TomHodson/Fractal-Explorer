from __future__ import division
import ctypes as c

import pyglet
import pyglet.clock
import pyglet.window
from pyglet.window import key
from pyglet import gl
import numpy as np
import time

from shader import Shader

vertex_shader = """
uniform vec2 z;
uniform vec2 res;

void main(void)
{
  gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;
}
"""

fragment_shader = """
uniform vec2 res;
uniform vec2 z;
uniform vec2 view;


//map screen space to world space
vec2 screen_map(vec2 uv, vec2 center, vec2 zoom) {
    return ((uv - vec2(0.5,0.5)) * zoom) - center;
}

//raise a complex number to an arbitrary power then add a constant
vec2 power_add(vec2 z, float power, vec2 c) {
    float r = length(z);
    float t = atan(z.y, z.x);
    return vec2(pow(r,power)*cos(power*t) + c.x, pow(r,power)*sin(power*t) + c.y);
}

//square a complex number just using components then add a constant
vec2 square_add(vec2 z, vec2 c) {
    return vec2((z.x*z.x - z.y*z.y) + c.x, (2.0 * z.y * z.x) + c.y);
}

//calculate if the given point is in the mandelbrot set
float mandelbrot(vec2 c) {
    
    const float power = 2.0;
    const float limit = 2.0;// choose a limit of 2 becuase the point is guranteed to diverge once |z| > 2
    vec2 z = c;
    float escape = 0.0;
    
    for(int i = 0; i < 600; i++)    {
        
        z = square_add(z, c);    
        //z = power_add(z, power, c);
        
        if(length(z) > limit) {
            //add a fractional part to the escape time to make the colours smoother
            //based on the observation that the recursion formula is asymptopically just squaring
            escape =  float(i) - log(log(length(z))/ log(limit)) / log(power) ;//float(i);
            break;
        }
    }  
    return escape;
}


void main( void )
{
    //uv is a 2d vector represnting which pixel you're currently computing
    vec2 uv = gl_FragCoord.xy / res;
    
    vec2 z = screen_map(uv, z, view);
    
    //float escape = average_mandelbrot(z, zoom);
    float escape = mandelbrot(z);
    
    float Pi = 3.14159;
    float x = escape / 50.0;
    vec4 orange = vec4(0.8, 0.2,0.1, 1.0);
    vec4 black = vec4(0.0, 0.0,0.0, 1.0);
    
    gl_FragColor = mix(black, orange, x);
  
}
"""

fragment_shader_simple = """
uniform vec2 res;
uniform vec2 z;
uniform vec2 view;

//map screen space to world space
vec2 screen_map(vec2 uv, vec2 center, vec2 zoom) {
    return ((uv - vec2(0.5,0.5)) * zoom) - center;
}

void main(void) {
    vec2 uv = gl_FragCoord.xy / res;
    vec2 pos = screen_map(uv, z, view);

    gl_FragColor.xyz = vec3(1.0,1.0,0.0) * length(pos);
    gl_FragColor.w = 1.0;
}
"""


clib = c.CDLL("./mandelbrot_render.so")

class vec2(c.Structure):
        _fields_ = [("x", c.c_double),
                    ("y", c.c_double)]
        def __init__(self, array):
            self.x = c.c_double(array[0])
            self.y = c.c_double(array[1])
        
class colour(c.Structure):
        _fields_ = [("r", c.c_byte),
                    ("g", c.c_byte),
                    ("b",c.c_byte)]


class MainWindow(pyglet.window.Window):
    def __init__(self, **kwargs):
        config = pyglet.gl.Config(sample_buffers=1, samples=4)

        pyglet.window.Window.__init__(self, width=1000, height=700,
            resizable=True, config=self.config, **kwargs)

        self.fps = pyglet.clock.ClockDisplay()
        self.shader = Shader(vertex_shader, fragment_shader)
        self.center = np.array([0.0,0.0])
        self.show_fps = False

        self.screen_size = np.array([self.width, self.height])
        self.view_size = np.array([3.0, 2.0])
        self.col_scale = 4000.0

        self.draw()

    def on_key_press(self, symbol, modifiers):
        if symbol == key.ESCAPE:
            self.has_exit = True
        elif symbol == key.F:
            self.set_fullscreen(not self.fullscreen)
            self.screen_size = np.array([self.width, self.height])
        elif symbol == key.F1:
            self.show_fps = not self.show_fps
        elif symbol == key.F2:
            pyglet.image.get_buffer_manager().get_color_buffer().save('screenshot.png')
        elif symbol == key.C:
            self.renderC()
            return
        elif symbol == key.DOWN:
            self.col_scale *= 0.9
            print self.col_scale
            self.renderC() 
            return
        elif symbol == key.UP:
            self.col_scale *= 1.1
            print self.col_scale
            self.renderC() 
            return

        self.draw()

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        delta = np.array((dx,dy))
        self.center += delta * self.view_size / self.screen_size
        self.draw()

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        scale = 1.1 ** scroll_y
        screen_center = np.array([self.width/2.0, self.height/2.0])
        self.center += (scale - 1.0) * (np.array([x,y]) - screen_center) * (self.view_size / self.screen_size)
        self.view_size *= scale
        self.draw()

    def on_resize(self, width, height):
        pyglet.window.Window.on_resize(self, width, height)
        self.draw()

    def draw(self):
            if self.view_size[0] < 1e-4 or self.view_size[1] < 1e-4 :
                self.renderC()
                return

            gl.glClear(gl.GL_COLOR_BUFFER_BIT)
            gl.glLoadIdentity()
            self.shader.bind()
            self.shader.uniformf("z", self.center)
            self.shader.uniformf("res", self.screen_size)
            self.shader.uniformf("view", self.view_size)

            #draw square across screen
            gl.glBegin(gl.GL_QUADS)
            gl.glVertex3f(0.0, 0.0, 0.0)
            gl.glVertex3f(0.0, self.height, 0.0)
            gl.glVertex3f(self.width, self.height, 0.0)
            gl.glVertex3f(self.width, 0.0, 0.0)
            gl.glEnd()

            self.shader.unbind()
            if self.show_fps:
                self.fps.draw()
            self.flip()

    def run(self):
        while not self.has_exit:
            pyglet.clock.tick()
            self.dispatch_events()

    def renderC(self):
        w, h, = self.width,self.height
        t = time.time()
        imagetype = c.c_byte * (w * h * 3)
        imagedata = imagetype()
        clib.mandelbrot(c.c_int(w), c.c_int(h),c.c_double(self.col_scale), vec2(self.center), vec2(self.view_size), imagedata)
        image = pyglet.image.ImageData(w, h, "RGB", imagedata, pitch = 3 * c.sizeof(c.c_char) * w)
        image.blit(0,0)
        self.flip()
        return image

def main():
    from subprocess import call
    call("make".split())
    #MainWindow(visible = False).renderC()

    #call("gcc-4.9 --std=gnu99 -lm -shared -o mandelbrot_render.so mandelbrot_render.c".split())
    #MainWindow(visible = False).renderC()

    MainWindow().run()

if __name__ == "__main__":
    main()