
import os, sys, re, urllib, urllib2, urlparse, json
import xbmc, xbmcaddon, xbmcgui, xbmcplugin




def init():
    import datetime
    
    global addon, addonname, addondir
    global userAgent, header_ua
    global default_fanart
    global kodi
    global now
    
    addon = xbmcaddon.Addon()
    addonname = addon.getAddonInfo('name')
    addondir = xbmc.translatePath( addon.getAddonInfo('profile') ).replace("\\", "/")
    
    arg_init()
    
    userAgent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10) AppleWebKit/600.1.25 (KHTML, like Gecko) Version/8.0 Safari/600.1.25'
    header_ua = {'User-Agent' : userAgent}

    kodi = xbmc.getInfoLabel('System.BuildVersion').split()[0].split('.')
    
    now = datetime.datetime.now()
    
    
    

def arg_init():
    global addon_handle
    global base_url, current_url
    global args, base_arg
    
    try:
        addon_handle = int(sys.argv[1])
        base_url = sys.argv[0]    
        current_url = base_url+sys.argv[2]
        args = urlparse.parse_qs(sys.argv[2][1:])
        base_arg = args.copy()
        for key, val in base_arg.iteritems(): base_arg[key] = val[0]
    
    except:
        addon_handle, base_url, current_url, args, base_arg = [None, None, None, None, None]
    
    
    

def addon_init():
    
    if not os.path.isdir(addondir): os.makedirs(addondir)
    
    info1 = [addon, addonname, addondir]
    info2 = [base_url, addon_handle, args, current_url, base_arg]
    
    return [info1, info2]
    


def alert(msg): 

    xbmcgui.Dialog().ok(xbmcaddon.Addon().getAddonInfo('name'), msg)
        
    


def notify(title, msg, icon, sec):
    
    xbmc.executebuiltin('Notification('+title+','+msg+','+str(sec*1000)+','+icon+')')
    
    

def curl(url, params, headers):
    
    req = urllib2.Request(url, params, headers)
    resp = urllib2.urlopen(req).read()
    try: resp = json.loads(resp)
    except: pass
    
    return resp
    
    
def xcurl(url, args, headers):
    import base64
    
    try:
        mac, donation, token = json.loads(args['auth'][0])
        info = json.loads(args['info'][0])["js"]
        data = [[base64.b64encode(mac), "mac"], [donation, "username"], [token, "token"]]
        for i in data:
            result = (i[0] == info[i[1]])
            if not result: break
    except Exception as e:
        alert('[COLOR red]ERROR:[/COLOR]\n\nAuthentication FAILED\n'+str(e))
        result = False
        
    return [info["username"], info["password"]] if result else result
    
    


def redirect(url, headers):

    req = urllib2.Request(url, None, headers)
    res = urllib2.urlopen(req)
    finalurl = res.geturl()
    
    return finalurl
        
    

def pipeURL(url):
    
    if (not url.startswith('http')) or ('|' in url): return url
    
    params = urllib.urlencode(header_ua)
    url += '|' + params
    
    return url



def url_encode(cmd):
    
    try:
        return cmd+''
    except:
        url, vars = cmd
        if not url: url = base_url
        params = urllib.urlencode(vars) if vars else ''
    
    return url + '?' + params if params else url
    



def window_open(url):

    try: url = '' + url
    except: url = url_encode(url)
    
    xbmc.executebuiltin('Container.Update(%s)' % url)



def view_mode(type):

    xbmc.executebuiltin('Container.SetViewMode('+str(type)+')')
        



def line(n, color):
    
    dash = '-' * int(n)
    li = xbmcgui.ListItem('[COLOR '+color.lower()+']'+dash+'[/COLOR]', iconImage=None, thumbnailImage=None)
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=current_url, listitem=li, isFolder=True)
    



def metadata_set(li, meta):

    if not meta: return li
    
    try: meta, flags = meta
    except: flags = None
    
    li.addStreamInfo('video', {})
    
    if meta:
        try:
            li.setProperty('fanart_image', meta['fanart'])
            del meta['fanart']
        except:
            pass
        li.setInfo(type='Video', infoLabels=meta)
    
    return li
        


def menu_set(li, menus):

    if not menus: return li
    
    menu, replace = menus
    menus = []
    for item, cmd in menu:
        try: menus.append([item, 'XBMC.RunPlugin(' + url_encode(cmd) + ')'])
        except: menus.append([item, cmd])
    
    li.addContextMenuItems(menus, replace)
    
    return li



def add_item(item, cmd, icon, menus, meta, last):
    
    if item.startswith('*'):
        line(40, 'red')
        item = item[1:]
        
    try: item, color = item.split('||')
    except: color = 'silver'
#    item = '[COLOR ' + color.lower() + ']' + item + '[/COLOR]'
    icon = icon if icon else 'DefaultProgram.png'
    
    url = url_encode(cmd)
    
    li = xbmcgui.ListItem(item, iconImage=icon, thumbnailImage=icon)
    li = menu_set(li, menus)
    li = metadata_set(li, meta)

    is_folder = (meta == None)
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=is_folder)
    if last: xbmcplugin.endOfDirectory(addon_handle)



def get_string(left, right, source):
    result = re.findall(left+"(.*?)"+right, source)
    return result
    


def fileExpired(f, exp_secs):
    import time

    if not os.path.isfile(f): return True
    delta = time.time() - os.path.getmtime(f)
    
    return (delta >= exp_secs)

    
def local_ip():
    import socket
    
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8",80))
    ip = s.getsockname()[0]
    s.close()
    
    return ip

  
def get_localhost():
    host_ip   = local_ip()
    host_port = addon.getSetting("server_port")
    host_addr = "http://" + host_ip + ":" + host_port
    
    return [host_ip, host_port, host_addr]

    

def hashText(txt):
    import hashlib
    
    m = hashlib.md5(txt).hexdigest()
    m = ''.join([m[len(m)-i-1] for i in range(0, len(m))])    
     
    return m
    
    

def youtube(yid):

    url = 'http://keepvid.com/?url=https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3D'+yid
    try:
        data = curl(url, None, header_ua)
        url = get_string('Full Video.*?href="', '"', data)[0]
    except:
        url = ''
    
    return url
    


def no_video():
    import random

    url = 'https://www.dropbox.com/s/306jq21872ottjd/my_vids.json?raw=true'
    try:
        data = json.loads(urllib2.urlopen(url).read())
        id = random.randint(0, len(data)-1)
        url = youtube(data[id])
    except:
        url = ''
        
    if not all (item in url for item in ['://', '/', '.']):
        url = 'http://nasatv-lh.akamaihd.net/i/NASA_101@319270/master.m3u8'
    
    return url

        

################################### MAIN ###################################


init()
    


