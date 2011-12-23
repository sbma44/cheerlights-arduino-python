import gecoloreffects, time, os, signal, fcntl, json
import tornado.httpserver, tornado.ioloop, tornado.web

MAX_MESSAGE_SIZE = 8192
HTTP_PORT = 8080

ls = None

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

class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        ls.log('served index')
        self.render("web/template/index.html", title="GE Color Effects HQ")

class ActionHandler(tornado.web.RequestHandler):
    def get(self):    
        try:
            mode = self.get_argument('mode')
        except:
            return
            
        if mode=='color':
            try:
                color = self.get_argument('color')
            except:
                return                    
            ls.send_message({'_': 'action', 'mode': 'color', 'color': color })
            ls.log('Setting color %s' % color)

        elif mode=='xmas':
            ls.send_message({'_': 'action', 'mode': 'xmas'})
            ls.log('Entering XMAS mode')
            

class LightServer(object):
    def __init__(self):
        super(LightServer, self).__init__()

        # interprocess stuff
        self.webserver_pid = None
        self.is_webserver_process = False
        self.web_rx, self.web_tx = os.pipe()
        self.inc_rx, self.inc_tx = os.pipe()

        # set pipes to not block
        fcntl.fcntl(self.web_rx, fcntl.F_SETFL, os.O_NONBLOCK)
        fcntl.fcntl(self.web_tx, fcntl.F_SETFL, os.O_NONBLOCK)
        fcntl.fcntl(self.inc_rx, fcntl.F_SETFL, os.O_NONBLOCK)
        fcntl.fcntl(self.inc_tx, fcntl.F_SETFL, os.O_NONBLOCK)
        
        self.mode = None
        self.color = None
        self.current_color = None
        
        self.con = gecoloreffects.Controller()

    def _print_log_message(self, msg):
        print "LOG: %s" % msg

    def log(self, msg):
        if self.is_webserver_process:
            self.send_message({'_':'log','message':msg})
        else:
            self._print_log_message(msg)
        
    def send_message(self, msg):  
        assert type(msg) is dict

        try:      
            socket = self.is_webserver_process and self.web_tx or self.inc_tx

            msg['_t'] = time.time()
            encoded_msg = json.dumps(msg)
            if len(encoded_msg)>MAX_MESSAGE_SIZE:
                self.log('Error: JSON package too large.')
            else:
                os.write(socket, "%s\n" % encoded_msg)
        except Exception, e:
            self.log(str(e))                
            
    def check_messages(self):
        if not self.is_webserver_process:
            socket = self.web_rx
            buf_i = 0
        else:    
            socket = self.inc_rx
            buf_i = 1

        data = ''
        buffer_empty = False
        while not buffer_empty:
            try:
                data = data + os.read(socket, MAX_MESSAGE_SIZE)
            except Exception, e:
                buffer_empty = True

        if len(data)==0:
            return []

        messages = data.split("\n")

        if len(messages[-1])==0:
            del messages[-1]

        decoded_messages = []
        for m in messages:
            try:
                decoded_messages.append((json.loads(m), m))
            except:
                decoded_messages.append(({'_': 'decode_failure'}, m))

        return decoded_messages    


    def handle_messages(self):
        msgs = self.check_messages()
        for (m, src) in msgs:       
            action = m['_']
            
            if action=='action':
                self.mode = m.get('mode', None)
                if self.mode=='color':
                    self.color = m.get('color', 'red')
            
            elif action=='decode_failure':
                print "Failed to decode JSON message: %s" % src

            elif action=='log':
                self._print_log_message(m['message'])


    def start(self):
        self.log("Starting webserver...")
        settings = {
            "static_path": os.path.join(os.path.dirname(__file__), "web", "static"),
        }
        self.application = tornado.web.Application([
            (r'/', IndexHandler),
            (r'/action', ActionHandler),
        ], **settings)

        self.webserver_pid = os.fork()
        if self.webserver_pid==0: # in child process
            self.is_webserver_process = True
            self.http_server = tornado.httpserver.HTTPServer(self.application)
            self.http_server.listen(HTTP_PORT)
            tornado.ioloop.IOLoop.instance().start()
        else:
            self.loop()

    def delay(self, secs):
        stop_time = time.time() + secs
        while time.time() < stop_time:
            self.handle_messages()
           
    def loop(self):
        self.log('In event loop')
        while True:
            if self.mode=='color':                
                if self.color != self.current_color:
                    target_light = COLOR_MAPPINGS.get(self.color, None)
                    if target_light is not None:
                        for i in range(0, len(self.con.lights)):
                            self.con.lights[i] = target_light
                        self.con.update_hue()
                        self.current_color = self.color
                self.delay(0.1)

            elif self.mode=='xmas':
                red = gecoloreffects.Light.XMAS_COLOR_RED()
                green = gecoloreffects.Light.XMAS_COLOR_GREEN()
                while True:
                    if self.mode!='xmas': break
                    for i in range(0,2):
                        if self.mode!='xmas': break
                        for j in range(0, len(self.con.lights)):
                            self.con.lights[j] = ((j+i)%2)==0 and green or red
                        self.con.update_hue()
                        self.delay(0.5)

            else:
                self.delay(0.1)
                
    def finish(self):
        """ Clean up lingering processes """
        os.kill(self.webserver_pid, signal.SIGTERM) 
    
    
if __name__ == '__main__':
    ls = LightServer()
    try:
        ls.start()
    except Exception, e:
        raise e
    finally:
        ls.finish()