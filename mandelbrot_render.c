//mandelbrot.c - generates a ppm file of the mandelbrot set with shading
//Still to add: include a jpeg library, add user defined dimensions, add user defined file name
#include "stdio.h"
#include "complex.h"
#include "math.h"

double mandelbrot_test(double complex c);

struct colour //the data structure the rgb values will be returned as
{
        char r;
        char g;
        char b;
};

struct vec2 {
    double x;
    double y;
    };
 
double clamp(double min, double max, double in) {
    if(in > max) return max;
    if(in < min) return min;
    return in;
}

struct colour mix(struct colour a, struct colour b, double x) {
    struct colour out = {a.r * x + b.r * (1.0 - x), a.g * x + b.g * (1.0 - x), a.b * x + b.b * (1.0 - x)};
    return out;
}

void mandelbrot(int width, int height, struct vec2 center, struct vec2 viewport, struct colour image[])
{
    for(int j = 0; j < height; j++) {
        for (int i = 0; i < width; i++)
        {
            double complex z = ((((double) i / (double) width) - 0.5) * viewport.x - center.x);
            z += I*((((double) j / (double) height) - 0.5) * viewport.y - center.y);
            double output = mandelbrot_test(z);
            struct colour col;
            col.r = col.g = col.b = (char) (output * 100.0);
            struct colour orange = {0.8*255.0, 0.2*255.0,0.1*255.0};
            struct colour black = {0,0,0};

            image[width*j + i] = mix(orange, black, atan(output));
        }
    }
}
 
double mandelbrot_test(double complex c)
{
        double complex x = 0;
        int i;
        const int limit = 300;

        //check if the point is in the main cardioid
        double r_squared = cimag(c) * cimag(c) + creal(c) * creal(c);
        if(r_squared *(8.0*r_squared - 3.0) < 3.0/32.0 - creal(c)) {
            //this point will definitely not diverge so bailout early
            return 0.0;
        }
       
        for (i = 1; i < limit; i++)
        {
                x = x*x + c;
                
                r_squared = cimag(x) * cimag(x) + creal(x) * creal(x);
                if ( r_squared >= 4.0)
                {
                        return (double) i*1.0 - log(log(sqrt(r_squared))/ log(limit)) / log(2.0);
                }
        }
 
        return 0.0;
}
