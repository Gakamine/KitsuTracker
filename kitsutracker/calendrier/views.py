from django.shortcuts import render
from django.http import HttpResponse
import urllib.request as urllib
from datetime import date, datetime
import json
import math

global error,username

def handler404(request, *args, **argv):
    return render(request, '404.html')


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

def get_planning():
    now=datetime.now()
    year=get_year()
    season=get_season(now,int(year))
    url='https://kitsu.io/api/edge/anime?filter[year]='+year+'&filter[season]='+season
    nb_anime=readurl(url)['meta']['count']
    animes=[]
    for urls in range(10, nb_anime+10,10):
        data=readurl(url)
        for anime_id in data['data']:
            if(anime_id['attributes']['status']=="current"):
                id=anime_id['id']
                try:
                    title=anime_id['attributes']['titles']['en_jp']
                except Exception:
                    title=anime_id['attributes']['titles']['en_us']
                day=datetime.strptime(anime_id['attributes']['startDate'], '%Y-%m-%d').weekday()
                animes.append([id,title,day])
        url='https://kitsu.io/api/edge/anime?filter[year]='+year+'&filter[season]='+season+'&page[limit]=10&page[offset]='+str(urls)
    return animes

def index(request):
    global error, username
    username=""
    error=0
    monday=[]
    tuesday=[]
    wednesday=[]
    thursday=[]
    friday=[]
    saturday=[]
    sunday=[]
    days=[monday,tuesday,wednesday,thursday,friday,saturday,sunday]
    if 'username' in request.GET:
        animes=search(request.GET.get('username'))
    else:
        animes=get_planning()
    for anime in animes:
        if anime[2]==0:
            monday.append(anime[1])
        elif anime[2]==1:
            tuesday.append(anime[1])
        elif anime[2]==2:
            wednesday.append(anime[1])
        elif anime[2]==3:
            thursday.append(anime[1])
        elif anime[2]==4:
            friday.append(anime[1])
        elif anime[2]==5:
            saturday.append(anime[1])
        else:
            sunday.append(anime[1])
    anime_pics=0
    for i in days:
        if len(i)>anime_pics:
            anime_pics=len(i)
    context = {
        'monday': monday,
        'tuesday': tuesday,
        'wednesday': wednesday,
        'thursday': thursday,
        'friday': friday,
        'saturday': saturday,
        'sunday': sunday,
        'monday_l': len(monday),
        'tuesday_l': len(tuesday),
        'wednesday_l': len(wednesday),
        'thursday_l': len(thursday),
        'friday_l': len(friday),
        'saturday_l': len(saturday),
        'sunday_l': len(sunday),
        'error': error,
        'username': username,
        'pic': range(0,anime_pics),
     }
    return render(request, 'index.html', context)

def Get_user_id(arg):
    ask_id=False
    arg=str(arg)
    data=""
    ids=['https://kitsu.io/api/edge/users?filter[name]='+str(arg),'https://kitsu.io/api/edge/users?filter[slug]='+str(arg),'https://kitsu.io/api/edge/users?filter[id]='+str(arg)]
    for id in ids:
        if ask_id==False:
            try :
                data=readurl(id)['data'][0]['id']
                ask_id=True
            except Exception:
                ask_id=False
    return data

def search(query):
    global error, username
    user_id=Get_user_id(query)
    username=query
    if user_id!="":
        animes=[]
        url="https://kitsu.io/api/edge/library-entries?filter[userId]="+str(user_id)+"&filter[kind]=anime&filter[status]=current,planned"
        nb_anime = readurl(url)['meta']['count']
        for urls in range(10, nb_anime+10,10):
            datas=readurl(url)
            for data_id in datas['data']:
                data=readurl(data_id['relationships']['media']['links']['related'])
                if data['data']['attributes']['status']=='current':
                    id=data['data']['id']
                    try:
                        title=data['data']['attributes']['titles']['en_jp']
                    except Exception:
                        title=data['data']['attributes']['titles']['en_us']
                    day=datetime.strptime(data['data']['attributes']['startDate'], '%Y-%m-%d').weekday()
                    animes.append([id,title,day])
            url="https://kitsu.io/api/edge/library-entries?filter[userId]="+str(user_id)+"&filter[kind]=anime&filter[status]=current,planned&page[limit]=10&page[offset]="+str(urls)
        return animes
    else:
        error=query
        animes=get_planning()
        return animes
