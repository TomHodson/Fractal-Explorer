CC=gcc
CFLAGS=-Wall --std=gnu99 -lm


mandelbrot_render.so : mandelbrot_render.c
	$(CC) -shared -fPIC $(CFLAGS) -o $@ $< #-Wl,-soname,$@

.PHONY: clean
clean:
	rm -rf *.o *.so *.pyc *~ *.bak
