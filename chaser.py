import gecoloreffects, time

if __name__ == '__main__':
    con = gecoloreffects.Controller()

    # set all to green
    for i in range(0, len(con.lights)):
        con.lights[i] = gecoloreffects.Light.XMAS_COLOR_GREEN()
    con.update_hue()

    CHAIN_LENGTH = 7

    while True:
        for o in range(0,CHAIN_LENGTH):
            for i in range(0, len(con.lights)):
                if ((i+o) % CHAIN_LENGTH)==0:
                    con.lights[i] = gecoloreffects.Light.XMAS_COLOR_RED()
                else:
                    con.lights[i] = gecoloreffects.Light.XMAS_COLOR_GREEN()
            con.update_hue()
            time.sleep(0.1)
