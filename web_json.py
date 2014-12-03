import gecoloreffects, time, os, signal, fcntl, json, math, random
import tornado.httpserver, tornado.ioloop, tornado.web
import redis

from settings import *

HTTP_PORT = 8080

class DataHandler(tornado.web.RequestHandler):
    def get(self): 
        self.set_header("Content-Type", "text/plain")
        self.write("Try something like:\n\n   curl --data \"q=`node xmas.js`\" http://rpi-lights:8080/\n\nwhere xmas.js is https://gist.github.com/sbma44/9e63ac4c61ff07ca6707")

    def post(self):
        try:
            data = json.loads(self.get_argument('q'))
            rdis = redis.StrictRedis(host='localhost', port=6379, db=0)
            rdis.set('data', data)
        except:
            pass
        
class LightServer(object):
    def __init__(self):
        super(LightServer, self).__init__()
        self.redis = redis.StrictRedis(host='localhost', port=6379, db=0)
        self.con = gecoloreffects.Controller()

    def start(self):
        self.log("Starting webserver...")        
        self.application = tornado.web.Application([
            (r'/', DataHandler),
        ])
        self.webserver_pid = os.fork()
        if self.webserver_pid==0: # in child process
            self.is_webserver_process = True
            self.http_server = tornado.httpserver.HTTPServer(self.application)
            self.http_server.listen(HTTP_PORT)
            tornado.ioloop.IOLoop.instance().start()
        else:
            self.loop()
         
    def log(self, x):
        print x

    def loop(self):
        self.log('In event loop')
        data = None
        while True:            
            try:
                newdata = self.redis.get('data')
                data = json.loads(newdata)
            except:
                pass
            
            try:
                if data is not None:
                    for frame in data:
                        lights = frame.get('lights')
                        if lights:
                            for i in range(0, len(self.con.lights)):
                                self.con.lights[i].r = lights[i][0]
                                self.con.lights[i].g = lights[i][1]
                                self.con.lights[i].b = lights[i][2]
                        self.con.update_hue()
                        time.sleep(float(frame.get('delay', 0.5)))
            except:
                data = None

            time.sleep(0.1)
                
    def finish(self):
        """ Clean up lingering processes """
        os.kill(self.webserver_pid, signal.SIGTERM) 
    
if __name__ == '__main__':
    ls = LightServer()
    ls.start()

    try:
        ls.start()
    except Exception, e:
        raise e
    finally:
        ls.finish()