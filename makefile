CC=gcc-4.9
CC=clang
CFLAGS= -O3 -ffast-math -Wstrict-prototypes -Wall --std=gnu99 -lm


mandelbrot_render.so : mandelbrot_render.o
	$(CC) -shared -fPIC $(CFLAGS) -o $@ $< #-Wl,-soname,$@

mandelbrot_render.o : mandelbrot_render.c
	$(CC) -c $(CFLAGS) -fPIC -o $@ $< #-Wl,-soname,$@



.PHONY: clean
clean:
	rm -rf *.o *.out *.so *.pyc *~ *.bak