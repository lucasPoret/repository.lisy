import xbmcaddon
import xbmcplugin
import xbmcgui
import xbmcvfs
import xbmc
import urllib.parse
import lib.stb as stb
import lib.lisy as lisy
import sys
import json
import os
import platform
import uuid

addon = xbmcaddon.Addon()
portal_url = 'http://mol-2.com:8080/c/'
mac_address = '00:1A:79:2F:E1:54'
base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
args = urllib.parse.parse_qs(sys.argv[2][1:])
user = addon.getSetting('user')
password = addon.getSetting('password')



file_path = xbmcvfs.translatePath("special://profile/addon_data/plugin.video.lisy/token.json")

# Check if the variables.json file exist
if os.path.exists(file_path):
    # Read the contents of the variables.json file
    with open(file_path, 'r') as file:
        data = json.load(file)
    
    # Get the values of new_url and token from the dictionary
    token = data.get('token')
else:
    # If the variables.json file does not exist, set new_url and token to None
    token = None

def init():

    device_name = platform.node().split('.')[0]
    mac = ':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff) for ele in range(0, 8 * 6, 8)][::-1])
   
    login_response = lisy.login(user, password, device_name, mac)
    token = login_response.get('token')
    message = login_response.get('message')
    status_code = login_response.get('status_code')
    
    if status_code != 200:
        xbmcgui.Dialog().notification('Error', f"{message} : {status_code}", xbmcgui.NOTIFICATION_ERROR)
        return False
    if token is None:
        xbmcgui.Dialog().notification('Error', 'Token is None', xbmcgui.NOTIFICATION_ERROR)
        return False

    # Create a dictionary to store the variables
    data = {
        'token': token
    }

    # Write the dictionary to the variables.json file
    with open(file_path, 'w') as file:
        json.dump(data, file)

    return True

def build_url(query):
    return base_url + '?' + urllib.parse.urlencode(query)

mode = args.get('mode', None)

def router(args):
    if mode is None:
        if not init():
            return
        
        url = build_url({'mode': 'TV'})
        li = xbmcgui.ListItem('TV')
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,
                                    listitem=li, isFolder=True)

        url = build_url({'mode': 'VOD'})
        li = xbmcgui.ListItem('VOD')
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,
                                    listitem=li, isFolder=True)

        url = build_url({'mode': 'Series'})
        li = xbmcgui.ListItem('Series')
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,
                                    listitem=li, isFolder=True)

        xbmcplugin.endOfDirectory(addon_handle)

    elif mode[0] == 'TV':
        if args.get('category', None) is None:
            show_tv_categories()
        else:
            show_tv(args['category'][0])
    elif mode[0] == 'play_tv':
        play_tv(args['cmd'][0])
        
    elif mode[0] == 'VOD':
        if args.get('category', None) is None:
            show_vod_categories()
        else:
            show_vod(args['category'][0],args['page'][0])
    elif mode[0] == 'play_vod':
        play_vod(args['cmd'][0])
    elif mode[0] == 'Series':
        if args.get('category', None) is None:
            show_series_categories()
        else:
            show_series(args['category'][0],args['page'][0])
    elif mode[0] == 'Seasons':
        show_seasons(args['category'][0],args['page'][0],args['series_id'][0])
    elif mode[0] == 'Episodes':
        show_episodes(args['category'][0],args['page'][0],args['series_id'][0],args['season_id'][0],args['nb_episodes'][0],args['thumb'][0],args['description'][0])
    elif mode[0] == 'play_episode':
        play_episode(args['episode'][0],args['season_id'][0])
    elif mode[0] == 'Search':
        search(args['type'][0],args['category'][0],args['current_page'][0],args['page'][0],args.get('search', None))

def show_tv_categories():
    li=xbmcgui.ListItem("Home")
    li.setArt({"thumb": xbmcvfs.translatePath("special://home/addons/plugin.video.STB/resources/icons/home.png")})
    url = base_url
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)

    categories = lisy.getTvCategories(token)

    if categories.get('status_code') != 200:
        xbmcgui.Dialog().notification('Error', f"Error: {categories.get('message')} : {categories.get('status_code')}", xbmcgui.NOTIFICATION_ERROR)
        return

    for key, value in categories.get('categories').items():
        url = build_url({'mode': 'TV', 'category': key})
        li = xbmcgui.ListItem(value)
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,
                                    listitem=li, isFolder=True)
    xbmcplugin.endOfDirectory(addon_handle)

def show_tv(category):
   
    channels = lisy.getTvByCat(token, category)

    if channels.get('status_code') != 200:
        xbmcgui.Dialog().notification('Error', f"Error: {channels.get('message')} : {channels.get('status_code')}", xbmcgui.NOTIFICATION_ERROR)
        return

    #search for tv
    li=xbmcgui.ListItem("Search")
    li.setArt({"thumb": xbmcvfs.translatePath("special://home/addons/plugin.video.STB/resources/icons/search.png")})
    url=build_url({'mode': 'Search','type': 'tv', 'category': category, 'page': 1})
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)

    #home
    li=xbmcgui.ListItem("Home")
    li.setArt({"thumb": xbmcvfs.translatePath("special://home/addons/plugin.video.STB/resources/icons/home.png")})
    url = base_url
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)

    #go back
    li=xbmcgui.ListItem("Back")
    li.setArt({"thumb": xbmcvfs.translatePath("special://home/addons/plugin.video.STB/resources/icons/back.png")})
    url = build_url({'mode': 'TV'})
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)



    for channel in channels.get('channels'):
        li = xbmcgui.ListItem(channel.get("name"))
        cmd=channel.get("cmd")
        li.setArt({"thumb":channel.get("logo")})
        url=build_url({'mode': 'play_tv', 'cmd': cmd})
        li.setProperty('IsPlayable', 'true')
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li)

    xbmcplugin.endOfDirectory(addon_handle)

def play_tv(cmd):
    url = lisy.getLink(token, cmd)
    if url.get('status_code') != 200:
        xbmcgui.Dialog().notification('Error', f"Error: {url.get('message')} : {url.get('status_code')}", xbmcgui.NOTIFICATION_ERROR)
        return

    li = xbmcgui.ListItem(path=url.get('link'))
    xbmcplugin.setResolvedUrl(addon_handle, True, listitem=li)


def show_vod_categories():

    li=xbmcgui.ListItem("Home")
    li.setArt({"thumb": xbmcvfs.translatePath("special://home/addons/plugin.video.STB/resources/icons/home.png")})
    url = base_url
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)

    categories = lisy.getVodsCategories(token)

    if categories.get('status_code') != 200:
        xbmcgui.Dialog().notification('Error', f"Error: {categories.get('message')} : {categories.get('status_code')}", xbmcgui.NOTIFICATION_ERROR)
        return
    
    for key, value in categories.get('categories').items():
        url = build_url({'mode': 'VOD', 'category': key, 'page': 1})
        li = xbmcgui.ListItem(value)
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,
                                    listitem=li, isFolder=True)
    xbmcplugin.endOfDirectory(addon_handle)

def show_vod(category, page):

    # Log a message
    page = int(page)
    
    req = lisy.getVodsByCat(token, category, page)

    if req.get('status_code') != 200:
        xbmcgui.Dialog().notification('Error', f"Error: {req.get('message')} : {req.get('status_code')}", xbmcgui.NOTIFICATION_ERROR)
        return
    
    films = req.get('films')
    has_next_page = req.get('has_next_page')

    #search for vod
    li=xbmcgui.ListItem("Search")
    li.setArt({"thumb": xbmcvfs.translatePath("special://home/addons/plugin.video.STB/resources/icons/search.png")})
    url=build_url({'mode': 'Search','type': 'vod', 'category': category, 'current_page': page, 'page': 1})
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)

    #home
    li=xbmcgui.ListItem("Home")
    li.setArt({"thumb": xbmcvfs.translatePath("special://home/addons/plugin.video.STB/resources/icons/home.png")})
    url = base_url
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)

    #go back
    li=xbmcgui.ListItem("Back")
    li.setArt({"thumb": xbmcvfs.translatePath("special://home/addons/plugin.video.STB/resources/icons/back.png")})
    url = build_url({'mode': 'VOD'})
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)

    if page>1:
        li=xbmcgui.ListItem("Previous Page")
        url = build_url({'mode': 'VOD', 'category': category, 'page': str(int(page)-1)})
        li.setArt({"thumb": xbmcvfs.translatePath("special://home/addons/plugin.video.STB/resources/icons/previous.png")})
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)

    for film in films:
        li = xbmcgui.ListItem(film.get("name"))
        plot = film.get("description")
        cmd=film.get("cmd")
        li.setArt({"thumb":film.get("screenshot_uri"), "icon": film.get("screenshot_uri"), "poster": film.get("screenshot_uri"), "fanart": film.get("screenshot_uri"), "banner": film.get("screenshot_uri")})
        li.addContextMenuItems([('Infos', 'Action(Info)')])

        info_tag = li.getVideoInfoTag()
        info_tag.setTitle(film.get("name"))
        info_tag.setPlot(plot)
        # info_tag.setCast = film.get("actors")
        info_tag.setDirectors(film.get("director").split(','))
        info_tag.setDateAdded(film.get("added"))
        info_tag.setGenres(film.get("genres_str").split(','))
        if film.get("rating_imdb") != '':
            imdb_rating = float(film.get("rating_imdb"))
        else:
            imdb_rating = 0.0

        if film.get("rating_kinopoisk") != '':
            kinopoisk_rating = float(film.get("rating_kinopoisk"))
        else:
            kinopoisk_rating = 0.0

        info_tag.setRatings({'imdb': (imdb_rating, 0), 'kinopoisk': (kinopoisk_rating, 0)}, 'imdb')
        url=build_url({'mode': 'play_vod', 'cmd': cmd,'name': film.get("name"),'thumb': film.get("screenshot_uri"),'plot': film.get("description")})
        li.setProperty('IsPlayable', 'true')    
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li)

    if has_next_page:
        url = build_url({'mode': 'VOD', 'category': category, 'page': str(int(page)+1)})
        li = xbmcgui.ListItem('Next Page')
        li.setArt({"thumb": xbmcvfs.translatePath("special://home/addons/plugin.video.STB/resources/icons/next.png")})
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,
                                    listitem=li, isFolder=True)

    xbmcplugin.endOfDirectory(addon_handle)

def play_vod(cmd):
    url = stb.getVodLink(new_url, mac_address, token, cmd)
    li = xbmcgui.ListItem(path=url)
    xbmcplugin.setResolvedUrl(addon_handle, True, listitem=li)

def show_series_categories():

    li=xbmcgui.ListItem("Home")
    li.setArt({"thumb": xbmcvfs.translatePath("special://home/addons/plugin.video.STB/resources/icons/home.png")})
    url = base_url
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)

    categories = lisy.getSeriesCategories(token)
    if categories.get('status_code') != 200:
        xbmcgui.Dialog().notification('Error', f"Error: {categories.get('message')} : {categories.get('status_code')}", xbmcgui.NOTIFICATION_ERROR)
        return

    for key, value in categories.get('categories').items():
        url = build_url({'mode': 'Series', 'category': key, 'page': 1})
        li = xbmcgui.ListItem(value)
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,
                                    listitem=li, isFolder=True)
    xbmcplugin.endOfDirectory(addon_handle)

def show_series(category, page):

    page = int(page)
    xbmc.log(f'category: {category}, page: {page}', xbmc.LOGINFO)
    xbmc.log(f'new_url: {new_url}', xbmc.LOGINFO)
    series, has_next_page = stb.getSeriesByCat(new_url, mac_address, token, category, None, page)

    #search for series
    li=xbmcgui.ListItem("Search")
    li.setArt({"thumb": xbmcvfs.translatePath("special://home/addons/plugin.video.STB/resources/icons/search.png")})
    url=build_url({'mode': 'Search','type': 'series', 'category': category, 'current_page': page, 'page': 1})
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)

    #home
    li=xbmcgui.ListItem("Home")
    li.setArt({"thumb": xbmcvfs.translatePath("special://home/addons/plugin.video.STB/resources/icons/home.png")})

    url = base_url
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)

    #go back
    li=xbmcgui.ListItem("Back")
    li.setArt({"thumb": xbmcvfs.translatePath("special://home/addons/plugin.video.STB/resources/icons/back.png")})
    url = build_url({'mode': 'Series'})
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)

    if page>1:
        li=xbmcgui.ListItem("Previous Page")
        url = build_url({'mode': 'Series', 'category': category, 'page': str(int(page)-1)})
        li.setArt({"thumb": xbmcvfs.translatePath("special://home/addons/plugin.video.STB/resources/icons/previous.png")})
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)

    for serie in series:
        li = xbmcgui.ListItem(serie.get("name"))
        plot = serie.get("description")
        serie_id=serie.get("id")
        li.setArt({"thumb":serie.get("screenshot_uri"), "icon": serie.get("screenshot_uri"), "poster": serie.get("screenshot_uri"), "fanart": serie.get("screenshot_uri"), "banner": serie.get("screenshot_uri")})
        li.addContextMenuItems([('Infos', 'Action(Info)')])
        info_tag = li.getVideoInfoTag()
        info_tag.setTitle(serie.get("name"))
        info_tag.setPlot(plot)
        # info_tag.setCast = film.get("actors")
        info_tag.setDirectors(serie.get("director").split(','))
        info_tag.setDateAdded(serie.get("added"))
        info_tag.setGenres(serie.get("genres_str").split(','))
        if serie.get("rating_imdb") != '':
            imdb_rating = float(serie.get("rating_imdb"))
        else:
            imdb_rating = 0.0
        if serie.get("rating_kinopoisk") != '':
            kinopoisk_rating = float(serie.get("rating_kinopoisk"))
        else:
            kinopoisk_rating = 0.0
        info_tag.setRatings({'imdb': (imdb_rating, 0), 'kinopoisk': (kinopoisk_rating, 0)}, 'imdb')
        url=build_url({'mode': 'Seasons', 'category': category, 'page': page, 'series_id': serie_id})
        li.setProperty('IsPlayable', 'false')
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)

    if has_next_page:
        url = build_url({'mode': 'Series', 'category': category, 'page': str(int(page)+1)})
        li = xbmcgui.ListItem('Next Page')
        li.setArt({"thumb": xbmcvfs.translatePath("special://home/addons/plugin.video.STB/resources/icons/next.png")})
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,
                                    listitem=li, isFolder=True)
        
    xbmcplugin.endOfDirectory(addon_handle)

def show_seasons(category, page, series_id):

    page = int(page)
    xbmc.log(f'category: {category}, page: {page}', xbmc.LOGINFO)
    xbmc.log(f'new_url: {new_url}', xbmc.LOGINFO)
    seasons = stb.getSeasons(new_url, mac_address, token, series_id).get('data')

    #home
    li=xbmcgui.ListItem("Home")
    li.setArt({"thumb": xbmcvfs.translatePath("special://home/addons/plugin.video.STB/resources/icons/home.png")})
    url = base_url
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)

    #go back
    li=xbmcgui.ListItem("Back")
    li.setArt({"thumb": xbmcvfs.translatePath("special://home/addons/plugin.video.STB/resources/icons/back.png")})
    url = build_url({'mode': 'Series', 'category': category, 'page': page})
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)


    for season in seasons:
        li = xbmcgui.ListItem(season.get("name"))
        plot = season.get("description")
        nb_episodes=len(season.get('series'))
        li.setArt({"thumb":season.get("screenshot_uri"), "icon": season.get("screenshot_uri"), "poster": season.get("screenshot_uri"), "fanart": season.get("screenshot_uri"), "banner": season.get("screenshot_uri")})
        li.addContextMenuItems([('Infos', 'Action(Info)')])
        info_tag = li.getVideoInfoTag()
        info_tag.setTitle(season.get("name"))
        info_tag.setPlot(plot)
        # info_tag.setCast = film.get("actors")
        info_tag.setDirectors(season.get("director").split(','))
        info_tag.setDateAdded(season.get("added"))
        info_tag.setGenres(season.get("genres_str").split(','))
        if season.get("rating_imdb") != '':
            imdb_rating = float(season.get("rating_imdb"))
        else:
            imdb_rating = 0.0
        if season.get("rating_kinopoisk") != '':
            kinopoisk_rating = float(season.get("rating_kinopoisk"))
        else:
            kinopoisk_rating = 0.0
        info_tag.setRatings({'imdb': (imdb_rating, 0), 'kinopoisk': (kinopoisk_rating, 0)}, 'imdb')
        url=build_url({'mode': 'Episodes', 'category': category, 'page': page, 'series_id': series_id, 'season_id':season.get("id"), 'nb_episodes': nb_episodes, 'thumb':season.get("screenshot_uri"), 'description': plot})
        li.setProperty('IsPlayable', 'false')
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)

    xbmcplugin.endOfDirectory(addon_handle)
    
def show_episodes(category, page, series_id, season_id, nb_episodes,thumb,description):

    page = int(page)
    xbmc.log(f'category: {category}, page: {page}', xbmc.LOGINFO)
    xbmc.log(f'new_url: {new_url}', xbmc.LOGINFO)
   

    #home
    li=xbmcgui.ListItem("Home")
    li.setArt({"thumb": xbmcvfs.translatePath("special://home/addons/plugin.video.STB/resources/icons/home.png")})
    url = base_url
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)

    #go back
    li=xbmcgui.ListItem("Back")
    li.setArt({"thumb": xbmcvfs.translatePath("special://home/addons/plugin.video.STB/resources/icons/back.png")})
    url = build_url({'mode': 'Seasons', 'category': category, 'page': page, 'series_id': series_id})
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)

    for episode in range(1, int(nb_episodes)+1):
        li = xbmcgui.ListItem("Episode " + str(episode))
        li.setArt({"thumb": thumb, "icon": thumb, "poster": thumb, "fanart": thumb, "banner": thumb})
        li.addContextMenuItems([('Infos', 'Action(Info)')])
        info_tag = li.getVideoInfoTag()
        info_tag.setTitle("Episode " + str(episode))
        info_tag.setPlot(description)
        url=build_url({'mode': 'play_episode', 'episode': episode, 'season_id':season_id})
        li.setProperty('IsPlayable', 'true')
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li)
    
    xbmcplugin.endOfDirectory(addon_handle)

def play_episode(episode, season_id):
    xbmc.log(f'episode: {episode}', xbmc.LOGINFO)
    xbmc.log('play_episode', xbmc.LOGINFO)
    url = stb.getEpisodeLink(new_url, mac_address, token, season_id, episode)
    li = xbmcgui.ListItem(path=url)
    xbmc.log(f'url: {url}', xbmc.LOGINFO)
    xbmcplugin.setResolvedUrl(addon_handle, True, listitem=li)

def search(type, category, current_page,page, current_search=None):

    xbmc.log(f'type: {type}, category: {category}, page: {current_page}', xbmc.LOGINFO)
    li = xbmcgui.ListItem('Home')
    li.setArt({"thumb": xbmcvfs.translatePath("special://home/addons/plugin.video.STB/resources/icons/home.png")})
    url = base_url
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)

    page = int(page)

    if type == 'vod':
        #back
        li=xbmcgui.ListItem("Back")
        li.setArt({"thumb": xbmcvfs.translatePath("special://home/addons/plugin.video.STB/resources/icons/back.png")})
        url = build_url({'mode': 'VOD', 'category': category, 'page': current_page})
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)

        if current_search is None:
            search = xbmcgui.Dialog().input('Search for VODs')
        else:
            search = current_search[0]
        #previous 
        if page>1:
            li=xbmcgui.ListItem("Previous Page")
            url = build_url({'mode': 'Search', 'type': type, 'category': category, 'current_page': page, 'page': str(int(page)-1), 'search': search})
            li.setArt({"thumb": xbmcvfs.translatePath("special://home/addons/plugin.video.STB/resources/icons/previous.png")})
            xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)

        if search:
            films,has_next_page = stb.search(new_url, mac_address, token, type, category, search, page)
            for film in films:
                li = xbmcgui.ListItem(film.get("name"))
                plot = film.get("description")
                cmd=film.get("cmd")
                li.setArt({"thumb":film.get("screenshot_uri")})
                info_tag = li.getVideoInfoTag()
                info_tag.setTitle(film.get("name"))
                info_tag.setPlot(plot)
                # info_tag.setCast = film.get("actors")
                info_tag.setDirectors(film.get("director").split(','))
                info_tag.setDateAdded(film.get("added"))
                info_tag.setGenres(film.get("genres_str").split(','))
                if film.get("rating_imdb") != '':
                    imdb_rating = float(film.get("rating_imdb"))
                else:
                    imdb_rating = 0.0
                if film.get("rating_kinopoisk") != '':
                    kinopoisk_rating = float(film.get("rating_kinopoisk"))
                else:
                    kinopoisk_rating = 0.0
                info_tag.setRatings({'imdb': (imdb_rating, 0), 'kinopoisk': (kinopoisk_rating, 0)}, 'imdb')
                url=build_url({'mode': 'play_vod', 'cmd': cmd,'name': film.get("name"),'thumb': film.get("screenshot_uri"),'plot': film.get("description")})
                li.setProperty('IsPlayable', 'true')
                xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li)
            if has_next_page:
                url = build_url({'mode': 'Search', 'type': type, 'category': category, 'current_page': page, 'page': str(int(page)+1), 'search': search})
                li = xbmcgui.ListItem('Next Page')
                li.setArt({"thumb": xbmcvfs.translatePath("special://home/addons/plugin.video.STB/resources/icons/next.png")})
                xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,
                                            listitem=li, isFolder=True)

    elif type == 'series':
        #back
        li=xbmcgui.ListItem("Back")
        li.setArt({"thumb": xbmcvfs.translatePath("special://home/addons/plugin.video.STB/resources/icons/back.png")})
        url = build_url({'mode': 'Series', 'category': category, 'page': current_page})
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)

        if current_search is None:
            search = xbmcgui.Dialog().input('Search for Series')
        else:
            search = current_search[0]
        #previous 
        if page>1:
            li=xbmcgui.ListItem("Previous Page")
            url = build_url({'mode': 'Search', 'type': type, 'category': category, 'current_page': page, 'page': str(int(page)-1), 'search': search})
            li.setArt({"thumb": xbmcvfs.translatePath("special://home/addons/plugin.video.STB/resources/icons/previous.png")})
            xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)

        if search:
            series,has_next_page = stb.search(new_url, mac_address, token, type, category, search, page)
            for serie in series:
                li = xbmcgui.ListItem(serie.get("name"))
                plot = serie.get("description")
                serie_id=serie.get("id")
                li.setArt({"thumb":serie.get("screenshot_uri")})
                info_tag = li.getVideoInfoTag()
                info_tag.setTitle(serie.get("name"))
                info_tag.setPlot(plot)
                # info_tag.setCast = film.get("actors")
                info_tag.setDirectors(serie.get("director").split(','))
                info_tag.setDateAdded(serie.get("added"))
                info_tag.setGenres(serie.get("genres_str").split(','))
                if serie.get("rating_imdb") != '':
                    imdb_rating = float(serie.get("rating_imdb"))
                else:
                    imdb_rating = 0.0
                if serie.get("rating_kinopoisk") != '':
                    kinopoisk_rating = float(serie.get("rating_kinopoisk"))
                else:
                    kinopoisk_rating = 0.0
                info_tag.setRatings({'imdb': (imdb_rating, 0), 'kinopoisk': (kinopoisk_rating, 0)}, 'imdb')
                url=build_url({'mode': 'Seasons', 'category': category, 'page': page, 'series_id': serie_id})
                li.setProperty('IsPlayable', 'false')
                xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)

            if has_next_page:
                url = build_url({'mode': 'Search', 'type': type, 'category': category, 'current_page': page, 'page': str(int(page)+1), 'search': search})
                li = xbmcgui.ListItem('Next Page')
                li.setArt({"thumb": xbmcvfs.translatePath("special://home/addons/plugin.video.STB/resources/icons/next.png")})
                xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,
                                            listitem=li, isFolder=True)
                
    if search:
        xbmcplugin.endOfDirectory(addon_handle)


# device_name = platform.node().split('.')[0]
# xbmc.log(f'Device Name: {device_name}', xbmc.LOGINFO)
# mac = ':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff) for ele in range(0, 8 * 6, 8)][::-1])
# xbmc.log(f'MAC Address: {mac_address}', xbmc.LOGINFO)
# login = lisy.login(user, password, device_name, mac)
# xbmc.log(f'login: {login}', xbmc.LOGINFO)
init()  
router(args)