from django.shortcuts import render
from django.http import HttpResponse
import urllib.request as urllib
from datetime import date, datetime
import json
import math

def get_season(now,Y):
    seasons = [('winter', (date(Y,  1,  1),  date(Y,  3, 20))),
           ('spring', (date(Y,  3, 21),  date(Y,  6, 20))),
           ('summer', (date(Y,  6, 21),  date(Y,  9, 22))),
           ('fall', (date(Y,  9, 23),  date(Y, 12, 20))),
           ('winter', (date(Y, 12, 21),  date(Y, 12, 31)))]
    if isinstance(now, datetime):
        now = now.date()
    now = now.replace(year=Y)
    return next(season for season, (start, end) in seasons
                if start <= now <= end)

def get_year():
    now=datetime.now()
    year=now.strftime("%Y")
    return year

def readurl(url):
    hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive'}
    req = urllib.Request(url, headers=hdr)
    with urllib.urlopen(req) as result:
        json_out=result.read()
        data = json.loads(json_out.decode())
    return data

def get_episodes(animes):
    for anime in animes[0]:
        url="https://kitsu.io/api/edge/episodes?filter[mediaId]="+anime
        nb_episode=readurl(url)['meta']['count']
        for episodes_url in range(10, nb_episode+10,10):
            data=readurl(url)
            dates=[]
            for episode_date in data['data']:
                dates.append(episode_date['attributes']['airdate'])
            url="https://kitsu.io/api/edge/episodes?filter[mediaId]="+anime+'&page[limit]=10&page[offset]='+str(episodes_url)
        animes[2].append(dates)
    return animes

def index(request):
    now=datetime.now()
    year=get_year()
    season=get_season(now,int(year))
    url='https://kitsu.io/api/edge/anime?filter[year]='+year+'&filter[season]='+season
    nb_anime=readurl(url)['meta']['count']
    animes=[[],[],[]]
    for urls in range(10, nb_anime+10,10):
        data=readurl(url)
        for anime_id in data['data']:
            animes[0].append(anime_id['id'])
            try:
                animes[1].append(anime_id['attributes']['titles']['en_jp'])
            except Exception:
                animes[1].append(anime_id['attributes']['titles']['en_us'])
        url='https://kitsu.io/api/edge/anime?filter[year]='+year+'&filter[season]='+season+'&page[limit]=10&page[offset]='+str(urls)
    animes=get_episodes(animes)
    return HttpResponse(animes[2])
