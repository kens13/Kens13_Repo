# -*- coding: utf-8 -*-



import xbmc, xbmcaddon, xbmcgui, xbmcplugin
import os, sys, json, urllib, urllib2, base64, re

from tools import addon_init
from tools import fileExpired
from tools import alert, notify
from tools import xcurl

from config import stalker_init
from config import mac, donation, server
from config import portal_url, portal_ref
from config import vod_pages
from config import mac_based
from config import token_type

from m3u import m3u_create
from m3u import m3u_read


reload(sys)
sys.setdefaultencoding('utf8')

    

def dir_init():
    global addon, addonname, data_dir, alldir
    global user_dir, addon_dir, resource_dir, strm_dir

    info = addon_init()
    [addon, addonname, data_dir], info = info
    addon_dir = data_dir.replace('userdata/addon_data', 'addons')
    user_dir = data_dir.split('addon_data')[0]
    alldir = user_dir.replace('/userdata', '/addons')
    resource_dir = os.path.join(addon_dir, 'resources/')
    strm_dir = os.path.join(data_dir, 'STRM Files/')

    return info
    
    
    

def init():
    global userAgent
    global timezone
    global kodi
    global acc_ok
    
    acc_ok = True

    dir_init()
    stalker_init()
    cache_init()
    
    timezone = addon.getSetting("tzone").split(' | ')[0]
    userAgent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10) AppleWebKit/600.1.25 (KHTML, like Gecko) Version/8.0 Safari/600.1.25'
    
    kodi = xbmc.getInfoLabel('System.BuildVersion').split()[0].split('.')
    
    
    

def cache_init():
    global cache_dir
    global fkey, fgenre, fchannel, fvod, fvod_genre, fm3u, fadult
    global exp_token, exp_iptv, exp_vod
    
    cache_dir = os.path.join(data_dir, '['+server+']/')
    if server and not os.path.isdir(cache_dir): os.mkdir(cache_dir)

    fkey = os.path.join(cache_dir, 'key.json')
    fgenre = os.path.join(cache_dir, 'genres.json')
    fchannel = os.path.join(cache_dir, 'channels.json')
    fvod = os.path.join(cache_dir, 'vod.json')
    fvod_genre = os.path.join(cache_dir, 'vod_genres.json')
    fm3u = os.path.join(cache_dir, 'iptvxtra.m3u')
    fadult = os.path.join(cache_dir, 'extras.json')
    
    exp_token = 60 * 60
    exp_iptv = 60 * 60
    exp_vod = 24 * 60 * 60
    
    

def cache_refresh(auth, fcache, exp):

    mac, id, pw, token = auth
    
    try:
        if not fileExpired(fcache, exp):
            with open(fcache, 'r') as f: cache = f.read()
            prev = '/movie/.*?/.*?/'
            new = '/movie/'+id+'/'+pw+'/'
            cache = re.sub(prev, new, cache)
            with open(fcache, 'w') as f: f.write(cache)
            cache = json.loads(cache)
            return cache
        else:
            return None
    except:
        return None

    

def is_valid(f, exp):

    valid = not fileExpired(fkey, exp_token)
    if valid and f: valid = not fileExpired(f, exp)
    
    return valid
    
    
    

def retrieve_data(vars):
    import urlparse

    headers = { 
        'Host' : server,
        'User-Agent' : userAgent, 
        'Cookie' : 'mac=' + mac + '; stb_lang=en; timezone=' + timezone,
        'Referer' : portal_ref,
        'Accept-Charset' : 'UTF-8,*;q=0.8',
        'Connection' : 'Keep-Alive',
        'X-User-Agent' : 'Model: MAG250; Link: WiFi'
    }
    
    try: headers['Authorization'] = 'Bearer ' + key
    except: pass
    
    try: params = vars + ''
    except: params = urllib.urlencode(vars)
    
    args = urlparse.parse_qs(params)
    
    try:
        if mac_based and args['action'][0] == 'do_auth':
            return xcurl(portal_url, args, headers)
    except:
        pass
    
    limit = 2
    
    for tries in range(0, limit):
        try:
            req = urllib2.Request(portal_url, params, headers)
            info = urllib2.urlopen(req).read()
            info = json.loads(info)
            if (info["js"] != None): return info
        except:
            pass

    return None
    

def handshake():
    global key
    global acc_ok
    
    if is_valid(None, None):
        with open(fkey) as f: mac_ref, login, pw, key = json.load(f)
        if (mac == mac_ref) and (donation == login): return [mac_ref, login, pw, key]
    
    getToken()
    info = getProfile()
    info = getAuth(info)
    #watchdog()
    
    if info:
        id, pw = info
        info = [mac, id, pw, key]
        js = json.dumps(info)
        with open(fkey, 'w') as f: f.write(js)
    
    else:
        alert('[COLOR red]ERROR:[/COLOR]\n\nINVALID  LOGIN')
        clear_caches(refreshed=False, silent=True)
        acc_ok = False
    
    return info
    



def getToken():
    global key
    
    params = 'type=stb&action=handshake'
    
    info = retrieve_data(params)
        
    key = info['js']['token']
    
    clear_caches(refreshed=False, silent=True)
    
    return key
    
    

def get_SN():
    import hashlib

    sn = hashlib.md5(mac).hexdigest().upper()[13:]
    dev1 = hashlib.sha256(sn).hexdigest().upper()
    dev2 = hashlib.sha256(mac).hexdigest().upper()
    sig = hashlib.sha256(sn + mac).hexdigest().upper()
    
    return [sn, dev1, dev2, sig]


    
    
def getAuth(info):

    if not info: return None
    
    sn, dev1, dev2, sig = get_SN()
    auth = [mac, donation, key]
    
    vars = {
        'type' : 'stb', 
        'action' : 'do_auth',
        'auth' : json.dumps(auth),
        'JsHttpRequest' : '1-xml',
        'info' : json.dumps(info),
        'sn' : sn,
        'device_id' : dev1,
        'device_id2' : dev2,
        'signature' : sig
    }
        
    info = retrieve_data(vars);
    
    return info;

    
    
def getProfile():

    params = 'type=stb&action=get_profile&stb_type=MAG250&sn=0000000000000&ver=ImageDescription%3a%200.2.16-250%3b%20ImageDate%3a%2018%20Mar%202013%2019%3a56%3a53%20GMT%2b0200%3b%20PORTAL%20version%3a%204.9.9%3b%20API%20Version%3a%20JS%20API%20version%3a%20328%3b%20STB%20API%20version%3a%20134%3b%20Player%20Engine%20version%3a%200x566&not_valid_token=0&auth_second_step=0&hd=1&num_banks=1&image_version=216&hw_version=1.7-BD-00'
    
    info = retrieve_data(params)
    
    return info

    
    
def watchdog():
    
    params = 'type=watchdog&action=get_events&init=0&cur_play_type=1&event_active_id=0'
    
    info = retrieve_data(params)

    return info

    
    
def get_genres():

    if not acc_ok: return None

    if not mac_based:
#        acc = [donation, donation, server]
        genres, channels, vod, adult = m3u_read(fgenre, fchannel, fvod, fadult)
        return genres

    if is_valid(fgenre, exp_iptv):
        with open(fgenre) as f: genres = json.load(f)
        return genres
        
    ok = handshake()
    if not ok: return None
    
    params = 'type=itv&action=get_genres'
    
    try: info = retrieve_data(params)['js']
    except: info = None
    
    if not info: return None

    genres = sorted([[i['title'], i['id']] for i in info])
    
    js = json.dumps(genres)
    with open(fgenre, 'w') as f: f.write(js)
    
    return genres

    
    
def get_channels():

    if not acc_ok: return None

    if not mac_based:
        acc = [donation, donation, server]
        genres, channels, vod, adult = m3u_read(fgenre, fchannel, fvod, fadult)
        return channels

    if is_valid(fchannel, exp_iptv):
        with open(fchannel) as f: channels = json.load(f)
        return channels

    ok = handshake()
    if not ok: return None
    
    params = 'type=itv&action=get_all_channels'
    
    try: data = retrieve_data(params)['js']['data']
    except: data = None
    
    if not data: return None
    
    data = iptv_obj(data)
    
    for genre in ['3', '13']:
        data += get_extra(genre)
    
    js = json.dumps(data)
    with open(fchannel, 'w') as f: f.write(js)
    
    try: m3u_create()
    except Exception as e:
        alert(str(e))
    
    return data
    
    

def iptv_obj(data):

    channels = []

    for i in data:
        id = int(i["id"])
        num = int(i["number"])
        name = i["name"]
        icon = i["logo"]
        cat = i["tv_genre_id"]
        url = i["cmd"]
        tmp = i["use_http_tmp_link"]
        
        channels.append([num, name, id, cat, icon, url, tmp])
        
    return sorted(channels)
    
    

def get_extra(genre):

    ok = handshake()
    if not ok: return None
    
    extra = []
    
    for page in range(1, 666):
    
        params = 'p='+str(page)+'&genre='+str(genre)+'&fav=0&JsHttpRequest=1-xml&action=get_ordered_list&type=itv'
    
        try: info = retrieve_data(params)['js']
        except: info = None
        
        if not info: continue
        
        if page == 1:
            max_pages = get_pages(info)
            if max_pages < page: break

        data = info['data']
        
        extra += iptv_obj(data)
        
        if (page == max_pages): break
        
    return extra
    
    
    
def get_pages(info):
    
    try:
        total_items = float(info['total_items']);
        max_page_items = float(info['max_page_items']);
        max_pages = -(-total_items // max_page_items)
    except:
        max_pages = 1
    
    return max_pages
    
    

def get_vod():

    if not acc_ok: return None

    if not mac_based:
        acc = [donation, donation, server]
        genres, channels, vod, adult = m3u_read(fvod_genre, fchannel, fvod, fadult)
        return vod

    if not fileExpired(fvod, exp_token):
        with open(fvod) as f: vod = json.load(f)
        return vod

    start = 1
    max_pages = 666

    auth = handshake()
    if not auth: return None
    
    vod = cache_refresh(auth, fvod, exp_vod)
    
    if vod: return vod
        
    vod = []
    genres = []
    
    progress = xbmcgui.DialogProgress()
    progress.create('Collecting  VOD  Data', 'Start downloading ...')
    
    for page in range(start, 1+vod_pages):
        
        percent = (100 * (1+page-start) / max_pages)
        msg = "Please wait ..." if page < max_pages else "Collecting DONE ..."
        progress.update( percent, "Collecting data from page #" + str(page) + ' / ' + str(int(max_pages)), '', msg)
        if progress.iscanceled(): return None
        
        params = 'p='+str(page)+'&not_ended=0&fav=0&sortby=added&action=get_ordered_list&type=vod&JsHttpRequest=1-xml'
        
        try: info = retrieve_data(params)['js']
        except: info = None
        
        if not info: continue
        
        if page == start:
            max_pages = get_pages(info)
            if max_pages < page: break

        result = info['data']
        
        for i in result:
            data = vod_obj(i, server)
            vod.append(data)
            try: genre = data[-1]['genre'].split(',')[0]
            except: genre = 'N/A'
            if genre not in genres: genres.append(genre)
            
        if (page == max_pages): break
        
    progress.close()
    
    for fcache, cache in [[fvod, vod], [fvod_genre, sorted(genres)]]:
        js = json.dumps(cache)
        with open(fcache, 'w') as f: f.write(js)
    
    return vod
        
        

def get_vod_genre():

    if not os.path.isfile(fvod_genre): vod = get_vod()
    
    with open(fvod_genre) as f: genres = json.load(f)
    
    return genres
        
        

def vod_obj(data, server):
    
    info = json.loads(base64.b64decode(data["cmd"]))
    
    title = info["movie_display_name"]
    icon = data["screenshot_url"]
    
    fname = info["movie_id"]
    ext = info["target_container"]
    id = info["username"]
    pwd = info["password"]
    url = 'http://'+server+'/movie:80/'+id+'/'+pwd+'/'+fname+'.'+ext
    
    meta = vod_meta(data)
    
    return [title, icon, url, meta]
        
        

def vod_meta(data):
    
    try:
        runtime = data["time"]
        if runtime and int(kodi[0]) >= 16: runtime = str(int(runtime) * 60)
        meta = {
            'title': data["name"],
            'year': data["year"].split()[0],
            'genre': data["genres_str"],
            'director': data["director"],
            'cast': data["actors"].split('/ '),
            'plot': data["description"],
            'originaltitle': data["o_name"],
            'duration': runtime
        }
    
    except:
        meta = None

    return meta

    

def get_link(url, tmp):

    if tmp == '0':
        url = url.split()[-1]
        return url

    ok = handshake()
    if not ok: return None
    
    vars = {
        'type' : 'itv' if int(tmp) > 0 else 'vod', 
        'action' : 'create_link',
        'cmd' : url,
        'JsHttpRequest' : '1-xml'
    }
    
    try: url = retrieve_data(vars)['js']['cmd']
    except: url = None
    
    return url
    
    

def get_url(channel):

    if channel.startswith('*'):
        channel = get_extra_url(channel[1:])
    
    if not channel: return None
    
    try: channels = get_channels()
    except: return None
    
    try: url, tmp = [[url, tmp] for ch_num, name, id, cat, icon, url, tmp in channels if channel == name][0]
    except: url = None
    
    if url: url = get_link(url, tmp)
    
    return url
    
    

def get_extra_url(channel):
    from config import key_passed

    if channel.startswith('?'):
        if not key_passed(silent=True): return None
        channel = channel[1:]
        
    return channel
    
    

def get_language(lang_filtered):

    if lang_filtered:
        langs = ['ENGLISH', 'FOREIGN', 'ALL']
        language = xbmcgui.Dialog().select('Preferred  Language?', langs)
        if language < 0: return -1
        language = langs[language].lower()
    else:
        language = 'all'
    
    return language
    
    

def language_valid(lang, ch_num, foreign, type):

    if type == 'tv':
        valid = (lang == 'all') or (lang == 'english' and int(ch_num) < int(foreign)) or (lang != 'english' and int(ch_num) >= int(foreign))
    elif type == 'vod':
        valid = (lang == 'all') or (lang == 'english' and foreign not in ch_num) or (lang != 'english' and foreign in ch_num)
    
    return valid
    
    

def get_genre(genre_filtered):
    
    try:
        if genre_filtered:
            genres = ['ALL'] + get_vod_genre()
            genre = xbmcgui.Dialog().select('Preferred  Genre?', genres)
            if genre < 0: return
            genre = genres[genre]
        else:
            genre = 'ALL'
    except:
        genre = 'ALL'
        
    return genre
    
    

def clear_caches(refreshed, silent):

    xfiles = [fvod]

    try:
        files = [f for f in os.listdir(cache_dir) if (cache_dir+f not in xfiles)]
        for f in files:
            os.remove(cache_dir+f)
        
        if refreshed:
            ok = (xbmcgui.Dialog().yesno('Clear: Caches', '\n', '\n', 'Do you also want to generate a new token ?') > 0)
            if ok:
                dummy = get_genres()
                dummy = get_channels()
        
        if not silent: notify('IPTV', '[COLOR lime]Process:  DONE![/COLOR]', icon='DefaultIconInfo.png', sec=3)
    
    except Exception as e:
        if not silent: notify('[COLOR red]Clear Caches:  FAIL![/COLOR]', str(e), icon='DefaultIconError.png', sec=3)

    


def search_channel(ch_name):

    channels = get_channels()
    
    alias = [ch_name] if ' HD' in ch_name else [ch_name, ch_name+' HD']
    
    try: result = [[name, icon, url, tmp] for num, name, id, cat, icon, url, tmp in channels if name in alias][0]
    except: result = None
    
    return result
    

    

######################### MAIN #########################



init()    
    