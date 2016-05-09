import alsaaudio as aa
import numpy   # from http://numpy.scipy.org/
import audioop
import sys
import math
import struct
import time
#graph 

from dotstar import Adafruit_DotStar

#globals
count = 0
curcolor = 0

 
def list_devices():
    #List all audio devices
    print aa.cards()

def init_list( length):
    list = []
    for i in xrange( 0 , length):
        list.append(0)
    
    return list

def calc_fps( tnot , fps ):
    fps += 1
    t = time.time() - tnot
    if( t>= 1.0):
        print( fps / t)
        tnot = time.time()
        fps = 0
    return tnot , fps

def init_strip( numpixels , brightness , datapin , clockpin):
    strip = Adafruit_DotStar(numpixels , 125000000)
    #strip = Adafruit_DotStar(numpixels, datapin , clockpin)
    #Initialize pins for output
    strip.begin()         
    strip.setBrightness(brightness) 
    return strip

def color_strip( strip , color , numpixels):
    for count in xrange( 0 , numpixels):
        ncolor = color
        #fix color for first 2 strips and last strip
        if( (count < 40) | (count >= 220)):
            ncolor = fix_color(color)
        #can be removed 
        
        
        strip.setPixelColor( count , ncolor )
    strip.show()
    
def init_pcm( device , samplerate , chunk ):
    pcm = aa.PCM( aa.PCM_CAPTURE , aa.PCM_NORMAL , device )
    pcm.setchannels(1)
    pcm.setrate(samplerate)
    pcm.setformat( aa.PCM_FORMAT_S16_LE )
    pcm.setperiodsize(chunk)
    return pcm



def do_fft( pcmdata , rate ):
    #returns numpy array that needs to be split later
    try:
        ### DO THE FFT ANALYSIS ###
        fft=numpy.fft.fft(pcmdata)
        fftb=10*numpy.log10(numpy.sqrt(fft.imag**2+fft.real**2))[:len(pcmdata)/2]
        
        #freq=numpy.fft.fftfreq(numpy.arange(len(pcm)).shape[-1])[:len(pcm)/2]
        #freq=freq*rate/1000 #make the frequency scale
    except ValueError as e:
            print e
            print "FFT error"
        
    return fft 
    
    
def fix_color( color ):
    #swaps color from RGB to RBG or back format due to my strips being inconsistent 
    gbyte = (color & 0x00FF00) >> 8
    bbyte = (color & 0x0000FF) << 8
    ret = (color & 0xFF0000) + gbyte + bbyte
    return ret
    
    
def dynam_scale( scale , value , targetscale ):
    targetscale = value
    scale += int((targetscale - scale) / 10)      
    return targetscale , scale
    
    
def smooth_color( targetcolor , currentcolor):
    smoothval = 50
    tred = targetcolor & 0xFF0000
    tgreen = targetcolor & 0x00FF00
    tblue = targetcolor & 0x0000FF
    cred = currentcolor & 0xFF0000
    cgreen = currentcolor & 0x00FF00
    cblue = currentcolor & 0x0000FF
    
    
    r = int( (tred - cred) / smoothval) + cred
    g = int( (tgreen - cgreen) / smoothval) + cgreen
    b = int( (tblue - cblue) / smoothval) + cblue  
            
    currentcolor = ((r << 16) + (g << 8) ) + b
    
    return currentcolor
    
    
    
    
    
def form_color( valuelist):
    global count 
    

    scale = float((count + 1) * 20)
    r = 0
    rc = 0 
    g = 0
    gc = 0
    b = 0
    bc = 0
            
    length = len( valuelist)
    third = int(length / 3)
    for i in xrange( 0 , length ):
        if( i < third):
            b+= valuelist[i]
            bc+= 1
        
        elif( i < (2 * third)):
            g+= valuelist[i]
            gc+= 1
        
        
        elif( i < (length)):   
            r+= valuelist[i]
            rc+= 1
   
    # extra cooeficients can be  tweaked
    b = 0.95 * b
    g = 1.0 * g
    r = 1.1 * r
   
            
     #prevent white effect
    lowval = 0
    if( r < g):
        if( r < b):
            r *= lowval
        else:
            b *= lowval
    else:
        if( g < b):
            g *= lowval
        else:
            b *= lowval
    
    r = int( r / float(rc) / scale * 255 )
    g = int( g / float(gc) / scale  * 255)
    b = int( b / float(bc) / scale * 255)
    
    
    #print r , g, b 
    
    color = ( r << 16) + (g << 8) + b
    
   
    
    return color
        
        
        
    
    


def strip_control(value , offset , strip, striplength , color ):
    #vars
    global scale
    blank = 0x000000

     # # if statement only for my strips due to inconsistency in RGB vs RBG 
    stripnumb = offset / striplength 
    if( (stripnumb <= 1 ) ):
        color = fix_color(color)
    # end of can be removed 
    
    
    #reverse odd strips
    if( (stripnumb % 2 )== 1):
        value = striplength - value
        blank = color
        color = 0x000000
        
    value = value + offset

    for count in xrange( offset , offset + striplength  ):
        if(count < value ):
            strip.setPixelColor( count , color)
        else:
            strip.setPixelColor( count , blank)
            
    return strip
            
             
    
def run():
    global count
    global curcolor
     
    #strip vars

    striplength = 20
    numpixels =220
    numstrips = 11
    #Limit brightness to ~1/4 duty cycle
    brightness = 128
    datapin = 23
    clockpin = 18
    
    #colors
    blue = 0x000000
    red = 0xFF0000
    color = 0

    #pcm data vars
    device   = 'J2400'
    chunk      = 1024 # Change if too fast/slow
    samplerate = 44100
    
    #scale
    scale = 1
    tscale = 1
   
    
    #fps
    fps = 0
    tnot = time.time()
    
    #initializions
    strip = init_strip( numpixels , brightness ,datapin , clockpin)
    pcm = init_pcm( device , samplerate , chunk)
    valuelist = init_list( numstrips)
  
   #MAIN LOOP
    while True:
        
        
        #make sure pcm data is good
        length, data  = pcm.read()
        while ( length < 0):
            length, data  = pcm.read()
        #parse data, apply fft , and split into strips    
        a = numpy.fromstring(data, dtype=numpy.int16)   
        fftdata = do_fft(a , samplerate)      
        fftlist = numpy.array_split(fftdata , 7 ) # this value can be tweaked. in my case setting it to 5 will give me about 0 - 20khz. 7 worked better for music.
        #cut off low 
        if numpy.amax(fftlist[0]).astype(int) < 1400:
            tscale = tscale
            scale = 100000000
        else:
            tscale , scale = dynam_scale( scale , numpy.amax(fftlist[0]).astype(int)   , tscale)  #calculate scaling on this cycle    
            
        fftlist = numpy.array_split(fftlist[0] , numstrips ) #split the first section and split across the strips
    
        curcolor = form_color(valuelist)
            
        #curcolor = smooth_color( color , curcolor)
        if((count % 10) == 0 ):
           valuelist = init_list(numstrips)
           
           
        #loop through strips and s
        for i in xrange(0 , numstrips):
            offset = i * striplength
            value = numpy.amax(fftlist[i]).astype(int)
            value = int( value / float(scale) * striplength)
            
            valuelist[i] += value
         
            strip = strip_control( value , offset , strip , striplength , curcolor  ) # optimize
        strip.show()
        
        
       
        
        #reset or increment count 
        if(count == 100 ):
            count = 0
        else:   
            count += 1
        
        #fps
        tnot , fps = calc_fps(tnot , fps)
        
 

if __name__ == '__main__':  
    list_devices()
    run()


