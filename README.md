# PiSpectrum #

My first RaspberryPi project done in 2014. The Pi takes audio output from a usb headset and applies a Fast Fourier Transform and then controls the LEDS. Project gets about 16 FPS on a Pi Model A.
There is probably a couple of things that could be optimized. The leds are [Adafruit Dotstar](https://www.adafruit.com/products/2240).

[Demonstration Video](https://youtu.be/-LMZxSWGLSQ)


This article helped me understand how to use the FFT in python. [Article Link](http://www.swharden.com/blog/2010-06-23-insights-into-ffts-imaginary-numbers-and-accurate-spectrographs/)


Dependencies

-[PyAlsaAudio](http://larsimmisch.github.io/pyalsaaudio/)


-[Dotstar Python Module](https://github.com/adafruit/Adafruit_DotStar_Pi)
