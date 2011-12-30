import gecoloreffects, time
con = gecoloreffects.Controller()
con.update_hue()
time.sleep(0.1)
print 'done updating hue'
STEP = 8
while True:
    # for b in range(0, 0xF):
    #     for i in range(0, len(con.lights)):
    #         con.lights[i].r = b
    #         con.lights[i].g = 0
    #         con.lights[i].b = 0
    #     print '#'
    #     con.update_hue()
    #     time.sleep(0.1)
    #     print b
    # 
    # 
    # for b in range(0xF, 0, -1):
    #     for i in range(0, len(con.lights)):
    #         con.lights[i].r = b
    #         con.lights[i].g = 0
    #         con.lights[i].b = 0
    #     con.update_hue()
    #     time.sleep(0.1)
    #     print b
    
    
    for b in range(0, 0xCC, STEP):
        for i in range(0, len(con.lights)):
            con.lights[i].intensity = b
        con.update_intensity()    
        time.sleep(0.01)

    for b in range(0xCC, 0, (-2*STEP)):
        con.update_intensity()    
        time.sleep(0.01)

    time.sleep(0.3)



print 'done'