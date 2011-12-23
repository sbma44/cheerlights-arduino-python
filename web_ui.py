import gecoloreffects, time, os
import tornado.httpserver, tornado.ioloop, tornado.web

COLOR_MAPPINGS = {
    'blue': gecoloreffects.Light.XMAS_COLOR_BLUE(),
    'white': gecoloreffects.Light.XMAS_COLOR_WHITE(),    
    'warmwhite': gecoloreffects.Light.XMAS_COLOR_WHITE(),    
    'yellow': gecoloreffects.Light.XMAS_COLOR_YELLOW(),
    'green': gecoloreffects.Light.XMAS_COLOR_GREEN(),    
    'red': gecoloreffects.Light.XMAS_COLOR_RED(),
    'purple': gecoloreffects.Light.XMAS_COLOR_PURPLE(),
    'magenta': gecoloreffects.Light.XMAS_COLOR_PURPLE(),
    'cyan': gecoloreffects.Light.XMAS_COLOR_CYAN(),
    'orange': gecoloreffects.Light.XMAS_COLOR_ORANGE()
}

con = gecoloreffects.Controller()

class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("web/template/index.html", title="GE Color Effects HQ")

class ActionHandler(tornado.web.RequestHandler):
    def get(self):    
        try:
            color = self.get_argument('color')
        except:
            return

        target_light = COLOR_MAPPINGS.get(color, None)
        if target_light is not None:
            for i in range(0, len(con.lights)):
                con.lights[i] = target_light
            con.update_hue()

        
if __name__ == '__main__':    
    print "Starting webserver..."
    settings = {
        "static_path": os.path.join(os.path.dirname(__file__), "web", "static"),
    }
    application = tornado.web.Application([
        (r'/', IndexHandler),
        (r'/action', ActionHandler),
    ], **settings)

    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(8080)
    tornado.ioloop.IOLoop.instance().start()