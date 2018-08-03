# -*- coding: utf-8 -*-


import xbmc, xbmcaddon, xbmcgui, xbmcplugin
import os, sys, json, urllib, urllib2, base64

from config import mac_based, token_type

from tools import addondir
from tools import get_string
from tools import fileExpired

reload(sys)
sys.setdefaultencoding('utf8')



def m3u_create():
    
    from pvr import epg_sources, epg_src
    from tools import get_localhost

    from stalker import get_genres, get_channels
    from stalker import fm3u, fadult
    
    from config import adult_ok, is_protected, key_passed

    try:
        epg_ref = epg_sources.index(epg_src)
        url = [
            'https://raw.githubusercontent.com/kens13/EPG/master/stalker_grouptest.json',
            'https://raw.githubusercontent.com/kens13/EPG/master/stalker_grouptest.json'
        ][epg_ref]
    
    except:
        url = None
    
    try: epg = json.loads(urllib2.urlopen(url).read())
    except: epg = {}
    
    genres = get_genres()
    channels = get_channels()
    
    cats = {}
    for genre, id in genres:
        cats[id] = genre
        
    ip, port, host = get_localhost()
        
    m3u = '#EXTM3U\n\n#EXTINF:-1 tvg-id="00411" tvg-chno="1" tvg-name="Information" tvg-logo="https://raw.githubusercontent.com/kens13/EPG/master/info.png" group-title="Information",Information \nhttps://raw.githubusercontent.com/kens13/EPG/master/test_pattern_1.mp4\n\n'
    
    adult = ''
    
    #link_type = token_type if mac_based else 0
    #link_type = token_type
    link_type = 1 if adult_ok and is_protected else (token_type if mac_based else 0)
    
    for ch_num, name, id, cat, icon, url, tmp in channels:
        name = name.encode("utf-8")
        alias = name.replace(' ', ' ')
        
        is_adult = any (item in cat.lower() for item in ['adult', '13'])
        
        ch_name = '*?'+name if is_adult and adult_ok and is_protected else name
        ch_title = '[COLOR yellow]'+name+'[/COLOR]' if is_adult and adult_ok else name
        
        link = [
            url.split()[-1],
            host+'/play?channel='+urllib.quote_plus(ch_name)
        ]
        
        try: epg_id = epg[name]
        except: epg_id = ''
        
        line = '#EXTINF:-1 tvg-id="" tvg-name="'+alias+'" tvg-logo="'+icon+'" group-title="'+epg_id+'", '+ch_title+'\n'
        line += link[link_type] + '\n\n'
        
        if is_adult: adult += line
        else: m3u += line
    
    if adult_ok: m3u += adult
    
    with open(fm3u, 'w') as f: f.write(m3u)
    
    return fm3u
    
    
    

def m3u_read(fcat, fchannel, fvod, fadult):
    from stalker import exp_iptv
    from config import foreign_channel, foreign_ch_num, donation, server

    acc = [donation, donation, server]
    
    if not fileExpired(fchannel, exp_iptv):
        all_caches = []
        try:
            for fcache in [fcat, fchannel, fvod, fadult]:
                with open(fcache, 'r') as f: cache = f.read()
                valid = all (item in cache for item in acc) or (fcache == fcat)
                if not valid: valid = 1 / 0
                all_caches.append(json.loads(cache))
            return all_caches
        except:
            pass

    url = 'http://'+server+':80/get.php?username='+donation+'&password='+donation+'&type=m3u_plus&output=ts'

    try:
        req = urllib2.Request(url)
        req.add_header('User-Agent' , "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.155 Safari/537.36")
        response = urllib2.urlopen(req)
        M3U=response.read()
#        SaveFile(m3uFile, link)
        response.close()
#        return link
#        M3U = urllib2.urlopen(url).read()
    except:
        M3U = None
        
    if not M3U: return [None, None, None]
    
    try: data = M3U.split('#EXTINF:')[1:]
    except: data = None
    
    if not data: return [None, None, None]
    
    tmp = '0'
    num = 0
    meta = None
    cats = []
    channels = []
    vod = []
    adult = []
    
    for i in data:
        i = ' '.join(i.split())
        if not i: continue
        
        url = i.split()[-1]
        name = ' '.join(','.join(i.split(',')[1:]).replace(url, '').split())
#        name = name.replace('.', '')
        name = name.replace('?', '')
#        name = name.replace("'", '')
        name = name.replace('#', ' ')
        name = name.replace(':', '-')
#        name = name.replace(']', '')
#        name = name.replace('[', '')

        if (name == foreign_channel): num = foreign_ch_num
        else: num += 1
        
        try: icon = get_string('tvg-logo="', '"', i)[0]
        except: icon = ''
        
        try: id = int(icon.split('/')[-1].split('.')[0])
        except: id = num
        
        try: cat = get_string('group-title="', '"', i)[0] 
        except: cat = None
        if not cat: cat = 'Uncategorized'
        
        if ('/movie/' in url.lower()) and (cat.lower() == 'for adults'):
            adult.append([name, icon, url, cat])
        elif ('/movie/' in url.lower()) and (cat.lower() != 'for adults'):
            vod.append([name, icon, url, cat])
        else:
            channels.append([num, name, id, cat, icon, url, tmp])
            if cat not in cats: cats.append(cat)
        
    cats = [["All", "*"]]+[[cat, cat] for cat in sorted(cats)]
    
    caches = [[cats,fcat], [channels,fchannel], [vod, fvod], [adult, fadult]]
    for cache, fcache in caches:
        js = json.dumps(cache)
        with open(fcache, 'w') as f: f.write(js)
    
    m3u_create()
    
    return [cats, channels, vod, adult]
