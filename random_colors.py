import gecoloreffects, time

if __name__ == '__main__':
    print 'connecting...'
    con = gecoloreffects.Controller()
    print 'connected'


    print "there are %d lights" % len(con.lights)

    for i in range(0, len(con.lights)):
        con.lights[i] = gecoloreffects.Light().random_color()
        # con.lights[i] = ((i%2)==0) and gecoloreffects.Light.XMAS_COLOR_CYAN() or gecoloreffects.Light.XMAS_COLOR_RED()
        # con.lights[i] = gecoloreffects.Light.XMAS_COLOR_GREEN()
    print 'updating hue'
    con.update_hue()
    print 'done'    

    while True:
        pass