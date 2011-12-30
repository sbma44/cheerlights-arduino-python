import gecoloreffects, time
from settings import *

OFFSETS = (50, 63, 83, 103, 119, 139)
NUM_SEGMENTS = (len(OFFSETS) - 1)
# COLORS = (gecoloreffects.Light(6, 0, 0), gecoloreffects.Light(3, 0, 0), gecoloreffects.Light(0, 0, 0), gecoloreffects.Light(0, 0, 0), gecoloreffects.Light(16, 0, 0))
COLORS = (gecoloreffects.Light(16, 0, 16), gecoloreffects.Light(16, 16, 0), gecoloreffects.Light(16, 16, 0), gecoloreffects.Light(16, 16, 0), gecoloreffects.Light(16, 16, 0))

r = gecoloreffects.Light()
r.random_color()

if __name__ == '__main__':
    con = gecoloreffects.Controller()

    while True:

        for q in range(0, len(OFFSETS)):
            for (i,offset) in enumerate(OFFSETS):
                if(i>0):
                    for l in range(OFFSETS[i-1], OFFSETS[i]):
                        con.lights[l % NUM_LIGHTS] = COLORS[(q+i) % len(COLORS)]
            con.update_hue()                        
            time.sleep(0.08)        
            