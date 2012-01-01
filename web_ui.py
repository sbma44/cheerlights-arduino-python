import gecoloreffects, time, os, signal, fcntl, json, math, random
import tornado.httpserver, tornado.ioloop, tornado.web
from settings import *

MAX_MESSAGE_SIZE = 8192
HTTP_PORT = 8080

ls = None

OFFSETS = (50, 63, 83, 103, 119, 139)
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

        elif mode=='countdown':
            ls.send_message({'_': 'action', 'mode': 'countdown'})
            ls.log('Entering Countdown mode')

        elif mode=='waves':
            ls.send_message({'_': 'action', 'mode': 'waves'})
            ls.log('Entering WAVVES mode')

        elif mode=='cylon':
            ls.send_message({'_': 'action', 'mode': 'cylon'})
            ls.log('They have a plan.')

        elif mode=='sparkle':
            ls.send_message({'_': 'action', 'mode': 'sparkle'})
            ls.log('Affirming commitment to Sparkle Motion.')

        elif mode=='train':
            ls.send_message({'_': 'action', 'mode': 'train'})
            ls.log('Entering train mode.')

        elif mode=='easter':
            ls.send_message({'_': 'action', 'mode': 'easter'})
            ls.log('Entering easter mode.')

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
                        self.log('updating hue')
                        self.con.update_hue()
                        self.log('done')
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

            elif self.mode=='waves':
                NUM_SEGMENTS = (len(OFFSETS) - 1)
                COLORS = (gecoloreffects.Light(16, 0, 16), gecoloreffects.Light(16, 16, 0), gecoloreffects.Light(16, 16, 0), gecoloreffects.Light(16, 16, 0), gecoloreffects.Light(16, 16, 0))                
                while True:
                    if self.mode!='waves': break
                    for q in range(0, len(OFFSETS)):
                        for (i,offset) in enumerate(OFFSETS):
                            if(i>0):
                                for l in range(OFFSETS[i-1], OFFSETS[i]):
                                    self.con.lights[l % len(self.con.lights)] = COLORS[(q+i) % len(COLORS)]
                        self.con.update_hue()                        
                        self.delay(0.15)

            elif self.mode=='train':
                COLORS = (gecoloreffects.Light(16, 0, 16), gecoloreffects.Light(16, 16, 0), gecoloreffects.Light(0, 16, 16))
                TRAIN_LENGTH = 15
                offset = 0
                while True:
                    if self.mode!='train': break
                    for i in range(0, len(self.con.lights)):
                        self.con.lights[(i + LIGHTS_PER_STRING) % NUM_LIGHTS] = COLORS[((i+offset)/TRAIN_LENGTH) % len(COLORS)]

                    self.con.update_hue()                        
                    self.delay(0.05)        

                    offset = (offset + 1) % 1000000000

            elif self.mode=='sparkle':
                colors = []
                for i in range(16, 2, -1):
                    colors.append( gecoloreffects.Light(16, 16, i) )

                state = []
                for i in range(0, len(self.con.lights)):
                    state.append(0)

                while True:
                    if self.mode!='sparkle': break
                    for i in range(0, len(self.con.lights)):
                        self.con.lights[i] = colors[state[i]]
                        state[i] = max(state[i]-1, 0)
                        if random.random()<0.2:
                            state[i] = len(colors)-1

                    self.con.update_hue()                        
                    self.delay(0.07)        
                
            elif self.mode=='easter':
                STEP = 8
                black = gecoloreffects.Light(0,0,0)
                while True:
                    if self.mode!='easter': 
                        for i in range(0, len(self.con.lights)):
                            self.con.lights[i].intensity = gecoloreffects.Light.MAX_INTENSITY
                        self.con.update_intensity()
                        self.delay(0.05)
                        break

                    for b in range(0, 0xCC, STEP):
                        for i in range(0, len(self.con.lights)):
                            self.con.lights[i].intensity = b
                        self.con.update_intensity()    
                        self.delay(0.02)

                    for b in range(0xCC, 0, (-2*STEP)):
                        for i in range(0, len(self.con.lights)):
                            self.con.lights[i].intensity = b
                        self.con.update_intensity()    
                        self.delay(0.02)

                    for i in range(0, len(self.con.lights)):
                        self.con.lights[i].random_color()
                        self.con.lights[i].intensity = 0
                    self.delay(0.05)
                    self.con.update_intensity()        
                    self.delay(0.05)
                    self.con.update_hue()
                    self.delay(0.05)
            
            elif self.mode=='cylon':
                
                COLORS = (gecoloreffects.Light(16, 0, 0), gecoloreffects.Light(6, 0, 0), gecoloreffects.Light(3, 0, 0), gecoloreffects.Light(0, 0, 0))            
                SEGMENT_OFFSETS = (50, 63, 83, 103, 119, 139)
                
                for q in range(0, len(self.con.lights)):
                    self.con.lights[q] = COLORS[-1]
                self.con.update_hue()
                time.sleep(0.1)

                global_offset = 0
                while True:
                    if self.mode!='cylon': break
                    for q in range(0, len(self.con.lights)):
                        self.con.lights[q] = COLORS[-1]

                    for segment in range(0, len(SEGMENT_OFFSETS)-1):
                        start = SEGMENT_OFFSETS[segment]
                        end = SEGMENT_OFFSETS[segment+1]
                        sequence_length = (end - start) * 2

                        progress = start + (global_offset % sequence_length)
                        for i in range(0, len(COLORS)):
                            position = progress + i
                            if position<end:
                                self.con.lights[position % len(self.con.lights)] = COLORS[len(COLORS) - (i+1)]
                            else:          
                                new_pos = end - ((global_offset + i) % (end-start))
                                self.con.lights[new_pos % len(self.con.lights)] = COLORS[len(COLORS) - (i+1)]                

                    global_offset = (global_offset + 1) % 100000000        

                    self.con.update_hue()

                    self.delay(0.05)

            else:
                self.delay(0.01)
                
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