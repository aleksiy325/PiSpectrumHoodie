#!/usr/bin/python

# Simple strand test for Adafruit Dot Star RGB LED strip.
# This is a basic diagnostic tool, NOT a graphics demo...helps confirm
# correct wiring and tests each pixel's ability to display red, green
# and blue and to forward data down the line.  By limiting the number
# and color of LEDs, it's reasonably safe to power a couple meters off
# USB.  DON'T try that with other code!

import time
from dotstar import Adafruit_DotStar

def fix_color( color ):
    #swaps color from RGB to RBG or back format due to my strips being inconsistent 
    gbyte = (color & 0x00FF00) >> 8
    bbyte = (color & 0x0000FF) << 8
    ret = (color & 0xFF0000) + gbyte + bbyte
    return ret

numpixels = 30 # Number of LEDs in strip

# Here's how to control the strip from any two GPIO pins:
datapin   = 23
clockpin  = 18
strip     = Adafruit_DotStar(numpixels, 125000000)

# Alternate ways of declaring strip:
# strip   = Adafruit_DotStar(numpixels)           # Use SPI (pins 11, 12)
# strip   = Adafruit_DotStar(numpixels, 32000000) # SPI @ ~32 MHz
# strip   = Adafruit_DotStar()                    # SPI, No pixel buffer
# strip   = Adafruit_DotStar(32000000)            # 32 MHz SPI, no pixel buf
# See image-pov.py for explanation of no-pixel-buffer use.

strip.begin()           # Initialize pins for output
strip.setBrightness(64) # Limit brightness to ~1/4 duty cycle

# Runs 10 LEDs at a time along strip, cycling through red, green and blue.
# This requires about 200 mA for all the 'on' pixels + 1 mA per 'off' pixel.

head  = 0               # Index of first 'on' pixel
tail  = -10             # Index of last 'off' pixel
color = 0xFF0000        # 'On' color (starts red)


 #fps
fps = 0
tnot = time.time()
    

for count in xrange( 0 , 200):                              # Loop forever
    ncolor = color
    if( (head < 40 ) | (head >= 220)):
        ncolor = fix_color(ncolor)
    
    
    strip.setPixelColor(head, ncolor) # Turn on 'head' pixel
    strip.setPixelColor(tail, 0)     # Turn off 'tail'
    strip.show()                     # Refresh strip
    time.sleep(1.0 / 50 )             # Pause 20 milliseconds (~50 fps)

    head += 1                        # Advance head position
    if(head >= numpixels):           # Off end of strip?
        head    = 0              # Reset to start
        color >>= 8              # Red->green->blue->black
        if(color == 0): color = 0xFF0000 # If black, reset to red

    tail += 1                        # Advance tail position
    if(tail >= numpixels): tail = 0  # Off end? Reset
    
     #fps
    fps += 1
    t = time.time() - tnot
    if( t>= 1.0):
        print( fps / t)
        tnot = time.time()
        fps = 0
            
    
    

