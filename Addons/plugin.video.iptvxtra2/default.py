 #############Imports#############
import xbmc,xbmcaddon,xbmcgui,xbmcplugin,xbmcvfs,base64,os,re,unicodedata,requests,time,string,sys,urllib,urllib2,json,urlparse,datetime,zipfile,shutil
from resources.modules import client,control,tools,user,help
from datetime import date
import xml.etree.ElementTree as ElementTree


#################################

#############Defined Strings#############
icon         = xbmc.translatePath(os.path.join('special://home/addons/' + user.id, 'icon.png'))
fanart       = xbmc.translatePath(os.path.join('special://home/addons/' + user.id , 'fanart.jpg'))

icon_set     = xbmc.translatePath(os.path.join('special://home/addons/' + user.id + '/resources/images', 'icon_settings.png'))
icon_extr    = xbmc.translatePath(os.path.join('special://home/addons/' + user.id + '/resources/images', 'icon_extras.png'))
icon_help    = xbmc.translatePath(os.path.join('special://home/addons/' + user.id + '/resources/images', 'icon_help.png'))
icon_pvr     = xbmc.translatePath(os.path.join('special://home/addons/' + user.id + '/resources/images', 'icon_pvr.png'))
icon_vod     = xbmc.translatePath(os.path.join('special://home/addons/' + user.id + '/resources/images', 'icon_vod.png'))
icon_tool    = xbmc.translatePath(os.path.join('special://home/addons/' + user.id + '/resources/images', 'icon_tools.png'))

fan_set      = xbmc.translatePath(os.path.join('special://home/addons/' + user.id + '/resources/images', 'settings.jpg'))
fan_extr     = xbmc.translatePath(os.path.join('special://home/addons/' + user.id + '/resources/images', 'addons.jpg'))
fan_help     = xbmc.translatePath(os.path.join('special://home/addons/' + user.id + '/resources/images', 'help.jpg'))
fan_pvr      = xbmc.translatePath(os.path.join('special://home/addons/' + user.id + '/resources/images', 'pvr.jpg'))
fan_vod      = xbmc.translatePath(os.path.join('special://home/addons/' + user.id + '/resources/images', 'vod.jpg'))
fan_acct     = xbmc.translatePath(os.path.join('special://home/addons/' + user.id + '/resources/images', 'account.jpg'))
fan_epg      = xbmc.translatePath(os.path.join('special://home/addons/' + user.id + '/resources/images', 'epg.jpg'))
fan_tv       = xbmc.translatePath(os.path.join('special://home/addons/' + user.id + '/resources/images', 'livetv.jpg'))
fan_srch     = xbmc.translatePath(os.path.join('special://home/addons/' + user.id + '/resources/images', 'search.jpg'))
fan_ppv      = xbmc.translatePath(os.path.join('special://home/addons/' + user.id + '/resources/images', 'ppv.jpg'))
help_set1    = xbmc.translatePath(os.path.join('special://home/addons/' + user.id + '/resources/images', 'set1.jpg'))

xml_skip    = xbmc.translatePath(os.path.join('special://home/addons/' + user.id + '/resources/advanced_settings', 'xmlid.txt'))

username     = control.setting('Username')
password     = control.setting('Password')
host         = control.setting('Server')

PEPGurl      =  host+':80/xmltv.php?username='+username+'&password='+password
live_url     = '%s:%s/enigma2.php?username=%s&password=%s&type=get_live_categories'%(host,user.port,username,password)
vod_url      = '%s:%s/enigma2.php?username=%s&password=%s&type=get_vod_categories'%(host,user.port,username,password)
panel_api    = '%s:%s/panel_api.php?username=%s&password=%s'%(host,user.port,username,password)
player_api   = '%s:%s/player_api.php?username=%s&password=%s&action=get_live_streams'%(host,user.port,username,password)
play_url     = '%s:%s/live/%s/%s/'%(host,user.port,username,password)
playvod_url     = '%s:%s/movie/%s/%s/'%(host,user.port,username,password)
vod_info   = '%s:%s/player_api.php?username=%s&password=%s&action=get_vod_info&vod_id='%(host,user.port,username,password)


basePath     = ('special://userdata/addon_data/'+user.id+'/')
basePath     = xbmc.translatePath(basePath)

strmPath = ('special://profile/addon_data/'+user.id+'/vodstrms/')
if not xbmcvfs.exists(strmPath):
    xbmcvfs.mkdir(strmPath)
strmPath = xbmc.translatePath(strmPath)

Guide = xbmc.translatePath(os.path.join('special://home/addons/addons/'+user.id+'/resources/catchup', 'guide.xml'))
GuideLoc = xbmc.translatePath(os.path.join('special://home/addons/addons/'+user.id+'/resources/catchup', 'g'))

advanced_settings           =  xbmc.translatePath('special://home/addons/'+user.id+'/resources/advanced_settings')
advanced_settings_target    =  xbmc.translatePath(os.path.join('special://home/userdata','advancedsettings.xml'))

explayer_home  =  xbmc.translatePath(os.path.join('special://home/userdata','playercorefactory.xml'))
mouse_home  =  xbmc.translatePath(os.path.join('special://home/userdata/keymaps','mouse.xml'))
KODIV        = float(xbmc.getInfoLabel("System.BuildVersion")[:4])
######################################

def buildcleanurl(url):
    url = str(url).replace('USERNAME',username).replace('PASSWORD',password)
    return url
def start():

    if username=="":
        mod = '1'
        usern = userpopup()
        passw = passpopup()
        portp = portpopup()
        control.setSetting('Username',usern)
        control.setSetting('Password',passw)
        control.setSetting('Server',portp)
#        xbmc.executebuiltin('Container.Refresh')
        addSrc()
        getchan()
        correctPVR('0')
        home()
    else:
        vodupdate()
        home()

def home():
    tools.addDir('PVR Setup & System Tools','url',16,'',icon_pvr,fan_pvr,'')
    if xbmc.getCondVisibility('System.HasAddon(pvr.iptvsimple)'):
        tools.addDir('LiveTV EPG Guide','pvr',7,'',icon,fan_pvr,'')
    tools.addDir('Video-on-Demand','vod',3,'',icon_vod,fan_vod,'')
    tools.addDir('Pay-per-View','url',5,'',icon_extr,fan_ppv,'')
    tools.addDir('Account Information','url',6,'',icon,fan_acct,'')
    tools.addDir('IPTVXtra2 Settings','url',8,'',icon_set,fan_set,'')
    tools.addDir('Help','url',19,'',icon_help,fan_help,'')
    tools.addDir('Quit KODI','url',21,'',icon,fanart,'')

def vodupdate():
    choice = xbmcgui.Dialog().yesno(user.name,'Would You like to Update the VOD/PPV or TV Items?', yeslabel = "Yes", nolabel = "No", autoclose=15000)
    if choice:
        updatecat()
    else:
        return

def updatecat():
    xbmc.executebuiltin('Dialog.Close(yesno, true)') 
    mod = '2'
    dialog = xbmcgui.Dialog().select('Select Update Categories', ['TV Channels (Requires Restart)','VOD and Pay-Per-View','All (Including EPG)'])
    if dialog==0:
        getchan()
        correctPVR('ch')
    elif dialog==1:
        vodproc()
    elif dialog==2:
        vodproc()
        getchan()
        if xbmcaddon.Addon(user.id).getSetting('epgmrg')=='true':
            mkEPG()
            correctPVR('1')
        else:
            correctPVR('2')
    else:
        return

def vodselect():
    cat = ''

    if (xbmcaddon.Addon().getSetting('hidexxx')=='true'):
        dialog = xbmcgui.Dialog().select('Select VOD Category', ['Movies','Classics','Peliculas','Clasicos','Foreign','TV Series','Series de TV','Pay-Per-View'])
    else:
        dialog = xbmcgui.Dialog().select('Select VOD Category', ['Movies','Classics','Peliculas','Clasicos','Foreign','TV Series','Series de TV','Pay-Per-View','For Adults'])
    if dialog==0:
        cat = '23'
    elif dialog==1:
        cat = '27'
    elif dialog==2:
        cat = '21'
    elif dialog==3:
        cat = '28'
    elif dialog==4:
        cat = '26'
    elif dialog==5:
        cat = '24'
    elif dialog==6:
        cat = '22'
    elif dialog==7:
        cat = 'ppv'
    elif dialog==8:
        cat = '25'
    else:
        home()
    readVod(cat)

def livecategory(url):
    
    open = tools.OPEN_URL(live_url)
    all_cats = tools.regex_get_all(open,'<channel>','</channel>')
    for a in all_cats:
        name = tools.regex_from_to(a,'<title>','</title>')
        name = base64.b64decode(name)
        cat = tools.regex_from_to(a,'<category_id>','</category_id>')
        url1  = tools.regex_from_to(a,'<playlist_url>','</playlist_url>').replace('<![CDATA[','').replace(']]>','')
        if (xbmcaddon.Addon().getSetting('hidexxx')=='true') and (cat == '13') or (cat == '25'):
            continue
        else:
            tools.addDir('%s'%name,url1,2,'',icon,fan_tv,'')
        
def Livelist(url):
    url  = buildcleanurl(url)
    open = tools.OPEN_URL(url)
    all_cats = tools.regex_get_all(open,'<channel>','</channel>')
    for a in all_cats:
        name = tools.regex_from_to(a,'<title>','</title>')
        name = base64.b64decode(name)
        xbmc.log(str(name))
        name = re.sub('\[.*?min ','-',name)
        thumb= tools.regex_from_to(a,'<desc_image>','</desc_image>').replace('<![CDATA[','').replace(']]>','')
        cat = tools.regex_from_to(a,'<category_id>','</category_id>')
        url1  = tools.regex_from_to(a,'<stream_url>','</stream_url>').replace('<![CDATA[','').replace(']]>','')
        desc = tools.regex_from_to(a,'<description>','</description>')
        if (xbmcaddon.Addon().getSetting('hidexxx')=='true') and (cat == '13') or (cat == '25'):
            continue
        else:
            tools.addDir(name,url1,4,'',thumb,fanart,base64.b64decode(desc))


def vod(url):

    if url =="vod":
        open = tools.OPEN_URL(vod_url)
    else:
        url  = buildcleanurl(url)
        open = tools.OPEN_URL(url)
    all_cats = tools.regex_get_all(open,'<channel>','</channel>')
    for a in all_cats:
        if '<playlist_url>' in open:
            name = tools.regex_from_to(a,'<title>','</title>')
            cat = tools.regex_from_to(a,'<category_id>','</category_id>')
            url1  = tools.regex_from_to(a,'<playlist_url>','</playlist_url>').replace('<![CDATA[','').replace(']]>','')
            if (xbmcaddon.Addon().getSetting('hidexxx')=='true') and (cat == '25'):
                continue
            tools.addDir(str(base64.b64decode(name)).replace('?',''),url1,3,'',icon,fan_vod,'')
        else:
            if xbmcaddon.Addon().getSetting('meta') == 'true':
                try:
                    name = tools.regex_from_to(a,'<title>','</title>')
                    name = base64.b64decode(name)
                    thumb= tools.regex_from_to(a,'<desc_image>','</desc_image>').replace('<![CDATA[','').replace(']]>','')
                    url  = tools.regex_from_to(a,'<stream_url>','</stream_url>').replace('<![CDATA[','').replace(']]>','')
                    vodID = tools.regex_from_to(url,('movie/'+username+'/'+password+'/'),'.mp4')
                    desc = tools.regex_from_to(a,'<description>','</description>')
                    desc = base64.b64decode(desc)
                    cat = tools.regex_from_to(a,'<category_id>','</category_id>')
                    plot = tools.regex_from_to(desc,'PLOT: ','\n')
                    runt = tools.regex_from_to(desc,'DURATION: ','\n')
                    genre= tools.regex_from_to(desc,'GENRE: ','\n')
                    year = tools.regex_from_to(desc,'RELEASEDATE: ','\n')
                    year = re.findall("\d+", year)[0]
                    ratin= tools.regex_from_to(desc,'RATING: ','\n')
                    cast = tools.regex_from_to(desc,'CAST: ','\n')
                    dir  = tools.regex_from_to(desc,'DIRECTOR: ','\n')
                    tools.addDirMeta(str(name).replace('[/COLOR][/B].','.[/COLOR][/B]'),url,4,thumb,fanart,plot,int(year),cast.split(", "),ratin,runt,genre,dir)
                    if (xbmcaddon.Addon().getSetting('vodStrm')=='true'):
                        makeStrm(name,url)
                except:pass
                xbmcplugin.setContent(int(sys.argv[1]), 'movies')
            else:
                name = tools.regex_from_to(a,'<title>','</title>')
                name = base64.b64decode(name)
                thumb= tools.regex_from_to(a,'<desc_image>','</desc_image>').replace('<![CDATA[','').replace(']]>','')
                url  = tools.regex_from_to(a,'<stream_url>','</stream_url>').replace('<![CDATA[','').replace(']]>','')
                desc = tools.regex_from_to(a,'<description>','</description>')
                tools.addDir(name,url,4,'',thumb,fanart,base64.b64decode(desc))

def vodproc():

    vod21 = '{\n'
    vod22 = '{\n'
    vod23 = '{\n'
    vod24 = '{\n'
    vod25 = '{\n'
    vod26 = '{\n'
    vod27 = '{\n'
    vod28 = '{\n'
    vodPPV = '{\n'

    top21 = xbmcaddon.Addon(user.id).getSetting(id='last21')
    top22 = xbmcaddon.Addon(user.id).getSetting(id='last22')
    top23 = xbmcaddon.Addon(user.id).getSetting(id='last23')
    top24 = xbmcaddon.Addon(user.id).getSetting(id='last24')
    top25 = xbmcaddon.Addon(user.id).getSetting(id='last25')
    top26 = xbmcaddon.Addon(user.id).getSetting(id='last26')
    top27 = xbmcaddon.Addon(user.id).getSetting(id='last27')
    top28 = xbmcaddon.Addon(user.id).getSetting(id='last28')

    itop21 = int(top21)
    itop22 = int(top22)
    itop23 = int(top23)
    itop24 = int(top24)
    itop25 = int(top25)
    itop26 = int(top26)
    itop27 = int(top27)
    itop28 = int(top28)

    hi21 = itop21
    hi22 = itop22
    hi23 = itop23
    hi24 = itop24
    hi25 = itop25
    hi26 = itop26
    hi27 = itop27
    hi28 = itop28

    open = tools.OPEN_URL(panel_api)
    all_chans = tools.regex_get_all(open,'{"num":',':0},')
    for a in all_chans:
        name = tools.regex_from_to(a,',"name":"','"')
        vodID = tools.regex_from_to(a,'stream_id":"','",')
        vid = int(vodID)
        thumb = tools.regex_from_to(a,'stream_icon":"','"').replace('\/','/')
        cat = tools.regex_from_to(a,'category_id":"','"')
        ds = tools.regex_from_to(a,'direct_source":"','"').replace('\/','/')

        if ('PPV' in name):
            try: name = re.split(" - ", name)[1]
            except: name = re.split("-", name)[1]
            cat = 'ppv'
            vodID = ds

        line = '["name":"'+name+'","stream_id":"'+vodID+'","stream_icon":"'+thumb+'","new":"'

        if (cat == '21'):
            if vid > itop21:
                new ='true'
                if vid > hi21:
                    hi21 = vid
            else:
                new ='false'
            vod21 += line+new+'"],\n'
        elif (cat == '22'):
            if vid > itop22:
                new ='true'
                if vid > hi22:
                    hi22 = vid
            else:
                new ='false'
            vod22 += line+new+'"],\n'
        elif (cat == '23'):
            if vid > itop23:
                new ='true'
                if vid > hi23:
                    hi23 = vid
            else:
                new ='false'
            vod23 += line+new+'"],\n'
        elif (cat == '24'):
            if vid > itop24:
                new ='true'
                if vid > hi24:
                    hi24 = vid
            else:
                new ='false'
            vod24 += line+new+'"],\n'
        elif (cat == '25'):
            if vid > itop25:
                new ='true'
                if vid > hi25:
                    hi25 = vid
            else:
                new ='false'
            vod25 += line+new+'"],\n'
        elif (cat == '26'):
            if vid > itop26:
                new ='true'
                if vid > hi26:
                    hi26 = vid
            else:
                new ='false'
            vod26 += line+new+'"],\n'
        elif (cat == '27'):
            if vid > itop27:
                new ='true'
                if vid > hi27:
                    hi27 = vid
            else:
                new ='false'
            vod27 += line+new+'"],\n'
        elif (cat == '28'):
            if vid > itop28:
                new ='true'
                if vid > hi28: 
                    hi28 = vid
            else:
                new ='false'
            vod28 += line+new+'"],\n'
        elif (cat == 'ppv'):
            new = 'false'
            vodPPV += line+new+'"],\n'

    xbmcaddon.Addon(user.id).setSetting(id='last21', value=str(hi21))
    xbmcaddon.Addon(user.id).setSetting(id='last22', value=str(hi22))
    xbmcaddon.Addon(user.id).setSetting(id='last23', value=str(hi23))
    xbmcaddon.Addon(user.id).setSetting(id='last24', value=str(hi24))
    xbmcaddon.Addon(user.id).setSetting(id='last25', value=str(hi25))
    xbmcaddon.Addon(user.id).setSetting(id='last26', value=str(hi26))
    xbmcaddon.Addon(user.id).setSetting(id='last27', value=str(hi27))
    xbmcaddon.Addon(user.id).setSetting(id='last28', value=str(hi28))

    saveVod(vod21,'21')
    saveVod(vod22,'22')
    saveVod(vod23,'23')
    saveVod(vod24,'24')
    saveVod(vod25,'25')
    saveVod(vod26,'26')
    saveVod(vod27,'27')
    saveVod(vod28,'28')
    saveVod(vodPPV,'ppv')

#    xbmcaddon.Addon(user.id).setSetting(id='lastid', value=top)
    xbmc.executebuiltin("Notification(IPTVXtra II,[I][COLOR lime]    . .*VOD & PPV Updated.[/COLOR][/I],3000)")

def vodinfo(name,url):

    ID = tools.regex_from_to(url,'movie/'+username+'/'+password+'/','.mp4')

    try:
        open = tools.OPEN_URL(vod_info+ID)

        duration_secs = tools.regex_from_to(open,'duration_secs":',',"')
        duration = tools.regex_from_to(open,'duration":"','",')
        genre = tools.regex_from_to(open,'"genre":"','",')
        thumb = tools.regex_from_to(open,'movie_image":"','",').replace('\/','/')
        releasedate = tools.regex_from_to(open,'releasedate":"','",')
        year = re.findall("\d+", releasedate)[0]
        cast = tools.regex_from_to(open,'"cast":"','",')
        dir = tools.regex_from_to(open,'"director":"','"')
        plot = tools.regex_from_to(open,'plot":"','",')
        name = tools.regex_from_to(open,'"name":"','",')
        date_added = tools.regex_from_to(open,'added":"','",')
        if not date_added=="":
            date_added = datetime.datetime.fromtimestamp(int(date_added)).strftime('%d/%m/%Y - %H:%M')
            expreg = re.compile('^(.*?)/(.*?)/(.*?)$',re.DOTALL).findall(date_added)
            for day,month,year in expreg:
                month = tools.MonthNumToName(month)
                year = re.sub(' -.*?$','',year)
                date_added = month+' '+day+' - '+year

        text = "[B]%s[/B]%s[CR][CR][B]%s[/B]%s[CR][CR][B]%s[/B]%s[CR][CR][B]%s[/B]%s[CR][CR][B]%s[/B]%s[CR][CR][B]%s[/B]%s[CR][CR][B]%s[/B]%s[CR]" % ('Genre:  ',genre,'Release Date:  ',releasedate,'Runtime:  ',duration,'Date Added:  ',date_added,'Cast:  ',cast,'Director:  ',dir,'Plot:  ',plot)
        xbmcgui.Dialog().textviewer(name, text)



    except:
        pass


#    dialog = xbmcgui.Dialog()
#    dialog.textviewer('Plot', 'Some movie plot.')

def getchan():

    chlist = '{'

    js = '{"5426": "50" , "6353": "42" , "7073": "45" , "7105": "2" , "7165": "7" , "7235": "12" , "7236": "25" , "7691": "47" , "7700": "4" , "7731": "9" , "7871": "23" , "7889": "30" , "8001": "20" , "8003": "43" , "8033": "38" , "8042": "5" , "8053": "28" , "8073": "59" , "8100": "10" , "8101": "22" , "8102": "68" , "8103": "48" , "8132": "69" , "8201": "17" , "8203": "37" , "8221": "24" , "8223": "54" , "8253": "27" , "8300": "3" , "8301": "15" , "8303": "26" , "8322": "11" , "8323": "49" , "8332": "62" , "8353": "33" , "8371": "18" , "8373": "40" , "8403": "36" , "8422": "71" , "8432": "66" , "8433": "41" , "8490": "6" , "8491": "16" , "8492": "60" , "8493": "32" , "8513": "34" , "8533": "52" , "8573": "46" , "8593": "55" , "8655": "31" , "8693": "56" , "8705": "13" , "8773": "29" , "8794": "53" , "8811": "14" , "8830": "8" , "8831": "21" , "8832": "67" , "8833": "44" , "8882": "65" , "8902": "63" , "8903": "39" , "8923": "58" , "8953": "57" , "9051": "19" , "9068": "35" , "9112": "61" , "9188": "70" , "9272": "64" , "9283": "51" , "9878": "78" , "9879": "79" , "9880": "80" , "9881": "81" , "9882": "82" , "9883": "83" , "9884": "84" , "9885": "85" , "9886": "86" , "9887": "87" , "9888": "88" , "9889": "89" , "9890": "90" , "9891": "91" , "9892": "92" , "9893": "93" , "9894": "94" , "9895": "95" , "9896": "96" , "9897": "97" , "9898": "98" , "9899": "99" , "9900": "100" , "9901": "101" , "9902": "102" , "9903": "103" , "9904": "104"}'
    url = "https://iptvprivateserver.is/templates/iptv-channels-table.php"
    try: conv = json.loads(js)
    except: conv = {}

    open = tools.OPEN_URL(url)
    all_chans = tools.regex_get_all(open,'<tr>','</tr>')
    for a in all_chans:
        chname = tools.regex_from_to(a,'21px;">','</div>')
        chno = tools.regex_from_to(a,'<td align="center">','</td>')
        group = tools.regex_from_to(a,'</td>\\n<td>','</td>\\n<td>')

        try: chno = conv[chno]
        except: chno = chno

        if chno != '9999':
            line = '"'+chname+'": "tvg-chno=\\"'+chno+'\\" group-title=\\"'+group+'" , '
        else:
            line = '"'+chname+'": "tvg-chno=\\"'+chno+'\\" group-title=\\"'+group+'"}'
        chlist += line

    saveCh(chlist)
#    m3uproc(chlist)

def mkEPG():
    xbmc.executebuiltin('Notification(IPTVXtra II,[I][COLOR yellow] . . .Downloading. .  . . .Processing EPG Channel Data  .  . . . *Please Wait . . . [/COLOR][/I],9000)')
    xEPGurl       = xbmcaddon.Addon(user.id).getSetting(id='xepgurl')
    epg = '<?xml version="1.0" encoding="utf-8" ?>\n<tv>\n'
    idlist = ''
    chanskip = ''

    fileObject = open(xml_skip,'r')
    chanskip = fileObject.read()
    fileObject.close()

    extepg = tools.OPEN_URL(xEPGurl)
    extdata =  tools.regex_from_to(extepg,'<?xml ','</tv>').replace('\r','')
    altdata1 = '<?xml '+extdata


    response = tools.OPEN_URL(PEPGurl)
    all_chns = tools.regex_get_all(response,'<channel ','</channel>')
    all_pgms = tools.regex_get_all(response,'<programme ','</programme>')
    for a in all_chns:
        if 'id="">' in a:
            continue
        elif 'id="NULL"' in a:
            continue
        chid = tools.regex_from_to(a,'id="','">')
        name = tools.regex_from_to(a,'<display-name>','</display-name>')
        icon = tools.regex_from_to(a,'<icon src="','" />')
        if name in chanskip:
            id = chid+', '
            idlist += id 
            continue
        line = '  <channel id="x'+chid+'">\n    <display-name>'+name+'</display-name>\n    <icon src="'+icon+'" />\n  </channel>\n'
        altdata1 += line

    for b in all_pgms:
        start = tools.regex_from_to(b,'start="','" ')
        stop = tools.regex_from_to(b,'stop="','" ')
        xmid = tools.regex_from_to(b,'channel="','"')
        if xmid in idlist:
            continue

        title = tools.regex_from_to(b,'<title>','</title>')
        desc = tools.regex_from_to(b,'<desc>','</desc>').replace('\n','*')
        cat = tools.regex_from_to(desc,'Category: ',',')
        if cat == '':
            cat = tools.regex_from_to(desc,'Categoria: ',',')
            if cat == '':
                cat = 'Unknown'

        pgm = '  <programme start="'+start+'" stop="'+stop+'" channel="x'+xmid+'">\n    <title>'+title+'</title>\n    <desc>'+desc+'</desc>\n    <category>'+cat+'</category>\n  </programme>\n'
        altdata1 += pgm

    saveEPG(altdata1)

def saveEPG(content):
    eof = '</tv>\n'
    chanData = open((basePath+'iptvxepg.xml'),'w')
    content += eof
    chanData.write(content)
    chanData.close()
    xbmc.executebuiltin("Notification(IPTVXtra II,[I][COLOR lime]   . . .*Merged EPG Created.[/COLOR][/I],1000)")

def saveCh(content):
    eof = '}\n'
    chanData = open((basePath+'ch_list.txt'),'w')
#    content += eof# write endoffile content
    chanData.write(content)
    # close the file
    chanData.close()
#    xbmc.executebuiltin("Notification(IPTVXtra II,[I][COLOR blue]   . . .*Channel List Updated.[/COLOR][/I],1000)")
    m3uproc(content)

def saveVod(content, type):

    eof = '}\n'
    fileObject = open((basePath+'vod-'+type+'.txt'),'w')
    content += eof# write endoffile content
    fileObject.write(content)
    # close the file
    fileObject.close()


def readVod(cat):


    catlist = ['21','23','26','27','28']
    if cat in catlist:
        strmcat='true'
    else:
        strmcat='false'

    mod=''
    if (cat !='ppv'):
        choice = xbmcgui.Dialog().yesno(user.name,'Would You like New items only, or Complete listing?', yeslabel = "New Only", nolabel = "Complete", autoclose=10000)
        if choice:
            mod ='1'
        else:
            mod ='0'
    else: pass

    strmset = xbmcaddon.Addon(user.id).getSetting(id='vodStrm')
#    cnt=1

    fileObject = open((basePath+'vod-'+cat+'.txt'),'r')
#    all_chans = tools.regex_get_all(fileObject,'{"num":',':0},')
    for a in fileObject:
        name = tools.regex_from_to(a,'"name":"','"')
        vodID = tools.regex_from_to(a,'stream_id":"','",')
        thumb = tools.regex_from_to(a,'stream_icon":"','",')
        new = tools.regex_from_to(a,'new":"','"]')
        if (cat == 'ppv'):
            url = vodID
        else:
            url = playvod_url+vodID+'.mp4'

        if mod=='1':
            if new =='true':
                if not (name==""):
                    tools.addDir(name+'  *New!',url,4,cat,thumb,thumb,vodID)
            else: pass

        elif mod=='0':
            if not (name==""):
                if new =='true':
                    tools.addDir(name+'  *New!',url,4,cat,thumb,thumb,vodID)

                else:
                    tools.addDir(name,url,4,cat,thumb,thumb,vodID)
            if (strmset=='true') and (strmcat=='true'):
                makeStrm(name,url)
#                        cnt += 1
            else: pass

        else:
            if not (name==""):
                tools.addDir(name,url,4,cat,thumb,thumb,vodID)


    if (strmset=='true') and (strmcat=='true'):
        xbmc.executebuiltin('Notification(IPTVXtra II,[COLOR lime]  *.strm files updated.[/COLOR],3000)')

def makeStrm(name,content):

    try:
        fileObj = open((strmPath + str(name).replace(':','-').replace('/','-').replace('?','').replace("'","").replace('\\','_').replace('#', ' ').replace('&','and').replace('  *New!','') +'.strm'),'w')
        fileObj.write(content)
        fileObj.close()
    except:
        pass

def saveFile(content):

    fileObject = open((basePath+'iptvxtra2.m3u'),'w')
    # write file content
    fileObject.write(content)
    # close the file
    fileObject.close()
    xbmc.executebuiltin("Notification(IPTVXtra II,[I][COLOR lime]   . . .*Custom PVR Playlist Created.[/COLOR][/I],1000)")

def extplyr(mod):

    if xbmc.getCondVisibility('System.Platform.Android'):
        if mod=='1':
            if not os.path.exists(explayer_home):
                file = open(os.path.join(advanced_settings, 'playercorefactory.xml'))
                a = file.read()
                f = open(explayer_home, mode='w')
                f.write(a)
                f.close()
        else:
            os.remove(explayer_home)

    dialog = xbmcgui.Dialog().yesno(user.name, 'External Player mode changes will take effect upon next KODI restart./nRestart KODI now for changes to take effect?')
    if dialog:
        xbmc.executebuiltin('ActivateWindow(shutdownmenu)')
    else:
        return

def mouse(mod):

    if mod=='1':
        if not os.path.exists(mouse_home):
            if xbmc.getCondVisibility('System.Platform.Android')=='true':
                file = open(os.path.join(advanced_settings, 'mouseA.xml'))
            else:
                file = open(os.path.join(advanced_settings, 'mouseW.xml'))
            a = file.read()
            f = open(mouse_home, mode='w')
            f.write(a)
            f.close()
    else:
        os.remove(mouse_home)

    dialog = xbmcgui.Dialog().yesno(user.name, 'Mouse Remapping will take effect on next KODI restart.\nRestart KODI now for changes to take effect?')
    if dialog:
        xbmc.executebuiltin('ActivateWindow(shutdownmenu)')
    else:
        return



def autopvr():
    autoexec =  os.path.join(xbmc.translatePath('special://home'),'userdata', 'autoexec.py')
    if not os.path.exists(autoexec):
        file = open(os.path.join(advanced_settings, 'autoexec.txt'))
        a = file.read()
        f = open(autoexec, mode='w')
        f.write(a)
        f.close()

    xbmc.executeJSONRPC('{"jsonrpc":"2.0", "method":"Settings.SetSettingValue", "params":{"setting":"epg.futuredaystodisplay", "value":3}, "id":1}')
    xbmc.executeJSONRPC('{"jsonrpc":"2.0", "method":"Settings.SetSettingValue", "params":{"setting":"pvrmanager.backendchannelorder", "value":true}, "id":1}')
    xbmc.executeJSONRPC('{"jsonrpc":"2.0", "method":"Settings.SetSettingValue", "params":{"setting":"pvrmanager.usebackendchannelnumbers", "value":true}, "id":1}')
    xbmc.executeJSONRPC('{"jsonrpc":"2.0", "method":"Settings.SetSettingValue", "params":{"setting":"pvrmanager.syncchannelgroups", "value":true}, "id":1}')
    xbmc.executeJSONRPC('{"jsonrpc":"2.0", "method":"Settings.SetSettingValue", "params":{"setting":"epg.ignoredbforclient", "value":true}, "id":1}')

def addSrc():
    path = os.path.join(xbmc.translatePath('special://home'),'userdata', 'sources.xml')
    if not os.path.exists(path):
        f = open(path, mode='w')
        f.write('<sources>\n    <programs>\n        <default pathversion="1"></default>\n    </programs>\n    <video>\n        <default pathversion="1"></default>\n        <source>\n            <name>IPTVXtra II VOD</name>\n            <path pathversion="1">special://profile/addon_data/plugin.video.iptvxtra2/vodstrms/</path>\n            <thumbnail pathversion="1">special://home/addons/plugin.video.iptvxtra2/icon.png</thumbnail>\n            <allowsharing>true</allowsharing>\n        </source>\n    </video>\n    <music>\n        <default pathversion="1" />\n    </music>\n    <pictures>\n        <default pathversion="1" />\n    </pictures>\n    <files>\n        <default pathversion="1" />\n    </files>\n</sources>\n')
        f.close()
        return
        
    f   = open(path, mode='r')
    str = f.read()
    f.close()
    if not'IPTVXtra II VOD' in str:
        if '</video>' in str:
            str = str.replace('</video>','    <source>\n            <name>IPTVXtra II VOD</name>\n            <path pathversion="1">special://profile/addon_data/plugin.video.iptvxtra2/vodstrms/</path>\n            <thumbnail pathversion="1">special://home/addons/plugin.video.iptvxtra2/icon.png</thumbnail>\n            <allowsharing>true</allowsharing>\n        </source>\n    </video>')
            f = open(path, mode='w')
            f.write(str)
            f.close()
        else:
            str = str.replace('</sources>','    <video>\n        <default pathversion="1"></default>\n        <source>\n            <name>IPTVXtra II VOD</name>\n            <path pathversion="1">special://profile/addon_data/plugin.video.iptvxtra2/vodstrms/</path>\n            <thumbnail pathversion="1">special://home/addons/plugin.video.iptvxtra2/icon.png</thumbnail>\n            <allowsharing>true</allowsharing>\n        </source>\n    </video>\n</sources>')
            f = open(path, mode='w')
            f.write(str)
            f.close() 

def m3uproc(js):

    xbmc.executebuiltin('Notification(IPTVXtra II,[I][COLOR yellow] . . . .Processing Channel Data  . . . . . . . . . . . . . . . . . . . . . . . . . . [/COLOR][/I],7000)')
    m3u = '#EXTM3U\n#EXTINF:-1 tvg-id="00411" tvg-chno="1" tvg-name="Information" tvg-logo="https://raw.githubusercontent.com/kens13/EPG/master/info.png" group-title="Information",Information \nhttps://raw.githubusercontent.com/kens13/EPG/master/test_pattern_1.mp4\n' 
#    f = open(basePath+'iptvxtra_xmlid.json',mode='r')
#    chanskip = f.read()
#    f.close()
    try: conv = json.loads(js)
    except: conv = {}

    open = tools.OPEN_URL(player_api)
    all_chans = tools.regex_get_all(open,'{"num":',':0},')
    for a in all_chans:
        name = tools.regex_from_to(a,'name":"','"').replace('\/','/')
        url = tools.regex_from_to(a,'stream_id":','\,"')
        thumb = tools.regex_from_to(a,'stream_icon":"','"').replace('\/','/')
        cat = tools.regex_from_to(a,'category_id":"','"')
        xml_id = tools.regex_from_to(a,'epg_channel_id":"','"')
        ds = tools.regex_from_to(a,'direct_source":"','"').replace('\/','/')
        if (xbmcaddon.Addon().getSetting('hidexxx')=='true') and (cat == '13') or (cat == '25'):
            continue

        cat = cat.replace('4', 'Sports')
        cat = cat.replace('5', 'Cinema')
        cat = cat.replace('6', 'Kids')
        cat = cat.replace('7', 'Internationals')
        cat = cat.replace('8', 'Information')
        cat = cat.replace('10', 'Entertainments')
        cat = cat.replace('11', 'Science')
        cat = cat.replace('12', 'Music')
        cat = cat.replace('13', 'For Adults')
        cat = cat.replace('14', 'Culture')
        cat = cat.replace('15', 'Business')

        try: chno_grp = conv[name]
        except: chno_grp = 'group-title="'+cat

        if (':' in ds.lower()):
            line = '#EXTINF:-1 tvg-id="'+xml_id+'" tvg-name="'+name+'" tvg-logo="'+thumb+'" '+chno_grp+'", '+name+'\n'+ds+'\n'
        else:
            line = '#EXTINF:-1 tvg-id="'+xml_id+'" tvg-name="'+name+'" tvg-logo="'+thumb+'" '+chno_grp+'", '+name+'\n'+play_url+url+'.ts\n'
        m3u += line

    saveFile(m3u)

def catchup():
    listcatchup()
        
def listcatchup():
    open = tools.OPEN_URL(panel_api)
    all  = tools.regex_get_all(open,'{"num','direct')
    for a in all:
        if '"tv_archive":1' in a:
            name = tools.regex_from_to(a,'"epg_channel_id":"','"').replace('\/','/')
            thumb= tools.regex_from_to(a,'"stream_icon":"','"').replace('\/','/')
            id   = tools.regex_from_to(a,'stream_id":"','"')
            if not name=="":
                tools.addDir(name,'url',13,'',thumb,fanart,id)
            

def tvarchive(name,description):
    days = 5
    
    now = str(datetime.datetime.now()).replace('-','').replace(':','').replace(' ','')
    date3 = datetime.datetime.now() - datetime.timedelta(days)
    date = str(date3)
    date = str(date).replace('-','').replace(':','').replace(' ','')
    APIv2 = base64.b64decode("JXM6JXMvcGxheWVyX2FwaS5waHA/dXNlcm5hbWU9JXMmcGFzc3dvcmQ9JXMmYWN0aW9uPWdldF9zaW1wbGVfZGF0YV90YWJsZSZzdHJlYW1faWQ9JXM=")%(host,user.port,username,password,description)
    link=tools.OPEN_URL(APIv2)
    match = re.compile('"title":"(.+?)".+?"start":"(.+?)","end":"(.+?)","description":"(.+?)"').findall(link)
    for ShowTitle,start,end,DesC in match:
        ShowTitle = base64.b64decode(ShowTitle)
        DesC = base64.b64decode(DesC)
        format = '%Y-%m-%d %H:%M:%S'
        try:
            modend = dtdeep.strptime(end, format)
            modstart = dtdeep.strptime(start, format)
        except:
            modend = datetime.datetime(*(time.strptime(end, format)[0:6]))
            modstart = datetime.datetime(*(time.strptime(start, format)[0:6]))
        StreamDuration = modend - modstart
        modend_ts = time.mktime(modend.timetuple())
        modstart_ts = time.mktime(modstart.timetuple())
        FinalDuration = int(modend_ts-modstart_ts) / 60
        strstart = start
        Realstart = str(strstart).replace('-','').replace(':','').replace(' ','')
        start2 = start[:-3]
        editstart = start2
        start2 = str(start2).replace(' ',' - ')
        start = str(editstart).replace(' ',':')
        Editstart = start[:13] + '-' + start[13:]
        Finalstart = Editstart.replace('-:','-')
        if Realstart > date:
            if Realstart < now:
                catchupURL = base64.b64decode("JXM6JXMvc3RyZWFtaW5nL3RpbWVzaGlmdC5waHA/dXNlcm5hbWU9JXMmcGFzc3dvcmQ9JXMmc3RyZWFtPSVzJnN0YXJ0PQ==")%(host,user.port,username,password,description)
                ResultURL = catchupURL + str(Finalstart) + "&duration=%s"%(FinalDuration)
                kanalinimi = "[B][COLOR purple]%s[/COLOR][/B] - %s"%(start2,ShowTitle)
                tools.addDir(kanalinimi,ResultURL,4,'',icon,fanart,DesC)

    
                    
def DownloaderClass(url, dest):
    dp = xbmcgui.DialogProgress()
    dp.create('Fetching latest Catch Up',"Fetching latest Catch Up...",' ', ' ')
    dp.update(0)
    start_time=time.time()
    urllib.urlretrieve(url, dest, lambda nb, bs, fs: _pbhook(nb, bs, fs, dp, start_time))

def _pbhook(numblocks, blocksize, filesize, dp, start_time):
        try: 
            percent = min(numblocks * blocksize * 100 / filesize, 100) 
            currently_downloaded = float(numblocks) * blocksize / (1024 * 1024) 
            kbps_speed = numblocks * blocksize / (time.time() - start_time) 
            if kbps_speed > 0: 
                eta = (filesize - numblocks * blocksize) / kbps_speed 
            else: 
                eta = 0 
            kbps_speed = kbps_speed / 1024 
            mbps_speed = kbps_speed / 1024 
            total = float(filesize) / (1024 * 1024) 
            mbs = '[B][COLOR purple]%.02f MB of less than 5MB[/COLOR][/B]' % (currently_downloaded)
            e = '[B][COLOR purple]Speed:  %.02f Mb/s ' % mbps_speed  + '[/COLOR][/B]'
            dp.update(percent, mbs, e)
        except: 
            percent = 100 
            dp.update(percent) 
        if dp.iscanceled():
            dialog = xbmcgui.Dialog()
            dialog.ok(user.name, 'The download was cancelled.')
                
            sys.exit()
            dp.close()
#####################################################################

def tvguide():
    xbmc.executebuiltin('ActivateWindow(TVGuide)')
def stream_video(url):
    url = buildcleanurl(url)
    url = str(url).replace('USERNAME',username).replace('PASSWORD',password)
    liz = xbmcgui.ListItem('', iconImage='DefaultVideo.png', thumbnailImage=icon)
    liz.setInfo(type='Video', infoLabels={'Title': '', 'Plot': ''})
    liz.setProperty('IsPlayable','true')
    liz.setPath(str(url))
    xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, liz)
    
    
def searchdialog():
    search = control.inputDialog(heading='Search '+user.name+':')
    if search=="":
        return
    else:
        return search

    
def search():
    if mode==3:
        return False
    text = searchdialog()
    if not text:
        xbmc.executebuiltin("XBMC.Notification([B][COLOR purple][B]Search is Empty[/B][/COLOR][/B],Aborting search,4000,"+icon+")")
        return
    xbmc.log(str(text))
    open = tools.OPEN_URL(panel_api)
    all_chans = tools.regex_get_all(open,'{"num":','epg')
    for a in all_chans:
        name = tools.regex_from_to(a,'name":"','"').replace('\/','/')
        url  = tools.regex_from_to(a,'"stream_id":"','"')
        thumb= tools.regex_from_to(a,'stream_icon":"','"').replace('\/','/')
        if text in name.lower():
            tools.addDir(name,play_url+url+'.ts',4,'',thumb,fanart,'')
        elif text not in name.lower() and text in name:
            tools.addDir(name,play_url+url+'.ts',4,'',thumb,fanart,'')

    
def settingsmenu():
    if xbmcaddon.Addon(user.id).getSetting('meta')=='true':
        META = '[B][COLOR lime]ON[/COLOR][/B]'
    else:
        META = '[B][COLOR red]OFF[/COLOR][/B]'
    if xbmcaddon.Addon(user.id).getSetting('hidexxx')=='true':
        XXX = '[B][COLOR lime]ON[/COLOR][/B]'
    else:
        XXX = '[B][COLOR red]OFF[/COLOR][/B]'
    if xbmcaddon.Addon(user.id).getSetting('epgx')=='true':
        EPG = '[B][COLOR lime]Alternate Enabled[/COLOR][/B] / Provider EPG'
    else:
        EPG = 'Alternate Disabled/ [B][COLOR lime]Provider EPG[/COLOR][/B]'
    tools.addDir('Edit Advanced Settings','ADS',10,'',icon,fanart,'')
    tools.addDir('META for VOD is %s'%META,'META',10,'',icon,fanart,META)
    tools.addDir('Hide XXX Channels is %s'%XXX,'XXX',10,'',icon,fanart,XXX)
    tools.addDir('EPG Source-> %s'%EPG,'EPG',10,'',icon,fanart,EPG)
    tools.addDir('Logout/Reset User ID','LO',10,'',icon,fanart,'')
    

def addonsettings(url,description):
    url  = buildcleanurl(url)
    if   url =="CC":
        tools.clear_cache()
    elif url =="AS":
        xbmc.executebuiltin('Addon.OpenSettings(%s)'%user.id)
    elif url =="ADS":
        dialog = xbmcgui.Dialog().select('Edit Advanced Settings', ['Enable Fire TV Stick AS','Enable Fire TV AS','Enable 1GB Ram or Lower AS','Enable 2GB Ram or Higher AS','Enable Nvidia Shield AS','Disable AS'])
        if dialog==0:
            advancedsettings('stick')
            xbmcgui.Dialog().ok(user.name, 'Set Advanced Settings')
        elif dialog==1:
            advancedsettings('firetv')
            xbmcgui.Dialog().ok(user.name, 'Set Advanced Settings')
        elif dialog==2:
            advancedsettings('lessthan')
            xbmcgui.Dialog().ok(user.name, 'Set Advanced Settings')
        elif dialog==3:
            advancedsettings('morethan')
            xbmcgui.Dialog().ok(user.name, 'Set Advanced Settings')
        elif dialog==4:
            advancedsettings('shield')
            xbmcgui.Dialog().ok(user.name, 'Set Advanced Settings')
        elif dialog==5:
            advancedsettings('remove')
            xbmcgui.Dialog().ok(user.name, 'Advanced Settings Removed')
    elif url =="ADS2":
        dialog = xbmcgui.Dialog().select('Select Your Device Or Closest To', ['Fire TV Stick ','Fire TV','1GB Ram or Lower','2GB Ram or Higher','Nvidia Shield'])
        if dialog==0:
            advancedsettings('stick')
            xbmcgui.Dialog().ok(user.name, 'Set Advanced Settings')
        elif dialog==1:
            advancedsettings('firetv')
            xbmcgui.Dialog().ok(user.name, 'Set Advanced Settings')
        elif dialog==2:
            advancedsettings('lessthan')
            xbmcgui.Dialog().ok(user.name, 'Set Advanced Settings')
        elif dialog==3:
            advancedsettings('morethan')
            xbmcgui.Dialog().ok(user.name, 'Set Advanced Settings')
        elif dialog==4:
            advancedsettings('shield')
            xbmcgui.Dialog().ok(user.name, 'Set Advanced Settings')
    elif url =="tv":
        dialog = xbmcgui.Dialog().yesno(user.name,'Would you like to change the EPG guide source?')
        if dialog:
            xbmcaddon.Addon(user.id).openSettings()
            if xbmcaddon.Addon(user.id).getSetting('epgmrg')=='true':
                mkEPG()
                correctPVR('1')
            else:
                correctPVR('2')
    elif url =="ST":
        xbmc.executebuiltin('Runscript("special://home/addons/'+user.id+'/resources/modules/speedtest.py")')
    elif url =="helptest":
        xbmc.executebuiltin('ShowPicture('+help_set1+')')
    elif url =="XPLR":
        if 'Enabled' in description:
            xbmcaddon.Addon(user.id).setSetting(id='extplr',value='false')
            xbmc.executebuiltin('Container.Refresh')
            extplyr('0')
        else:
            if xbmc.getCondVisibility('System.Platform.Android'):
                xbmcaddon.Addon(user.id).setSetting(id='extplr',value='true')
                xbmc.executebuiltin('Container.Refresh')
            extplyr('1')
    elif url =="MKMP":
        if 'Enabled' in description:
            xbmcaddon.Addon(user.id).setSetting(id='mousemap',value='false')
            xbmc.executebuiltin('Container.Refresh')
            mouse('0')
        else:
            xbmcaddon.Addon(user.id).setSetting(id='mousemap',value='true')
            xbmc.executebuiltin('Container.Refresh')
            mouse('1')
    elif url =="META":
        if 'ON' in description:
            xbmcaddon.Addon(user.id).setSetting('meta','false')
            xbmc.executebuiltin('Container.Refresh')
        else:
            xbmcaddon.Addon(user.id).setSetting('meta','true')
            xbmc.executebuiltin('Container.Refresh')
    elif url =="EPG":
        if 'Enabled' in description:
            xbmcaddon.Addon(user.id).setSetting('epgx','false')
            xbmc.executebuiltin('Container.Refresh')
        else:
            xbmcaddon.Addon(user.id).setSetting('epgx','true')
            xbmc.executebuiltin('Container.Refresh')
    elif url =="XXX":
        if 'ON' in description:
            xbmcaddon.Addon(user.id).setSetting('hidexxx','false')
            xbmc.executebuiltin('Container.Refresh')
        else:
            xbmcaddon.Addon(user.id).setSetting('hidexxx','true')
            xbmc.executebuiltin('Container.Refresh')
    elif url =="LO":
        xbmcaddon.Addon(user.id).setSetting('Username','')
        xbmcaddon.Addon(user.id).setSetting('Password','')
        xbmcaddon.Addon(user.id).setSetting('Server','')
        xbmc.executebuiltin('XBMC.ActivateWindow(Videos,addons://sources/video/)')
        xbmc.executebuiltin('Container.Refresh')
    elif url =="UPDATE":
        if 'ON' in description:
            xbmcaddon.Addon(user.id).setSetting('update','false')
            xbmc.executebuiltin('Container.Refresh')
        else:
            xbmcaddon.Addon(user.id).setSetting('update','true')
            xbmc.executebuiltin('Container.Refresh')
    
        
def advancedsettings(device):
    if device == 'stick':
        file = open(os.path.join(advanced_settings, 'stick.xml'))
    elif device == 'firetv':
        file = open(os.path.join(advanced_settings, 'firetv.xml'))
    elif device == 'lessthan':
        file = open(os.path.join(advanced_settings, 'lessthan1GB.xml'))
    elif device == 'morethan':
        file = open(os.path.join(advanced_settings, 'morethan1GB.xml'))
    elif device == 'shield':
        file = open(os.path.join(advanced_settings, 'shield.xml'))
    elif device == 'remove':
        os.remove(advanced_settings_target)
    
    try:
        read = file.read()
        f = open(advanced_settings_target, mode='w+')
        f.write(read)
        f.close()
    except:
        pass
        
def pvrsetup():
#    correctPVR()
    return
        
def showHelp():
    dialog = xbmcgui.Dialog().select('Select Help Category', ['Main Menu','IPTVXtra Addon Settings','VOD & PPV Context Menu Functions','KODI Library Integration (.strm files)','n/a'])
    if dialog==0:
        xbmcgui.Dialog().textviewer('Main Menu',help.main)
        showHelp()
    elif dialog==1:
        xbmcgui.Dialog().textviewer('IPTVXtra Settings',help.settings)
        showHelp()
    elif dialog==2:
        xbmcgui.Dialog().textviewer('VOD & PPV Context Menu Functions',help.vodcm)
        showHelp()
    elif dialog==3:
        xbmcgui.Dialog().textviewer('KODI Library Integration',help.libint)
        showHelp()
    elif dialog==4:
        xbmcgui.Dialog().textviewer('Settings',help.settings)
        showHelp()
    else:
        home()

def asettings():
    choice = xbmcgui.Dialog().yesno(user.name, 'Please Select The RAM Size of Your Device', yeslabel='Less than 1GB RAM', nolabel='More than 1GB RAM')
    if choice:
        lessthan()
    else:
        morethan()
    

def morethan():
        file = open(os.path.join(advanced_settings, 'morethan.xml'))
        a = file.read()
        f = open(advanced_settings_target, mode='w+')
        f.write(a)
        f.close()

        
def lessthan():
        file = open(os.path.join(advanced_settings, 'lessthan.xml'))
        a = file.read()
        f = open(advanced_settings_target, mode='w+')
        f.write(a)
        f.close()
        
        
def userpopup():
    kb =xbmc.Keyboard ('', 'heading', True)
    kb.setHeading('Enter Username')
    kb.setHiddenInput(False)
    kb.doModal()
    if (kb.isConfirmed()):
        text = kb.getText()
        return text
    else:
        return False

        
def passpopup():
    kb =xbmc.Keyboard ('', 'heading', True)
    kb.setHeading('Enter Password')
    kb.setHiddenInput(False)
    kb.doModal()
    if (kb.isConfirmed()):
        text = kb.getText()
        return text
    else:
        return False

def portpopup():
    dialog = xbmcgui.Dialog()
    entries = ["http://p1.iptvrocket.tv", "http://p2.iptvrocket.tv", "http://s1.iptv66.tv", "http://s2.iptv66.tv", "http://p1.iptvprivateserver.tv", "http://p2.iptvprivateserver.tv", "http://p3.iptvprivateserver.tv", "http://p4.iptvprivateserver.tv", "http://p5.iptvprivateserver.tv", "http://p6.iptvprivateserver.tv", "http://p1.iptvrocket.ru", "http://p2.iptvrocket.ru", "http://s1.iptv66.ru", "http://s2.iptv66.ru", "http://p1.iptvprivateserver.ru", "http://p2.iptvprivateserver.ru", "http://p3.iptvprivateserver.ru", "http://p4.iptvprivateserver.ru", "http://p5.iptvprivateserver.ru", "http://p6.iptvprivateserver.ru"]
    nr = dialog.select("Select your Server/ Portal", entries)
    if nr>=0:
        text = entries[nr]
        return text
    else:
        return False

def accountinfo():

    try:
        open = tools.OPEN_URL(panel_api)
        useracct = tools.regex_from_to(open,'"username":"','"')
        passacct = tools.regex_from_to(open,'"password":"','"')
        status = tools.regex_from_to(open,'"status":"','"')
        connects = tools.regex_from_to(open,'"max_connections":"','"')
        active = tools.regex_from_to(open,'"active_cons":"','"')
        serverurl = tools.regex_from_to(open,'"url":"','"')
        expiry = tools.regex_from_to(open,'"exp_date":"','"')
        if not expiry=="":
            expiry = datetime.datetime.fromtimestamp(int(expiry)).strftime('%d/%m/%Y - %H:%M')
            expreg = re.compile('^(.*?)/(.*?)/(.*?)$',re.DOTALL).findall(expiry)
            for day,month,year in expreg:
                month = tools.MonthNumToName(month)
                year = re.sub(' -.*?$','',year)
                expiry = month+' '+day+' - '+year
        else:
            expiry = 'Unlimited'
        ip = tools.getlocalip()
        extip = tools.getexternalip()

        tools.addDir('[B][COLOR purple]Username :[/COLOR][/B] '+useracct,'','','',icon,fanart,'')
        tools.addDir('[B][COLOR purple]Password :[/COLOR][/B] '+passacct,'','','',icon,fanart,'')
        tools.addDir('[B][COLOR purple]Server URL :[/COLOR][/B] '+serverurl,'','','',icon,fanart,'')
        tools.addDir('[B][COLOR yellow]Expiry Date:[/COLOR][/B] '+expiry,'','','',icon,fanart,'')
        tools.addDir('[B][COLOR purple]Account Status :[/COLOR][/B] %s'%status,'','','',icon,fanart,'')
        tools.addDir('[B][COLOR purple]Current Connections:[/COLOR][/B] '+ active,'','','',icon,fanart,'')
        tools.addDir('[B][COLOR purple]Allowed Connections:[/COLOR][/B] '+connects,'','','',icon,fanart,'')
        tools.addDir('[B][COLOR purple]Local IP Address:[/COLOR][/B] '+ip,'','','',icon,fanart,'')
        tools.addDir('[B][COLOR purple]External IP Address:[/COLOR][/B] '+extip,'','','',icon,fanart,'')
        tools.addDir('[B][COLOR purple]Kodi Version:[/COLOR][/B] '+str(KODIV),'','','',icon,fanart,'')
    except:
        pass

def correctPVR(mod):

    addon = xbmcaddon.Addon(user.id)
    pvrsimple = xbmcaddon.Addon('pvr.iptvsimple')
    username_text = addon.getSetting(id='Username')
    password_text = addon.getSetting(id='Password')
    external = addon.getSetting(id='epgx')
    merge = addon.getSetting(id='epgmrg')
    xEPGurl = addon.getSetting(id='xepgurl')
    PEPGurl = host+':'+user.port+"/xmltv.php?username=" + username_text + "&password=" + password_text
    pvrOFF = xbmc.executeJSONRPC('{{"jsonrpc":"2.0","id":1,"method":"Addons.SetAddonEnabled","params":{{"addonid":"{}","enabled":false}}}}'.format("pvr.iptvsimple"))

    if (mod != '0') or (mod != 'ch'):
        if merge =='true':
            epg = (basePath+'iptvxepg.xml')
            mod = '1'
        elif external =='true':
            epg = xEPGurl
            mod = '2'
        elif external !='true':
            epg = PEPGurl
            mod = '2'

    pvrOFF
    pvrsimple.setSetting(id='m3uPathType', value="0")
    pvrsimple.setSetting(id='m3uPath', value=(basePath+'iptvxtra2.m3u'))


    if mod=='0':
        pvrOFF
        pvrsimple.setSetting(id='m3uPathType', value="0")
        pvrsimple.setSetting(id='m3uPath', value=(basePath+'iptvxtra2.m3u'))
        pvrsimple.setSetting(id='epgPathType', value="1")
        pvrsimple.setSetting(id='epgUrl', value=xEPGurl)
        pvrsimple.setSetting(id='m3uCache', value="false")
        pvrsimple.setSetting(id='epgCache', value="false")

    elif mod=='1':
        pvrOFF
        pvrsimple.setSetting(id='epgPathType', value="0")
        pvrsimple.setSetting(id='epgPath', value=(basePath+'iptvxepg.xml'))

    elif mod=='2':
        pvrOFF
        pvrsimple.setSetting(id='epgPathType', value="1")
        pvrsimple.setSetting(id='epgUrl', value= epg)

    else:
        pvrsimple.setSetting(id='epgCache', value="false")

    dialog2 = xbmcgui.Dialog().yesno(user.name, 'PVR Integration Complete.  Restart Kodi Now For Changes To Take Effect?')
    if dialog2:
        xbmc.executebuiltin('ActivateWindow(shutdownmenu)')
    else:
        return



def num2day(num):
    if num =="0":
        day = 'monday'
    elif num=="1":
        day = 'tuesday'
    elif num=="2":
        day = 'wednesday'
    elif num=="3":
        day = 'thursday'
    elif num=="4":
        day = 'friday'
    elif num=="5":
        day = 'saturday'
    elif num=="6":
        day = 'sunday'
    return day
    
def extras():
    if xbmcaddon.Addon(user.id).getSetting(id='extplr')=='true':
        MOD = '[COLOR lime]Enabled[/COLOR]'
    else:
        MOD = '[COLOR red]Disabled[/COLOR]'
    if xbmcaddon.Addon(user.id).getSetting(id='mousemap')=='true':
        MMOD = '[COLOR lime]Enabled[/COLOR]'
    else:
        MMOD = '[COLOR red]Disabled[/COLOR]'
    if xbmcaddon.Addon(user.id).getSetting(id='epgx')=='true':
        if xbmcaddon.Addon(user.id).getSetting(id='epgmrg')=='true':
            EPGMD = '[COLOR orange]Merged EPG[/COLOR]'
        else:
            EPGMD = '[COLOR lime]Alternate EPG[/COLOR]'
    else:
        EPGMD = '[COLOR yellow]Providers EPG[/COLOR]'


    tools.addDir('Change EPG Guide Source ->  %s'%EPGMD,'tv',10,'',icon_set,fan_extr,EPGMD)
    tools.addDir('Change External Player Status ->  %s'%MOD,'XPLR',10,'',icon_set,fan_extr,MOD)
    tools.addDir('Change Mouse Remapping Status ->  %s'%MMOD,'MKMP',10,'',icon_set,fan_extr,MMOD)
    tools.addDir('Live TV backup (PVR not used)','live',1,'',icon,fan_extr,'')
    tools.addDir('Run a Speed Test','ST',10,'',icon_tool,fan_extr,'')





    
#MKMP
params=tools.get_params()
url=None
name=None
mode=None
iconimage=None
description=None
query=None
type=None

try:
    url=urllib.unquote_plus(params["url"])
except:
    pass
try:
    name=urllib.unquote_plus(params["name"])
except:
    pass
try:
    iconimage=urllib.unquote_plus(params["iconimage"])
except:
    pass
try:
    mode=int(params["mode"])
except:
    pass
try:
    description=urllib.unquote_plus(params["description"])
except:
    pass
try:
    query=urllib.unquote_plus(params["query"])
except:
    pass
try:
    type=urllib.unquote_plus(params["type"])
except:
    pass

if mode==None or url==None or len(url)<1:
    autopvr()
    start()

elif mode==1:
    livecategory(url)
    
elif mode==2:
    Livelist(url)
    
elif mode==3:
    vodselect()
    
elif mode==4:
    stream_video(url)
    
elif mode==5:
    readVod('ppv')
    
elif mode==6:
    accountinfo()
    
elif mode==7:
    tvguide()
    
elif mode==8:
#    settingsmenu()
    xbmcaddon.Addon(user.id).openSettings()
elif mode==9:
    xbmc.executebuiltin('ActivateWindow(busydialog)')
    tools.Trailer().play(url) 
    xbmc.executebuiltin('Dialog.Close(busydialog)')
    
elif mode==10:
    addonsettings(url,description)
    
elif mode==11:
    pvrsetup()
    
elif mode==12:
    catchup()

elif mode==13:
    tvarchive(name,description)
    
elif mode==14:
    listcatchup2()
    
#elif mode==15:
#    showhelp(url)
    
elif mode==16:
    extras()
    
elif mode==17:
    getchan()

elif mode==18:
    makeStrm(name,url)
    xbmc.executebuiltin('Notification(IPTVXtra II,[B][COLOR lime]*'+name+'.strm created.[/COLOR][/B],4000,'+icon+')')
    xbmc.executebuiltin('updatelibrary(video)')

elif mode==19:
    showHelp()

elif mode==20:
    vodinfo(name,url)

elif mode==21:
    xbmc.executebuiltin('ActivateWindow(shutdownmenu)')

xbmcplugin.endOfDirectory(int(sys.argv[1]))