from django.utils import timezone
from portfolio.scheduler import *
import time
import datetime
import threading
import yfinance as yf
from portfolio.models import *
from stockdb.models import *
from stockdb.makedb import *

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
                    ticker=ticker.upper()
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

EACH_TASK_TIME = 30
TRIGGER_ITERATIONS = 100

def elapsedtime(currenttime,task_time=EACH_TASK_TIME):
    newtime=time.time()
    dt=newtime-currenttime
    print("{:.4f}".format(dt),flush=True)
    if(dt<task_time):
        time.sleep(task_time-dt)
    newtime=time.time()
    return newtime

def main():
    #
    today=timezone.now().date()
    ls={}
    #
    #####TIME STAMP 0
    currenttime=time.time()
    print("TIMESTAMP0",flush=True)
    #####
    #
    last_date=None
    #
    while(True):
        #
        target_date=Ticker.objects.get(ticker="_QUECONTROL").last_date
        if(target_date==None or target_date.date().year<2000):
            break
        #    
        #####TIME STAMP 0
        currenttime=time.time()
        print("TIMESTAMP0",flush=True)
        #####
        if(timezone.now()<target_date):
            today, ls = updateALL(today,ls)
            #####TIME STAMP i
            print("TIMESTAMP1",flush=True)
            currenttime=elapsedtime(currenttime,10)
            print(currenttime,flush=True)
            #####
        else:
            time.sleep(EACH_TASK_TIME)

def killsch():
    qc=Ticker.objects.get(ticker="_QUECONTROL")
    qc.last_date=timezone.now()
    days=(qc.last_date.year-1995)*365
    qc.last_date=qc.last_date-datetime.timedelta(days=days)
    qc.save()

main()