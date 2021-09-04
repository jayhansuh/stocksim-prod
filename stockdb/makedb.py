import yfinance as yf
import numpy as np
from .models import Ticker, DayPrice
from django.utils import timezone
import sys
import time

# def elapsedtime(currenttime):
#     newtime=time.time()
#     print("{:.4f}".format(newtime-currenttime),flush=True)
#     return newtime

def updateTicker(tickerObj,period="automatic",overwrite=False,timedelay=True):

    #print(tickerObj.ticker,flush=True)

    ######TIME STAMP 0
    #currenttime=time.time()
    #print("TIMESTAMP0",flush=True)
    ######

    try:
        if(tickerObj.last_date==None):
            print("First initialization for %s" % (tickerObj.ticker))
            period="max"

        if(period=="automatic"):
            timedelta=timezone.now()-tickerObj.last_date
            #no update if it has updated less than a min before
            if(timedelay and timedelta.seconds<8):
                return
            #convert the days value for the yfinance package name rule
            for p in [(5,'5d'),(28,'1mo'),(85,'3mo'),(170,'6mo'),
                (360,'1y'),(360*2,'2y'),(360*5,'5y'),(360*10,'10y'),(float('inf'),'max')]:
                if(timedelta.days<p[0]):
                    period=p[1]
                    break

        #################################  DONT FORGET TO COMMENT THIS FOR PRODUCTION!
        #time.sleep(1) ##################  SIMULATE TIME DELAY FOR UPDATE
        #################################  DONT FORGET TO COMMENT THIS FOR PRODUCTION!

        #fetch the data
        yfobj = yf.Ticker(tickerObj.ticker)
        dataFrame=yfobj.history(period=period,interval="1d")
        if(len(dataFrame)==0):
            print("No dataframe found for %s" % (tickerObj.ticker))
            return

        #update last_date
        last_date=tickerObj.last_date
        if(last_date):
            last_date=last_date.date()
        tickerObj.last_date=timezone.now()

        ######TIME STAMP 2
        #print("TIMESTAMP2")
        #currenttime=elapsedtime(currenttime)
        ######

        daypriceObjs=tickerObj.dayprice_set
        db_dayprice=[]
        todayprice=None
        for index, row in dataFrame.iterrows():
            if( overwrite or ( not daypriceObjs.filter(Date=index).exists() )):

                if not np.isnan(row['Close']):
                    db_dayprice.append(DayPrice(
                        ticker=tickerObj,

                        Date = index,
                        Open = row['Open'],
                        High = row['High'],
                        Low = row['Low'],
                        Close = row['Close'],

                        Volume = row['Volume'],
                        Dividends = row['Dividends'],
                        Split = row['Stock Splits']
                    ))
                    db_dayprice[-1].save()

            elif(index==last_date):
                todayprice=daypriceObjs.filter(Date=last_date)[0]


                todayprice.Open = row['Open']
                todayprice.High = row['High']
                todayprice.Low = row['Low']
                todayprice.Close = row['Close']

                todayprice.Volume = row['Volume']
                todayprice.Dividends = row['Dividends']
                todayprice.Split = row['Stock Splits']
                todayprice.save()

        #DayPrice.objects.bulk_create(db_dayprice)
        tickerObj.last_price=tickerObj.dayprice_set.order_by('-Date')[0].Close
        tickerObj.save()

    except:
        print("updateTicker not working!!!",flush=True)
        print(tickerObj.ticker,flush=True)
        print(sys.exc_info()[0],flush=True)

def setTicker(ticker):
    yfobj = yf.Ticker(ticker)

    yfobjinfo= yfobj.info if(yfobj) else None

    if(yfobjinfo==None or not('shortName' in yfobjinfo)):
        print(ticker+": No data found, symbol may be delisted",flush=True)
        return None

    if (Ticker.objects.filter(ticker=yfobj.ticker).exists()):
        db_ticker=Ticker.objects.get(ticker=yfobj.ticker)
        db_ticker.name=yfobjinfo.get('shortName',"")
        db_ticker.sector=yfobjinfo.get('sector',"")
        db_ticker.exchange=yfobjinfo.get('exchange',"")
        db_ticker.currency=yfobjinfo.get('currency',"")
    else:
        sname=yfobjinfo.get('shortName',"")
        if(Ticker.objects.filter(name=sname).exists()):
            sname += "("+yfobj.ticker+")"
        db_ticker = Ticker(
            ticker=yfobj.ticker,
            name=sname,
            sector=yfobjinfo.get('sector',""),
            exchange=yfobjinfo.get('exchange',""),
            currency=yfobjinfo.get('currency',""),
            pub_date=timezone.now(),
            last_date=None
        )
    db_ticker.save()

    #updateTicker(db_ticker)

    return db_ticker

def get_last_price(ticker,dbaccess=False):
    ticker_yahoo = yf.Ticker(ticker)
    data = ticker_yahoo.history()
    last_quote = (data.tail(1)['Close'].iloc[0])
    return last_quote