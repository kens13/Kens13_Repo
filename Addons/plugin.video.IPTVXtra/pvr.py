# -*- coding: utf-8 -*-



import xbmc, xbmcaddon, xbmcgui, xbmcplugin
import os, sys, json, urllib, urllib2

from tools import addon_init
from tools import alert, notify

from stalker import cache_dir, fgenre, fchannel


reload(sys)
sys.setdefaultencoding('utf8')

    

def dir_init():
    global addon, addonname, data_dir, alldir
    global user_dir, addon_dir, resource_dir

    info = addon_init()
    [addon, addonname, data_dir], info = info
    addon_dir = data_dir.replace('userdata/addon_data', 'addons')
    user_dir = data_dir.split('addon_data')[0]
    alldir = user_dir.replace('/userdata', '/addons')
    resource_dir = os.path.join(addon_dir, 'resources/')
    
    return info
    


def init():
    global userAgent
    global gmt_zone, gmt, gmt_hour
    global epg_sources, epg_src

    dir_init()
    
    try: gmt_zone, gmt, gmt_hour = addon.getSetting("tzone").split(' | ')
    except: gmt_zone, gmt, gmt_hour = [None, None, None]
    
    epg_sources = [
        'https://raw.githubusercontent.com/kens13/EPG/master/guide_kens.xml',
        'https://raw.githubusercontent.com/kens13/EPG/master/guide_ks.xml'
    ]
    
    epg_src = addon.getSetting("epg_src")

    
    
    
def epg_init():
    
    epg_src = ''
    epgs = ['EPG  by:  Kens', 'EPG  by:  Kens', '[COLOR yellow]C U S T O M[/COLOR]']
    epg = xbmcgui.Dialog().select('Preferred  EPG  Source ?', epgs)
    if epg < 0: return -1
    elif epg == len(epgs)-1:
        while not (epg_src and any (item in epg_src for item in [':', '.'])):
            epg_src = xbmcgui.Dialog().input('Your Custom EPG Source ?')
            if not epg_src: return -1
    else:
        epg_src = epg_sources[epg]
    
    addon.setSetting(id='epg_src', value=epg_src)
    
    return epg_src
    
    
    
    
def settings_init():
    global pvr_ref
    global epg_src

    pvrs = ['PVR  IPTV  Simple  Client', 'Stalker  Client']
    '''
    pvr = xbmcgui.Dialog().select('Preferred  PVR  Client ?', pvrs)
    if pvr < 0: return
    '''
    pvr = 0
    pvr_ref = ['simple', 'stalker'][pvr]
    
    f = {'simple': simple_settings, 'stalker': stalker_settings}
    
    f[pvr_ref](epg_src)
    
    


def simple_settings(epg):
    import xml.etree.ElementTree as ET
    from stalker import fm3u
    
    pvr_dir = os.path.join(user_dir, 'addon_data/pvr.iptvsimple/')
    if not os.path.isdir(pvr_dir): os.mkdir(pvr_dir)
    fpvr = os.path.join(pvr_dir, 'settings.xml')
    
    m3u_src, m3u_type, m3u_id = [fm3u, '0', 'm3uPath']
    
    xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "Addons.SetAddonEnabled", "params": { "addonid": "pvr.iptvsimple", "enabled": false }, "id": 1 }')

    try:
        with open(fpvr, 'r') as f: xml = f.read()
    except:
        return
        
    root = ET.fromstring(xml)
    tags = root.findall("setting")
    
    settings = {
            m3u_id:m3u_src, 'epgUrl':epg, 'epgTimeShift':str(gmt_hour), 'epgTSOverride':'true',
            'm3uPathType':m3u_type, 'epgPathType':'1', 'm3uCache':'false', 'epgCache':'false'
    }
    
    for i in tags:
        if i.attrib['id'] in settings: i.attrib['value'] = settings[i.attrib['id']]
    
    xml = ET.tostring(root).replace("><", ">\n<")
    with open(fpvr, 'w') as f: f.write(xml)
    
    notify('[COLOR orange]PVR Client[/COLOR]', '[COLOR lime]Auto Settings:  DONE![/COLOR]', icon='DefaultIconInfo.png', sec=2)
    xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "Addons.SetAddonEnabled", "params": { "addonid": "pvr.iptvsimple", "enabled": true }, "id": 1 }')

    
    
def stalker_settings(epg):

    alert(epg)

    

######################### MAIN #########################



init()    
