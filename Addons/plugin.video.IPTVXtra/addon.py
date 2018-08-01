# -*- coding: utf-8 -*-


import xbmc, xbmcaddon, xbmcgui, xbmcplugin
import os, sys, json, urllib, urllib2

from tools import alert, notify
from tools import add_item
from tools import window_open, view_mode

import stalker
from stalker import dir_init

import config
from config import adult_ok, is_protected
from config import foreign_channel, foreign_ch_num

import pvr

reload(sys)
sys.setdefaultencoding('utf8')

    

def init():
    from config import dead_acc
    
    global addon, addonname
    global base_url, addon_handle, args, current_url, base_arg
    #global lang_filtered, foreign_channel, genre_filtered
    global lang_filtered, genre_filtered
    
    addon = xbmcaddon.Addon()
    addonname = addon.getAddonInfo('name')
    addon_info = dir_init()

    base_url, addon_handle, args, current_url, base_arg = addon_info
    
    lang_filtered = (addon.getSetting("filter_lang") == 'true')
    #foreign_channel = 640
    
    genre_filtered = (addon.getSetting("filter_genre") == 'true')
    
    xbmcplugin.setContent(addon_handle, 'movies')
    
    return True

    

def home():

    items = [['IPTV'], ['VOD'], ['*Clear:  Caches', 'clear'], ['Auto-Setup:  PVR  Simple  Client', 'pvr'], ['Generate VOD STRM Files', 'recording'], ['Open IPTVXtra Settings', 'settings']]
    
    for item in items:
        try: item, mode = item
        except: item, mode = [item[0], item[0].lower()]
        cmd = [None, {'mode':mode}]
        add_item(item, cmd, icon=None, menus=None, meta=None, last=False)
    
    xbmcplugin.endOfDirectory(addon_handle)
    
    

def show_tv():

    try: genres = stalker.get_genres()
    except: genres = None
    
    if not genres: return
        
    opt = [genre for genre, id in genres if adult_ok or 'adult' not in genre.lower()]
    genre = xbmcgui.Dialog().select('Preferred  Genre?', opt)
    if genre < 0: return
    
    cat = [id for name,id in genres if name == opt[genre]][0]
    
    cmd = [None, {'mode':'channel', 'cat':cat}]
    window_open(cmd)

    

def show_channels():
    from tools import no_video
        
    try: cat_ref = args['cat'][0]
    except: cat_ref = '*'
    
    if adult_ok and any (item in cat_ref.lower() for item in ['adult', '13']) and is_protected and not config.key_passed(silent=True):
        data = ["Playboy TV Latin America", "http://content.iptvprivateserver.tv:88/stalker_portal/misc/logos/240/3636.png", no_video(), '0']
        cmd = [None, {'mode':'play', 'data':json.dumps(data)}]
        window_open(cmd)
        return

    language = stalker.get_language(lang_filtered)
    if language == -1: return

    try: data = stalker.get_channels()
    except: data = None
    
    if not data: return
    
    exist = False
    
    for ch_num, name, id, cat, icon, url, tmp in  data:
        if not stalker.language_valid(language, ch_num, foreign_ch_num, type='tv'): continue
        if not cat_ref in ['*', cat]: continue
        if (cat_ref == '*') and any (item in cat.lower() for item in ['adult', '13']):
            if not (adult_ok and not is_protected): continue
        info = json.dumps([name, icon, url, tmp])
        cmd = [None, {'mode':'play', 'data':info}]
        add_item(name, cmd, icon, menus=None, meta=None, last=False)
        exist = True
    
    #view_mode(500)
    if exist: xbmcplugin.endOfDirectory(addon_handle)
    
    
    
def show_vod():

    language = stalker.get_language(lang_filtered)
    if language == -1: return
    
    genre = stalker.get_genre(genre_filtered)
    
    try: data = stalker.get_vod()
    except Exception as e:
        alert('ERROR: VOD\n'+str(e))
        data = None
    
    if not data: return
    
    for name, icon, url, meta in data:
        if not stalker.language_valid(language, name, ' (ES)', type='vod'): continue
        try:
            if genre not in ['ALL', meta['genre'].split(',')[0]]: continue
        except:
            pass
        info = json.dumps([name, icon, url, '0'])
        cmd = [None, {'mode':'play', 'data':info}]
        add_item(name, cmd, icon, menus=None, meta=meta, last=False)
    
    #if meta: view_mode(508)
    #else: view_mode(500)
    
    xbmcplugin.endOfDirectory(addon_handle)
    
    


def search_channel():

    try: name = args['name'][0]
    except: name = None
    if not name: return
    
    info = stalker.search_channel(name)
    if not info: return
    
    info = json.dumps(info)
    cmd = [None, {'mode':'play', 'data':info}]
    
    window_open(cmd)
    
    
def record_channel():
    
    ############## removed ##############
    
    alert("SORRY!\n\nThis version does not have the .strm feature")



def settings():

    xbmcaddon.Addon('plugin.video.IPTVXtra').openSettings()
            
    
def play_video():
    from tools import header_ua, redirect, pipeURL

    try: name, icon, url, tmp = json.loads(args['data'][0])
    except: url = None
    
    if not url: return
    
    try: url = stalker.get_link(url, tmp)
    except: url = None
    
    if not url: return
    
    try:
        url = pipeURL(redirect(url, header_ua))
    
        li = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=icon)
        li.setInfo('video', {'Title': name})
    
        xbmc.Player().play(item=url, listitem=li)
    
    except Exception as e:
        alert('PLAY  ERROR:\n\n'+str(e))



def run_server():
    import server

    try: action = args['action'][0]
    except: return
    
    if action != 'check':
        dp = xbmcgui.DialogProgressBG()
        dp.create('M3U Server', 'Working ...')
    
    server.run(action)
    
    if action != 'check': dp.close()
    
    

def mode_set():
    
    mode = args.get('mode', None)
    
    if mode is None: home()
    elif mode[0] == 'iptv': show_tv()
    elif mode[0] == 'channel': show_channels()
    elif mode[0] == 'play': play_video()
    elif mode[0] == 'vod': show_vod()
    elif mode[0] == 'search': search_channel()
    
    elif mode[0] == 'portal': config.portal_set()
    elif mode[0] == 'mac_prefix': config.mac_prefix_set()
    elif mode[0] == 'timezone': config.set_timezone()
    
    elif mode[0] == 'clear': stalker.clear_caches(refreshed=True, silent=False)
    
    elif mode[0] == 'pvr': pvr.settings_init()
    elif mode[0] == 'epg_init': pvr.epg_init()
    
    elif mode[0] == 'server': run_server()
    
    elif mode[0] == 'password_set': config.password_set()
    elif mode[0] == 'adult_set': config.adult_set()
    
    elif mode[0] == 'recording': record_channel()

    elif mode[0] == 'settings': settings()    
#    elif mode[0] == 'recording': record_channel()

def main():

    ok = init()
    
    if ok: mode_set()




######################### MAIN #########################



main()




