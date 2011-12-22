import gecoloreffects, time

BENCHMARK_SIZE = 250

if __name__ == '__main__':
    con = gecoloreffects.Controller()

    start_time = time.time()
    for i in range(0, BENCHMARK_SIZE):
        for j in range(0, len(con.lights)):
            con.lights[j] = (i%2)==0 and gecoloreffects.Light.XMAS_COLOR_YELLOW() or gecoloreffects.Light.XMAS_COLOR_GREEN()
        con.update_hue()
    end_time = time.time()
    
    print "Hue update: %0.2f FPS" % (BENCHMARK_SIZE / (end_time - start_time))
