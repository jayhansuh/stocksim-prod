#from portfolio.models import Player, AssetHistory
from .models import *
from stockdb.models import *
from stockdb.makedb import *

import threading
import datetime
import time

from django.db import connection
from django.utils import timezone

def async_thread(function):
    def decorator(*args, **kwargs):
        t = threading.Thread(target = function, args=args, kwargs=kwargs, daemon=True)
        t.start()
    return decorator

def setNewDayAssetHistory():
    players = Player.objects.all()
    for player in players:
        player.catchupHistory()

@async_thread
def setTodayAssetHistory():

    #print("threading.active_count()")
    #print(threading.active_count())
    today=timezone.now().date()
    lastprice={}
    que=AssetHistory.objects.filter(code=3)

    if(len(que)==0 or today!=que[0].Date):
        print("updateTodayAssetHistory not working!!!",flush=True)
        if(len(que)==0):
            print( 'no AssetHistory at ' , today ,flush=True)
        else:
            print('last history is not today',today,que[0].Date,que[0].player.user.username,flush=True)
        return

    for history in que:
        #set amount
        for el in history.quant.keys():
            if(el=="_cash"):
                history.amount[el]=history.quant[el]
            else:
                if(not (el in lastprice)):
                    try:
                        tickerObj = Ticker.objects.get(ticker=el)
                        updateTicker(tickerObj)
                        lastprice[el]=tickerObj.last_price
                    except:
                        print("No price found for %s %s" % (el,str(self.Date)))
                        lastprice[el]=0
                history.amount[el]=lastprice[el]*history.quant[el]

        #set asset
        history.asset = 0
        for val in history.amount.values():
            history.asset += val
        history.save()

    connection.close()

def updateALL(date,lastprice_set=None):

    if(not lastprice_set):
        lastprice_set={}

    ticker_que=Ticker.objects.exclude(ticker__in=["_QUECONTROL","WORK"])
    player_que=Player.objects.all()

    today=timezone.now().date()
    print(" === update ticker",flush=True)
    for ticker in ticker_que:
        updateTicker(ticker)
        lastprice_set[ticker.ticker]=ticker.last_price

    if(date!=today):
        print(" === new day update player",today,flush=True)
        for player in player_que:
            player.makeHistory(pfchange={str(date):player.portfolio.copy()})
        for ticker in ticker_que:
            lastprice_set[ticker.ticker]=ticker.last_price
        return today, lastprice_set


    print(" === update player",flush=True)
    history_que=AssetHistory.objects.filter(Date=date)
    for player in player_que:
        if(history_que.filter(player=player).exists()):
            history = history_que.get(player=player)
            history.quant=player.portfolio.copy()
            #set amount and asset
            history.asset = 0
            history.amount={}
            for ticker in history.quant.keys():
                if(ticker=="_cash"):
                    history.amount[ticker]=history.quant[ticker]
                else:
                    if((ticker in lastprice_set) and (ticker in history.quant)):
                        history.amount[ticker]=lastprice_set[ticker]*history.quant[ticker]
                    else:
                        history.amount[ticker]=0
                history.asset += history.amount[ticker]
            history.save()
        else:
            print(" === catchupHistory - ",player,flush=True)
            player.catchupHistory()
    return today, lastprice_set


EACH_TASK_TIME = 10
TRIGGER_ITERATIONS = 10

def elapsedtime(currenttime,task_time=EACH_TASK_TIME):
    newtime=time.time()
    dt=newtime-currenttime
    print("{:.4f}".format(dt),flush=True)
    if(dt<task_time):
        time.sleep(task_time-dt)
    newtime=time.time()
    return newtime

def quetrigger(seconds):
    qc=Ticker.objects.get(ticker="_QUECONTROL")
    target=timezone.now()+datetime.timedelta(seconds=seconds)
    if(qc.last_date<target):
        qc.last_date=target
        qc.save()

#@async_thread
# def quetrigger(max_iters=TRIGGER_ITERATIONS):
#     # qc=Ticker.objects.get(ticker="_QUECONTROL")
#     # ident=None
#     # if(qc.name!='_INACTIVE'):
#     #     ident=int(qc.name[8:])
#     #     for thr in threading.enumerate():
#     #         if(ident==thr.ident):
#     #             print("thread already running",flush=True)
#     #             return
#     #     print("previous thread "+str(ident)+" dead")
#     # ident=threading.get_ident()
#     # threadname='_ACTIVE:'+str(ident)
#     # qc.name=threadname
#     # qc.save()

#     today=timezone.now().date()
#     ls={}

#     #####TIME STAMP 0
#     currenttime=time.time()
#     print("TIMESTAMP0",flush=True)
#     #####

#     for i in range(max_iters):
#         if(Ticker.objects.get(ticker="_QUECONTROL").name!=threadname):
#             return
#         print(i,flush=True)
#         today, ls = updateALL(today,ls)

#         #####TIME STAMP i
#         print("TIMESTAMP"+str(i+1))
#         currenttime=elapsedtime(currenttime)
#         print(currenttime,flush=True)
#         #####

#     # qc=Ticker.objects.get(ticker="_QUECONTROL")
#     # qc.name=='_INACTIVE'
#     # qc.save()