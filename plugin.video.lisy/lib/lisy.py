import requests
import json
import xbmc

base_url = 'http://82.66.160.190:5050/'

def login(username, password,device, mac):
    url = base_url + 'login'
    xbmc.log('URL: ' + url, xbmc.LOGINFO)
    data = {'username': username, 'password': password, 'device': device, 'mac': mac}
    response = requests.post(url,json=data)
    return json.loads(response.text)

def getVodsCategories(token):
    url = base_url + 'getVodsCategories'
    data = {'token': token}
    response = requests.post(url,json=data)
    return json.loads(response.text)

def getSeriesCategories(token):
    url = base_url + 'getSeriesCategories'
    data = {'token': token}
    response = requests.post(url,json=data)
    return json.loads(response.text)

def getTvCategories(token):
    url = base_url + 'getTvCategories'
    data = {'token': token}
    response = requests.post(url,json=data)
    return json.loads(response.text)

def getTvByCat(token, category):
    url = base_url + 'getTvByCat'
    data = {'token': token, 'category': category}
    response = requests.post(url,json=data)
    return json.loads(response.text)

def getVodsByCat(token, category, page):
    url = base_url + 'getVodsByCat'
    data = {'token': token, 'category': category, 'page': page}
    response = requests.post(url,json=data)
    return json.loads(response.text)

def getLink(token, cmd):
    url = base_url + 'getLink'
    data = {'token': token, 'cmd': cmd}
    response = requests.post(url,json=data)
    return json.loads(response.text)