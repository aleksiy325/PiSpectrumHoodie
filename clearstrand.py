import time
from dotstar import Adafruit_DotStar


numpixels = 360 

datapin   = 23
clockpin  = 18
strip     = Adafruit_DotStar(numpixels, 125000000)

strip.begin()           # Initialize pins for output
strip.setBrightness(64) # Limit brightness to ~1/4 duty cycle




for count in xrange(0, 60):
                strip.setPixelColor(count, 0x000000)
                strip.show()


    
    

