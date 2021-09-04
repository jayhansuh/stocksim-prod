from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views import generic

# Create your views here.

from .models import Ticker, DayPrice
from .makedb import get_last_price
from portfolio.models import Player, AssetHistory
from portfolio.scheduler import quetrigger
from .backdoor import backdoorIndex


import datetime
import json
#import random
import time

def getLastPrice(request):

    ticker = request.GET.get('ticker')
    try:
        price=get_last_price(ticker)
    except:
        print("ERROR: NO INFORMATION FOUND - " + ticker)
        return JsonResponse({"ERROR": "NO INFORMATION FOUND - CHECK TICKER"})
    return JsonResponse({"ticker":ticker,"price":price})

REFDATE=datetime.date(1900,1,1)
def indtodate(ind):
    try:
        return REFDATE+datetime.timedelta(days=ind-1)
    except:
        return REFDATE
def datetoind(date):
    try:
        return (date-REFDATE).days+1
    except:
        return REFDATE

def getMeta(request):

    req = json.loads(request.GET.get('req',"{}"))

    if("LAB" in req):
        return backdoorIndex(request,req)

    if("update_trigger" in req):
        quetrigger(180)
        del(req["update_trigger"])

    # if("setNewDayAssetHistory" in req):
    #     setNewDayAssetHistory()
    #     del(req["setNewDayAssetHistory"])

    if("recent_players" in req):
        que=Player.objects.order_by('-user__last_login')[:req["recent_players"]]
        for player in que.values('user__username'):
            key='player__'+player['user__username']
            if(not(key in req)):
                req[key]=1
        del(req["recent_players"])

    if("recent_tickers" in req):
        que=Ticker.objects.order_by('-last_date')[:req["recent_tickers"]]
        for ticker in que.values('ticker'):
            key='ticker__'+player['ticker']
            if(not key in req):
                req[key]=1
        del(req["recent_tickers"])


    res = {}

    for el in req:
        strt_date=indtodate(req[el])
        el_arr=el.split('__')
        extrct_cols=tuple()

        if(el_arr[0]=="player"):
            try:
                que=Player.objects.get(user__username=el_arr[1])
            except Player.DoesNotExist:
                continue
            #que.makeHistory()
            que=que.assethistory_set.filter(Date__gte=strt_date,code__gt=0)
            extrct_cols=('asset',)

        elif(el_arr[0]=="ticker"):
            try:
                que=Ticker.objects.get(ticker=el_arr[1])
            except Ticker.DoesNotExist:
                continue
            que=que.dayprice_set.filter(Date__gte=strt_date)
            extrct_cols=('Open','Close','High','Low',)
        else:
            print("Unknown request type",el,flush=True)
            continue

        if(not que.exists()):
            continue
        que=que.order_by('Date')
        date_ptr=que[0].Date

        res[el]={}
        res[el]['strt_date']=datetoind(date_ptr)
        for key in extrct_cols:
            res[el][key]=[]

        que=que.values(*(('Date',)+extrct_cols))
        oneday=datetime.timedelta(days=1)
        for q in que:
            while(date_ptr<q['Date']):
                for key in extrct_cols:
                    res[el][key].append(None)
                date_ptr+=oneday
            for key in extrct_cols:
                #res[el][key].append(q[key]*random.uniform(0.99,1.01))
                res[el][key].append(q[key])
            date_ptr+=oneday

        #for val in extrct_cols:
        #    while(date_ptr<val[])
        #    res[el][val]=[ q[val] for q in que]

    res=json.loads(json.dumps(res), parse_float=lambda x: round(float(x), 4))

    return JsonResponse(res)