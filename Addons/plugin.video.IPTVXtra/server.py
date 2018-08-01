
import xbmc, xbmcaddon, xbmcgui, xbmcplugin
import json, re, urllib, urllib2
from urlparse import urlparse, parse_qs
import socket, SocketServer
import SimpleHTTPServer
import string,cgi,time
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import threading

import tools
from tools import addon, addonname
from tools import alert
    
import stalker

import m3u


server = None

IP, port, host = tools.get_localhost()


class TimeoutError(RuntimeError):
    pass


class AsyncCall(object):
    def __init__(self, fnc, callback = None):
        self.Callable = fnc
        self.Callback = callback

    
    def __call__(self, *args, **kwargs):
        self.Thread = threading.Thread(target = self.run, name = self.Callable.__name__, args = args, kwargs = kwargs)
        self.Thread.start()
        return self

    
    def wait(self, timeout = None):
        self.Thread.join(timeout)
        if self.Thread.isAlive():
            raise TimeoutError()
        else:
            return self.Result

    
    def run(self, *args, **kwargs):
        self.Result = self.Callable(*args, **kwargs)
        if self.Callback:
            self.Callback(self.Result)


class AsyncMethod(object):
    def __init__(self, fnc, callback=None):
        self.Callable = fnc
        self.Callback = callback

    def __call__(self, *args, **kwargs):
        return AsyncCall(self.Callable, self.Callback)(*args, **kwargs)


def Async(fnc = None, callback = None):
    if fnc == None:
        def AddAsyncCallback(fnc):
            return AsyncMethod(fnc, callback)
        return AddAsyncCallback
    else:
        return AsyncMethod(fnc, callback)
        

def send_obj(obj, type, val):

    content = {'html':'text/html', 'xml':'application/xml', 'm3u':'application/x-mpegURL'}
    
    obj.send_response(200)    
    obj.send_header('Content-type',    content[type])
    obj.send_header('Connection',    'close')
    obj.send_header('Content-Length', len(val))
    obj.end_headers()    
    obj.wfile.write(val)
    

def redirect(obj, url):
    
    obj.send_response(301)
    obj.send_header('Location', url)
    obj.end_headers()
    obj.finish()
    

class MyHandler(BaseHTTPRequestHandler):


    def do_HEAD(self):
        
        self.send_response(200)

        if '/channels' in self.path:
            self.send_header('Content-type', 'application/x-mpegURL')
            
        elif '/play' in self.path:
            is_dash = any (item in self.path for item in ['rtmp%3A%2F%2F', 'dash%3D'])
            content = 'application/x-mpegURL' if is_dash else 'application/vnd.apple.mpegurl'
            self.send_header('Content-type', content)
            self.send_header('Accept-Ranges', 'none')

        else:
            self.send_header('Content-type', 'txt/html')
        
        self.end_headers()
    
    
    def do_GET(self):
        from tools import no_video

        try:
            if '.m3u' in self.path.lower():
                try:
                    fm3u = m3u.m3u_create()
                    with open(fm3u, 'r') as f: EXTM3U = f.read()
                    
                except Exception as e:
                    EXTM3U += '#EXTINF:-1, tvg-id="Error" tvg-name="Error" tvg-logo="" group-title="Error", ' + str(e) + '\n'
                    EXTM3U += 'http://\n\n'
            
                send_obj(self, 'm3u', EXTM3U)
                self.finish()
                
            elif '/play' in self.path:
                args = parse_qs(urlparse(self.path).query)
                try:
                    channel = args['channel'][0]
                    url = stalker.get_url(channel)
                except Exception as e:
                    alert(str(e))
                    url = None
                
                if not url: url = no_video()
                
                redirect(self, url)
                
            elif '/stop' in self.path:
                msg = 'Stopping ...'
                send_obj(self, 'html', msg)
                server.socket.close()
                
            elif '/online' in self.path:
                msg = 'Yes. I am.'
                send_obj(self, 'html', msg)

            else:
                self.send_error(400,'Bad Request')
                
        except IOError:
            self.send_error(500,'Internal Server Error ' + str(IOError))


@Async
def startServer():
    global server
    from config import token_type
    
    server_enable = (token_type == 1)
    
    if not server_enable: return
    
    try:
        server = SocketServer.TCPServer(('', int(port)), MyHandler)
        server.serve_forever()
        
    except KeyboardInterrupt:
        if server: server.socket.close()




def serverOnline():
    
    try:
        url = urllib.urlopen(host + '/online')
        code = url.getcode()
        if code == 200: return True
    except:
        pass

    return False




def stopServer():
    
    try:
        url = urllib.urlopen(host + '/stop')
        code = url.getcode()

    except:
        pass

    return


    

def run(action):
    
    if action == 'start':
        if serverOnline():
            xbmcgui.Dialog().notification(addonname, 'Server already started.\nPort: ' + str(port), xbmcgui.NOTIFICATION_INFO )
        else:
            startServer()
            time.sleep(5)
            if serverOnline():
                xbmcgui.Dialog().notification(addonname, 'Server started.\nPort: ' + str(port), xbmcgui.NOTIFICATION_INFO )
            else:
                xbmcgui.Dialog().notification(addonname, 'Server not started. Wait a minute and try again. ', xbmcgui.NOTIFICATION_ERROR )
                
    
    elif action == 'stop':
        if serverOnline():
            stopServer()
            time.sleep(5)
            xbmcgui.Dialog().notification(addonname, 'Server stopped.', xbmcgui.NOTIFICATION_INFO )
        else:
            xbmcgui.Dialog().notification(addonname, 'Server is already stopped.', xbmcgui.NOTIFICATION_INFO )
                
    
    elif action == 'check':
        status = '[COLOR lime]O N[/COLOR]' if serverOnline() else '[COLOR red]O F F[/COLOR]'
        alert('Server:  '+status)




if __name__ == '__main__':
    startServer()
