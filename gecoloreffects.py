import serial, random, time, colorsys
from settings import *


class Light(object):
    MAX_INTENSITY = 0xCC
    MAX_HUE = 0xF
    
    @staticmethod
    def XMAS_COLOR_WHITE():
        return Light(Light.MAX_HUE, Light.MAX_HUE, Light.MAX_HUE, Light.MAX_INTENSITY)
        
    @staticmethod
    def XMAS_COLOR_RED():
        return Light(Light.MAX_HUE, 0, 0, Light.MAX_INTENSITY)
        
    @staticmethod
    def XMAS_COLOR_GREEN():
        return Light(0, Light.MAX_HUE, 0, Light.MAX_INTENSITY)
        
    @staticmethod
    def XMAS_COLOR_BLUE():
        return Light(0, 0, Light.MAX_HUE, Light.MAX_INTENSITY)
        
    @staticmethod
    def XMAS_COLOR_CYAN():
        return Light(0, Light.MAX_HUE, Light.MAX_HUE, Light.MAX_INTENSITY)
        
    @staticmethod
    def XMAS_COLOR_PURPLE():
        return Light(Light.MAX_HUE, 0, Light.MAX_HUE, Light.MAX_INTENSITY)
        
    @staticmethod
    def XMAS_COLOR_YELLOW():
        return Light(Light.MAX_HUE, Light.MAX_HUE, 0, Light.MAX_INTENSITY)
        
    @staticmethod
    def XMAS_COLOR_ORANGE():
        return Light(Light.MAX_HUE, Light.MAX_HUE/6, 0, Light.MAX_INTENSITY)
            
    def __init__(self, r=0, g=0, b=0, intensity=None):
        super(Light, self).__init__()
        self.r = r
        self.g = g
        self.b = b
        self.intensity = (intensity is not None) and intensity or self.MAX_INTENSITY
        
    def safe(self):
        for color in ('r', 'g', 'b'):
            setattr(self, color, min(getattr(self, color), self.MAX_HUE))
        self.intensity = min(self.intensity, self.MAX_INTENSITY)

    def random_color(self):
        (r, g, b) = colorsys.hsv_to_rgb(random.random(), 1, 1)
        self.r = int(self.MAX_HUE * r)
        self.g = int(self.MAX_HUE * g)
        self.b = int(self.MAX_HUE * b)
        self.intensity = self.MAX_INTENSITY
        return self

    def get_intensity(self):
        self.safe()
        return 0xFF & self.intensity
        
    # deprecated
    def get_color(self):
        self.safe()
        return ( (0xFF & ((self.r << 4) | self.g)), (0xFF & self.b) )

class Controller(object):

    def __init__(self):
        super(Controller, self).__init__()

        self.lights = []
        for i in range(0, NUM_LIGHTS):
            self.lights.append(Light().random_color())

        self.ser = serial.Serial(SERIAL_PORT, SERIAL_RATE)
        time.sleep(2) # wait for the Arduino to reboot

    def update_intensity(self):
        # send intensity
        self.ser.write('I')
        
        self.ser.readline() # unsure why this is necessary but it is
        
        for string_offset in (0, LIGHTS_PER_STRING):
            for i in range(0, LIGHTS_PER_STRING):
                l = self.lights[string_offset + i]
                l.safe()
                self.ser.write(chr(0xFF & l.intensity))  

            # wait for ack -- do this twice        
            self.ser.readline()
        
    def update_hue(self):
        self.ser.write('H')
        
        for string_offset in (0, LIGHTS_PER_STRING):
            for i in range(0, LIGHTS_PER_STRING/2):
                light_a = self.lights[string_offset + (i*2)]
                light_b = self.lights[string_offset + ((i*2)+1)]

                light_a.safe()
                light_b.safe()

                self.ser.write(chr((light_a.r<<4) | light_a.g))
                self.ser.write(chr((light_a.b<<4) | light_b.r))
                self.ser.write(chr((light_b.g<<4) | light_b.b))            

            # need to do this twice due to the 128 byte buffer on the arduino serial
            self.ser.readline()
        
