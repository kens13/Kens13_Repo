import xbmc, xbmcaddon, xbmcgui, xbmcplugin
import os, urllib, urllib2, json

from tools import curl, header_ua, alert
from tools import hashText
from tools import addondir



def init():
    global addon
    global mac_based
    global dead_acc
    global fconfig
    global foreign_channel, foreign_ch_num
    
    addon = xbmcaddon.Addon()
    
    adult_init()
    
    stalker_init()
    
    mac_based = account_check()
    
    dead_acc = (mac.startswith('00:00:00') and mac_based)
    
    fconfig = os.path.join(addondir, 'config.json')
    
    foreign_channel = "Murcia TV 7"
    foreign_ch_num = 640 if mac_based else 5000
    

def adult_init():
    global adult_ok, is_protected, adult_key

    adult_ok = ('no' in addon.getSetting("adult_hide").lower())
    is_protected = ('yes' in addon.getSetting("adult_protect").lower())
    adult_key = addon.getSetting("adult_key")
    
    
    
def key_passed(silent):
    
    key = xbmcgui.Dialog().input('Current  Password?', option=xbmcgui.ALPHANUM_HIDE_INPUT)
    if not key: return False
    
    passed = (hashText(key) == adult_key)
    if not (passed or silent): alert('WRONG  PASSWORD!')
    
    return passed


def password_set():

    key = xbmcgui.Dialog().input("New  Password?", option=xbmcgui.ALPHANUM_HIDE_INPUT)
    if not key: return
    
    addon.setSetting(id='adult_key', value=hashText(key))
    
    
def adult_set():

    if not key_passed(silent=False): return
    
    is_yes = {True:"[COLOR lime]YES[/COLOR]", False:"[COLOR red]NO[/COLOR]"}

    try:
        with open(fconfig) as f: configs = json.load(f)
    except:
        configs = {}
    
    tags = ['adult_hide', 'adult_protect']
    vals = {}
    for i in tags:
        try: vals[i] = configs[i]
        except: vals[i] = ('yes' in addon.getSetting(i).lower())
        
    opt1 = [{True:'[COLOR red]UN-HIDE:[/COLOR]  Adult Contents', False:'[COLOR lime]HIDE[/COLOR]:  Adult Contents'}[vals['adult_hide']]]
    opt2 = [{True:'[COLOR red]UN-PROTECT:[/COLOR]  Adult Contents', False:'[COLOR lime]PROTECT[/COLOR]:  Adult Contents'}[vals['adult_protect']]]
    opt3 = ['[COLOR yellow]Change  Password[/COLOR]']
    
    opt = opt1 if vals['adult_hide'] else opt1 + opt2 + opt3
    
    act = xbmcgui.Dialog().select('Preferred  Action ?', opt)
    
    if act < 0: return
    
    elif act in [0, 1]:
        id = tags[act]
        configs[id] = not vals[id]
        addon.setSetting(id, value=is_yes[configs[id]])
        js = json.dumps(configs)
        with open(fconfig, 'w') as f: f.write(js)
        
    elif act == 2:
        password_set()
    

    
def stalker_init():
    global mac, donation, server
    global portal_url, portal_ref
    global vod_pages
    global token_type

    mac = addon.getSetting("mac_prefix") + ':' + addon.getSetting("mac_last")
    donation = addon.getSetting("donation")
    server = addon.getSetting("portal")
    
    portal_url = 'http://'+server+'/server/load.php'
    portal_ref = 'http://'+server+'/c/'
    
    vod_pages = int(addon.getSetting("vodpages"))
    
    if adult_ok and is_protected:
        addon.setSetting(id="link_ref", value="1")    
    
    token_type = int(addon.getSetting("link_ref"))
    
    
    
def all_portals():

    default = [
        'p1.iptvrocket.tv',
        's1.iptv66.tv',
        'p1.iptvprivateserver.tv',
    ]
    
    addon_dir = addondir.replace('userdata/addon_data', 'addons')
    resource_dir = os.path.join(addon_dir, 'resources/')
    fportals = os.path.join(resource_dir,'portals.list')
    portals = []
    try:
        with open(fportals, 'r') as f: data = f.read()
        data = data.split('\n')
        for portal in data:
            portal = ' '.join(portal.split())
            if '.' in str(portal): portals.append(portal)
    except:
        pass
        
    if not portals: portals = default[:]
    
    return portals



def portal_set():

    portals = all_portals()
    
    portals.append('[COLOR yellow]C U S T O M[/COLOR]')
    portal = xbmcgui.Dialog().select('Select your Server/Portal URL', portals)
    
    if portal < 0: return
    
    elif (portal == len(portals)-1):
        while (portal and '.' not in str(portal)):
            portal = xbmcgui.Dialog().input('Enter Custom Server URL')
        if not portal: return
        try: portal = portal.split('/')[2]
        except: pass
    
    else: portal = portals[portal]
    
    addon.setSetting(id='portal', value=portal)
    

def mac_prefix_set():

    prefix = ['00:1A:78', '00:1A:79', '00:00:00', '[COLOR yellow]C U S T O M[/COLOR]']
    head = xbmcgui.Dialog().select('MAC Prefix?', prefix)
    
    if head < 0: return
    
    elif (head == len(prefix)-1):
        while (head and str(head).count(':') != 2):
            head = xbmcgui.Dialog().input('Custom MAC Prefix?')
        if not head: return
        head = head.replace(' ', '')
    
    else: head = prefix[head]
    
    addon.setSetting(id='mac_prefix', value=head)
    
    if head == '00:00:00':
        addon.setSetting(id='mac_last', value=head)
        
        

def tz_offset(region):

    url  = 'http://m28ew.atwebpages.com/tz.php?'
    url += urllib.urlencode({'region' : region})
    data = urllib2.urlopen(url).read().split('<br>')
    
    return {'offset':data[0], 'gmt':data[1]}




def set_timezone():
    global local_timezone
    
    url = 'http://pastebin.com/raw/Qk4KrwJ5'
    data = json.loads(urllib2.urlopen(url).read())
    
    regions = sorted(data.keys())
    reg = xbmcgui.Dialog().select("[TIMEZONE]  Group", regions)
    if reg < 0: return
    reg = regions[reg]
    
    cities = sorted(data[reg])
    tz = xbmcgui.Dialog().select("[TIMEZONE]  Region", cities)
    if tz < 0: return
    
    ofs = ' | '.join(tz_offset(cities[tz]).values())
    local_timezone = cities[tz] + ' | ' + ofs
    
    addon.setSetting(id='tzone', value=local_timezone)
    
    return local_timezone.split(' | ')




def account_check():

    if not donation: return True
    
    url = 'http://'+server+'/player_api.php?username='+donation+'&password='+donation
    
    try:
        data = curl(url, '', header_ua)
        mac_based = (data["user_info"]["auth"] != 1)
    except:
        mac_based = True
    
    return mac_based
    

######################### MAIN #########################

    
        
init()

