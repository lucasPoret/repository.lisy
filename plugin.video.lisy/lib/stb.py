import requests
from urllib.parse import urlparse
import re
import math


def getUrl(url, proxy=None):
    def parseResponse(url, data):
        java = data.text.replace(' ', '').replace("'", '').replace('+', '')
        pattern = re.search(r'varpattern.*\/(\(http.*)\/;', java).group(1)
        result = re.search(pattern, url)
        protocolIndex = re.search(
            r'this\.portal_protocol.*(\d).*;', java).group(1)
        ipIndex = re.search(r'this\.portal_ip.*(\d).*;', java).group(1)
        pathIndex = re.search(r'this\.portal_path.*(\d).*;', java).group(1)
        protocol = result.group(int(protocolIndex))
        ip = result.group(int(ipIndex))
        path = result.group(int(pathIndex))
        portalPatern = re.search(
            r'this\.ajax_loader=(.*\.php);', java).group(1)
        portal = portalPatern.replace('this.portal_protocol', protocol).replace(
            'this.portal_ip', ip).replace('this.portal_path', path)
        return portal

    url = urlparse(url).scheme + "://" + urlparse(url).netloc
    urls = ["/c/xpcom.common.js", "/client/xpcom.common.js", "/c_/xpcom.common.js",
            "/stalker_portal/c/xpcom.common.js", "/stalker_portal/c_/xpcom.common.js"]

    proxies = {"http": proxy, "https": proxy}
    headers = {"User-Agent": "Mozilla/5.0 (QtEmbedded; U; Linux; C)"}

    try:
        for i in urls:
            try:
                response = requests.get(
                    url + i, headers=headers, proxies=proxies)
            except:
                response = None
            if response:
                return parseResponse(url + i, response)
    except:
        pass
    raise Exception("Error getting portal URL")


def getToken(url, mac, proxy=None):
    proxies = {"http": proxy, "https": proxy}
    cookies = {"mac": mac, "stb_lang": "en", "timezone": "Europe/London"}
    headers = {"User-Agent": "Mozilla/5.0 (QtEmbedded; U; Linux; C)"}
    try:
        response = requests.get(
            url + "?type=stb&action=handshake&JsHttpRequest=1-xml",
            cookies=cookies,
            headers=headers,
            proxies=proxies
        )
        data = response.json()
        token = data["js"]["token"]
        if token:
            getProfile(url, mac, token, proxy)
            return token
    except:
        pass
    raise Exception("Error getting token")


def getProfile(url, mac, token, proxy=None):
    proxies = {"http": proxy, "https": proxy}
    cookies = {"mac": mac, "stb_lang": "en", "timezone": "Europe/London"}
    headers = {
        "User-Agent": "Mozilla/5.0 (QtEmbedded; U; Linux; C)",
        "Authorization": "Bearer " + token,
    }
    try:
        response = requests.get(
            url + "?type=stb&action=get_profile&JsHttpRequest=1-xml",
            cookies=cookies,
            headers=headers,
            proxies=proxies
        )
        data = response.json()
        if data:
            return data
    except:
        pass
    raise Exception("Error getting profile")


def getExpires(url, mac, token, proxy=None):
    proxies = {"http": proxy, "https": proxy}
    cookies = {"mac": mac, "stb_lang": "en", "timezone": "Europe/London"}
    headers = {
        "User-Agent": "Mozilla/5.0 (QtEmbedded; U; Linux; C)",
        "Authorization": "Bearer " + token,
    }
    try:
        response = requests.get(
            url + "?type=account_info&action=get_main_info&JsHttpRequest=1-xml",
            cookies=cookies,
            headers=headers,
            proxies=proxies
        )
        data = response.json()
        expire = data["js"]["phone"]
        if expire:
            return expire
    except:
        pass
    return "Unkown"


def getAllChannels(url, mac, token, proxy=None):
    proxies = {"http": proxy, "https": proxy}
    cookies = {"mac": mac, "stb_lang": "en", "timezone": "Europe/London"}
    headers = {
        "User-Agent": "Mozilla/5.0 (QtEmbedded; U; Linux; C)",
        "Authorization": "Bearer " + token,
    }
    try:
        response = requests.get(
            url
            + "?type=itv&action=get_all_channels&force_ch_link_check=&JsHttpRequest=1-xml",
            cookies=cookies,
            headers=headers,
            proxies=proxies
        )
        channels = response.json()["js"]["data"]
        if channels:
            return channels
    except:
        pass
    raise Exception("Error getting channels")


def getGenres(url, mac, token, proxy=None):
    proxies = {"http": proxy, "https": proxy}
    cookies = {"mac": mac, "stb_lang": "en", "timezone": "Europe/London"}
    headers = {
        "User-Agent": "Mozilla/5.0 (QtEmbedded; U; Linux; C)",
        "Authorization": "Bearer " + token,
    }
    try:
        response = requests.get(
            url + "?action=get_genres&type=itv&JsHttpRequest=1-xml",
            cookies=cookies,
            headers=headers,
            proxies=proxies
        )
        genreData = response.json()["js"]
        genres = {}
        for i in genreData:
            gid = i["id"]
            name = i["title"]
            genres[gid] = name
        if genres:
            return genres
    except:
        pass
    raise Exception("Error getting genres")


def getLink(url, mac, token, cmd, proxy=None):
    proxies = {"http": proxy, "https": proxy}
    cookies = {"mac": mac, "stb_lang": "en", "timezone": "Europe/London"}
    headers = {
        "User-Agent": "Mozilla/5.0 (QtEmbedded; U; Linux; C)",
        "Authorization": "Bearer " + token,
    }
    try:
        response = requests.get(
            url + "?type=itv&action=create_link&cmd=" + cmd +
            "&series=0&forced_storage=false&disable_ad=false&download=false&force_ch_link_check=false&JsHttpRequest=1-xml",
            cookies=cookies,
            headers=headers,
            proxies=proxies
        )
        data = response.json()
        link = data["js"]["cmd"].split()[-1]
        if link:
            return link
    except:
        pass
    raise Exception("Error getting link")


def getEpg(url, mac, token, period, proxy=None):
    proxies = {"http": proxy, "https": proxy}
    cookies = {"mac": mac, "stb_lang": "en", "timezone": "Europe/London"}
    headers = {
        "User-Agent": "Mozilla/5.0 (QtEmbedded; U; Linux; C)",
        "Authorization": "Bearer " + token,
    }
    try:
        response = requests.get(
            url + "?type=itv&action=get_epg_info&period=" +
            str(period) + "&JsHttpRequest=1-xml",
            cookies=cookies,
            headers=headers,
            proxies=proxies
        )
        data = response.json()["js"]["data"]
        if data:
            return data
    except:
        pass
    raise Exception("Found no EPG data")


def getVods(url, mac, token, proxy=None):
    proxies = {"http": proxy, "https": proxy}
    cookies = {"mac": mac, "stb_lang": "en", "timezone": "Europe/London"}
    headers = {
        "User-Agent": "Mozilla/5.0 (QtEmbedded; U; Linux; C)",
        "Authorization": "Bearer " + token,
    }
    try:
        response = requests.get(
            url + "?type=vod&action=get_ordered_list&p=1&JsHttpRequest=1-xml",
            cookies=cookies,
            headers=headers,
            proxies=proxies
        )
        data = response.json()["js"]
        pages = math.ceil(int(data["total_items"]) /
                          int(data["max_page_items"]))
        vods = response.json()["js"]["data"]

        for i in range(2, pages):
            response = requests.get(
                url + "?type=vod&action=get_ordered_list&p=" +
                str(i) + "&JsHttpRequest=1-xml",
                cookies=cookies,
                headers=headers,
                proxies=proxies
            )
            vods = vods + response.json()["js"]["data"]
        if vods:
            return vods
    except:
        pass
    raise Exception("Found no VOD data")


def getVodLink(url, mac, token, cmd, proxy=None):
    proxies = {"http": proxy, "https": proxy}
    cookies = {"mac": mac, "stb_lang": "en", "timezone": "Europe/London"}
    headers = {
        "User-Agent": "Mozilla/5.0 (QtEmbedded; U; Linux; C)",
        "Authorization": "Bearer " + token,
    }
    try:
        response = requests.get(
            url + "?type=vod&action=create_link&cmd=" + cmd + "&JsHttpRequest=1-xml",
            cookies=cookies,
            headers=headers,
            proxies=proxies
        )
        data = response.json()
        link = data["js"]["cmd"].split()[-1]
        if link:
            return link
    except:
        pass
    raise Exception("Error getting link")


def getSeries(url, mac, token, proxy=None):
    proxies = {"http": proxy, "https": proxy}
    cookies = {"mac": mac, "stb_lang": "en", "timezone": "Europe/London"}
    headers = {
        "User-Agent": "Mozilla/5.0 (QtEmbedded; U; Linux; C)",
        "Authorization": "Bearer " + token,
    }
    try:
        response = requests.get(
            url + "?type=series&action=get_ordered_list&p=1&JsHttpRequest=1-xml",
            cookies=cookies,
            headers=headers,
            proxies=proxies
        )
        data = response.json()["js"]
        if data:
            return data
    except:
        pass
    raise Exception("Found no VOD data")


def test(url, mac, token, proxy=None):
    proxies = {"http": proxy, "https": proxy}
    cookies = {"mac": mac, "stb_lang": "en", "timezone": "Europe/London"}
    headers = {
        "User-Agent": "Mozilla/5.0 (QtEmbedded; U; Linux; C)",
        "Authorization": "Bearer " + token,
    }
    try:
        response = requests.get(
            url + "?type=series&action=get_ordered_list&movie_id=2198%3A1&category=2198:1&genre=*&season_id=0&episode_id=0&force_ch_link_check=&from_ch_id=0&fav=0&sortby=added&hd=0&not_ended=0&p=1&JsHttpRequest=1-xml",
            cookies=cookies,
            headers=headers,
            proxies=proxies
        )
        data = response.json()["js"]
        if data:
            return data
    except:
        pass
    raise Exception("Found no VOD data")

def getVodsCategories(url,mac,token,proxy=None):
    proxies = {"http": proxy, "https": proxy}
    cookies = {"mac": mac, "stb_lang": "en", "timezone": "Europe/London"}
    headers = {
        "User-Agent": "Mozilla/5.0 (QtEmbedded; U; Linux; C)",
        "Authorization": "Bearer " + token,
    }
    try:
        response = requests.get(
            url + "?type=vod&action=get_categories&JsHttpRequest=1-xml",
            cookies=cookies,
            headers=headers,
            proxies=proxies
        )
        categoryData = response.json()["js"]
        category = {}
        for i in categoryData:
            gid = i["id"]
            name = i["title"]
            category[gid] = name
        if category:
            return category
    except:
        pass
    raise Exception("Error getting genres")



def getVodsByCat(url, mac, token, category, proxy=None, page=0):
    proxies = {"http": proxy, "https": proxy}
    cookies = {"mac": mac, "stb_lang": "en", "timezone": "Europe/London"}
    headers = {
        "User-Agent": "Mozilla/5.0 (QtEmbedded; U; Linux; C)",
        "Authorization": "Bearer " + token,
    }
    try:
        response = requests.get(
            url + "?type=vod&action=get_ordered_list&category=" + str(category) + "&p=" + str(page) + "&JsHttpRequest=1-xml",
            cookies=cookies,
            headers=headers,
            proxies=proxies
        )
        data = response.json()["js"]
        total_items = int(data["total_items"])
        max_page_items = int(data["max_page_items"])
        pages = math.ceil(total_items / max_page_items)
        vods = response.json()["js"]["data"]

        if page == 0:
            for i in range(2, pages + 1):
                response = requests.get(
                    url + "?type=vod&action=get_ordered_list&category=" + str(category) + "&p=" + str(i) + "&JsHttpRequest=1-xml",
                    cookies=cookies,
                    headers=headers,
                    proxies=proxies
                )
                vods += response.json()["js"]["data"]
        elif page <= pages:
            response = requests.get(
                url + "?type=vod&action=get_ordered_list&category=" + str(category) + "&p=" + str(page) + "&JsHttpRequest=1-xml",
                cookies=cookies,
                headers=headers,
                proxies=proxies
            )
            vods = response.json()["js"]["data"]
        else:
            raise Exception("Page number exceeds total pages")

        if vods:
            return vods, page < pages
    except:
        pass
    raise Exception("Found no VOD data")

def getSeriesCategories(url,mac,token,proxy=None):
    proxies = {"http": proxy, "https": proxy}
    cookies = {"mac": mac, "stb_lang": "en", "timezone": "Europe/London"}

    headers = {
        "User-Agent": "Mozilla/5.0 (QtEmbedded; U; Linux; C)",
        "Authorization": "Bearer " + token
    }
    try:
        response = requests.get(
            url + "?type=series&action=get_categories&JsHttpRequest=1-xml",
            cookies=cookies,
            headers=headers,
            proxies=proxies
        )
        categoryData = response.json()["js"]
        category = {}
        for i in categoryData:
            gid = i["id"]
            name = i["title"]
            category[gid] = name
        if category:
            return category
    except:
        pass
    raise Exception("Error getting genres")

def getSeriesByCat(url, mac, token, category, proxy=None, page=0):
    proxies = {"http": proxy, "https": proxy}
    cookies = {"mac": mac, "stb_lang": "en", "timezone": "Europe/London"}
    headers = {
        "User-Agent": "Mozilla/5.0 (QtEmbedded; U; Linux; C)",
        "Authorization": "Bearer " + token,
    }
    try:
        response = requests.get(
            url + "?type=series&action=get_ordered_list&category=" + str(category) + "&p=" + str(page) + "&JsHttpRequest=1-xml",
            cookies=cookies,
            headers=headers,
            proxies=proxies
        )
        data = response.json()["js"]
        total_items = int(data["total_items"])
        max_page_items = int(data["max_page_items"])
        pages = math.ceil(total_items / max_page_items)
        series = response.json()["js"]["data"]
        if page == 0:
            for i in range(2, pages + 1):
                response = requests.get(
                    url + "?type=series&action=get_ordered_list&category=" + str(category) + "&p=" + str(i) + "&JsHttpRequest=1-xml",
                    cookies=cookies,
                    headers=headers,
                    proxies=proxies
                )
                series += response.json()["js"]["data"]
        elif page <= pages:
            response = requests.get(
                url + "?type=series&action=get_ordered_list&category=" + str(category) + "&p=" + str(page) + "&JsHttpRequest=1-xml",
                cookies=cookies,
                headers=headers,
                proxies=proxies
            )
            series = response.json()["js"]["data"]
        else:
            raise Exception("Page number exceeds total pages")
        if series:
            return series, page < pages
    except:
        pass
    raise Exception("Found no series data")
   
def getChannelsByCat(url, mac, token, genreId, proxy=None, page=0):  # pb ne recupere pas tout
    proxies = {"http": proxy, "https": proxy}
    cookies = {"mac": mac, "stb_lang": "en", "timezone": "Europe/London"}
    headers = {
        "User-Agent": "Mozilla/5.0 (QtEmbedded; U; Linux; C)",
        "Authorization": "Bearer " + token,
    }
    try:
        response = requests.get(
            url + "?type=itv&action=get_ordered_list&genre=" + str(genreId) + "&p=1&JsHttpRequest=1-xml",
            cookies=cookies,
            headers=headers,
            proxies=proxies
        )
        data = response.json()["js"]
        pages = math.ceil(int(data["total_items"]) /
                          int(data["max_page_items"]))
        channels = response.json()["js"]["data"]

        for i in range(2, pages):
            response = requests.get(
                url + "?type=itv&action=get_ordered_list&genre=" + str(genreId) + "&p=" +
                str(i) + "&JsHttpRequest=1-xml",
                cookies=cookies,
                headers=headers,
                proxies=proxies
            )
            channels = channels + response.json()["js"]["data"]
        if channels:
            return channels
    except:
        pass
    raise Exception("Found no live data")

def getSeasons(url, mac, token, id, proxy=None): 
    proxies = {"http": proxy, "https": proxy}
    cookies = {"mac": mac, "stb_lang": "en", "timezone": "Europe/Paris"}
    headers = {
        "User-Agent": "Mozilla/5.0 (QtEmbedded; U; Linux; C)",
        "Authorization": "Bearer "+token,
    }
    try:
        response = requests.get(
            url + "?type=series&action=get_ordered_list&movie_id="+str(id)+"p=1",
            cookies=cookies,
            headers=headers,
            proxies=proxies
        )
        data = response.json()["js"]
        if data:
            return data
    except:
        pass
    raise Exception("Found no live data")

def getEpisodeLink(url, mac, token, season_id, episode_number, proxy=None): 
    proxies = {"http": proxy, "https": proxy}
    cookies = {"mac": mac, "stb_lang": "en", "timezone": "Europe/Paris"}
    headers = {
        "User-Agent": "Mozilla/5.0 (QtEmbedded; U; Linux; C)",
        "Authorization": "Bearer "+token,
    }
    try:
        response = requests.get(
            url + "?type=vod&action=create_link&series="+str(episode_number)+"&cmd=/media/"+str(season_id)+".mpg",
            cookies=cookies,
            headers=headers,
            proxies=proxies
        )
        data = response.json()["js"]
        if data:
            print(url+"?type=vod&action=create_link&series="+str(episode_number)+"&cmd=/media/"+str(season_id)+".mpg")
            return data.get('cmd').split()[-1]
    except:
        pass
    raise Exception("Found no live data")

#http://mol-2.com:8080/server/load.php?action=get_ordered_list&p=1&type=vod&category=*&sortby=added&search=a

def search(url, mac, token, type, category, search, page=0, proxy=None):  # pb ne recupere pas tout
    proxies = {"http": proxy, "https": proxy}
    cookies = {"mac": mac, "stb_lang": "en", "timezone": "Europe/Paris"}
    headers = {
        "User-Agent": "Mozilla/5.0 (QtEmbedded; U; Linux; C)",
        "Authorization": "Bearer "+token,
    }
    try:
        response = requests.get(
            url + "?type="+type+"&action=get_ordered_list&category="+str(category)+"&p=1&search="+search,
            cookies=cookies,
            headers=headers,
            proxies=proxies
        )
        data = response.json()["js"]
        pages = math.ceil(int(data["total_items"]) /
                          int(data["max_page_items"]))
        videos = response.json()["js"]["data"]
        if page == 0:
            for i in range(2, pages):
                response = requests.get(
                    url + "?type="+type+"&action=get_ordered_list&sortby=added&category="+str(category)+"&p=" +
                    str(i) + "&search="+search,
                    cookies=cookies,
                    headers=headers,
                    proxies=proxies
                )
                videos += response.json()["js"]["data"]
        elif page <= pages:
            response = requests.get(
                url + "?type="+type+"&action=get_ordered_list&sortby=added&category="+str(category)+"&p=" + str(page) + "&search="+search,
                cookies=cookies,
                headers=headers,
                proxies=proxies
            )
            videos = response.json()["js"]["data"]
        else:
            raise Exception("Page number exceeds total pages")
        if videos:
            return videos, page < pages
    except:
        pass
    raise Exception("Found no live data")