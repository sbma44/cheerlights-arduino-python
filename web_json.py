#!/home/pi/.virtualenvs/cheerlights/bin/python


import gecoloreffects, time, os, signal, fcntl, json, math, random
import tornado.httpserver, tornado.ioloop, tornado.web
import redis

from settings import *

HTTP_PORT = 8080

class DataHandler(tornado.web.RequestHandler):
    
    def _json_is_valid(self, data):
        is_valid = True
        if type(data) is not list:
            is_valid = False
        else:
            for frame in data:
                if type(frame) is not dict:
                    is_valid = False
                else:
                    if ('delay' not in frame) or ('lights' not in frame):
                        is_valid = False
                    else:
                        try:
                            if float(frame['delay'])<(1.0/24):
                                is_valid = False
                        except:
                            is_valid = False
                        if type(frame['lights']) is not list:
                            is_valid = False
                        elif len(frame['lights']) != NUM_LIGHTS:
                            is_valid = False
                        else:
                            for l in frame['lights']:
                                if type(l) is not list:
                                    is_valid = False
                                elif len(l) != 3:
                                    is_valid = False
                                else:
                                    for b in l:
                                        try:
                                            if int(b)<0 or int(b)>15:
                                                is_valid = False
                                        except:
                                            is_valid = False
        return is_valid

    def get(self): 
        self.set_header("Content-Type", "text/plain")
        self.write("Try something like:\n\n   curl --data \"q=`node xmas.js`\" http://rpi-lights:8080/\n\nwhere xmas.js is https://gist.github.com/sbma44/9e63ac4c61ff07ca6707")

    def post(self):
        try:
            data = json.loads(self.get_argument('q'))

            if self._json_is_valid(data):
                rdis = redis.StrictRedis(host='localhost', port=6379, db=0)
                rdis.set('data', json.dumps(data))
            else:
                self.set_status(400, 'Bad input data. Ensure delay is >=%0.2fs and you have specified %d lights' % ((30.0 / 24), NUM_LIGHTS))
        except:
            self.set_status(500, 'Error (probably from parsing bad JSON)')
        
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
            
            newdata = self.redis.get('data')
            if newdata is not None and len(newdata):
                data = json.loads(newdata)
            
            did_something = False

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
                        did_something = True
                        time.sleep(float(frame.get('delay', 0.5)))
            except:
                data = None

            # if we didn't have any frames to play, avoid slamming redis
            if not did_something:
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
