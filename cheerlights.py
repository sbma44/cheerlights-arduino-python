import gecoloreffects, scrapelib, json, time

color_mappings = {
    'blue': gecoloreffects.Light.XMAS_COLOR_BLUE(),
    'warmwhite': gecoloreffects.Light.XMAS_COLOR_WHITE(),    
    'yellow': gecoloreffects.Light.XMAS_COLOR_YELLOW(),
    'green': gecoloreffects.Light.XMAS_COLOR_GREEN(),    
    'red': gecoloreffects.Light.XMAS_COLOR_RED(),
    'purple': gecoloreffects.Light.XMAS_COLOR_PURPLE(),
    'cyan': gecoloreffects.Light.XMAS_COLOR_CYAN(),
    'orange': gecoloreffects.Light.XMAS_COLOR_ORANGE()
}

if __name__ == '__main__':
    con = gecoloreffects.Controller()
    s = scrapelib.Scraper(requests_per_minute=10, allow_cookies=True, follow_robots=True)

    while True:
        cheerlights = json.loads(s.urlopen('http://api.thingspeak.com/channels/1417/field/1/last.json'))

        for i in range(0, len(con.lights)):
            con.lights[i] = color_mappings[cheerlights['field1']]

        con.update_hue()
        
        time.sleep(60)