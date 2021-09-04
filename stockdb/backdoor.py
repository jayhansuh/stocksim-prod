from django.shortcuts import render
from django.http import JsonResponse
from .models import Ticker
from .makedb import updateTicker,setTicker
import datetime, json


def backdoorIndex(request,req):
    protocol=req['LAB'].split(":")
    if(protocol[0]=='histplot'):
        
        hist_list=None
    
        mag_ratio = 10.
        if('mag_ratio' in req):
            mag_ratio=req['mag_ratio']
            if( not ( (type(mag_ratio) in (int,float)) and mag_ratio>0 and mag_ratio<100)):
                mag_ratio = 10.
    
        if('data' in req):
            try:
                hist_list=req['data']
                if(type(hist_list)==str):
                    hist_list=json.loads(hist_list)
                gen_hist_amount(hist_list)
            except:
                return render(request, 'portfolio/history_datagen.html', {
                   'history_list':False,
                })
        
        if(len(protocol)<2):
            if(hist_list==None):
                hist_list=myhist_list_compiled
                mag_ratio=7
            for hist in hist_list:
                if(type(hist['Date']) is str):
                    arr=list(map(int,hist['Date'].split("-")))
                    hist['Date']=datetime.datetime(arr[0],arr[1],arr[2])
            return render(request, 'portfolio/historyview.html', {
                'title_nav':False,
                'mag_ratio':mag_ratio,
                'history_list':hist_list,
            })
        elif(protocol[1]=='datagen'):
            return render(request, 'portfolio/history_datagen.html', {
                'history_list':hist_list,
            })
        
    return render(request,'home/construction.html',{
            'css_style':'font-size:16px;',
            'construction_msg': 'Unrecognized protocol - ' + str(protocol)})

####################################################################################
hist_list_example=[
    {
        'Date':'2020-06-30',
        'quant':{'GOOGL':3,'DAL':72,'ZM':9,'AMD':36},
    },
    {
        "Date": "2020-09-30",
        "quant": {
            "GOOGL": 1,
            "AMD": 36,
            "COST": 7,
            "MRNA": 10,
            "_cash": 4000.,
        },
    }
]
myhist_list_compiled=[
  {
    "Date": "2020-06-30",
    "quant": {
      "GOOGL": 3,
      "AMD": 36,
      "DAL": 72,
      "ZM": 9
    },
    "amount": {
      "GOOGL": 4254.150146484375,
      "AMD": 1893.9600219726562,
      "DAL": 2019.5999450683594,
      "ZM": 2281.8599395751953
    },
    "asset": 10449.570053100586
  },
  {
    "Date": "2020-09-30",
    "quant": {
      "GOOGL": 1,
      "AMD": 36,
      "COST": 7,
      "MRNA": 10,
      "SHORT/OPT": 3653.0
    },
    "amount": {
      "GOOGL": 1465.5999755859375,
      "AMD": 2951.639923095703,
      "COST": 2402.5028381347656,
      "MRNA": 707.5,
      "SHORT/OPT": 3653.0
    },
    "asset": 11180.242736816406
  },
  {
    "Date": "2020-12-31",
    "quant": {
      "AMD": 39,
      "COST": 7,
      "MRNA": 10,
      "SHORT/OPT": 3678.0
    },
    "amount": {
      "AMD": 3576.6899642944336,
      "COST": 2621.7213134765625,
      "MRNA": 1044.7000122070312,
      "SHORT/OPT": 3678.0
    },
    "asset": 10921.111289978027
  },
  {
    "Date": "2021-03-31",
    "quant": {
      "AMD": 51,
      "COST": 15,
      "MRNA": 29,
      "O": 15,
      "GSG": 40,
      "RJI": 100
    },
    "amount": {
      "AMD": 4003.5,
      "COST": 5266.0272216796875,
      "MRNA": 3797.5499114990234,
      "O": 939.5460891723633,
      "GSG": 558.8000106811523,
      "RJI": 548.9999771118164
    },
    "asset": 15114.423210144043
  },
  {
    "Date": "2021-06-30",
    "quant": {
      "AMD": 51,
      "COST": 15,
      "MRNA": 29,
      "O": 15,
      "GSG": 40,
      "RJI": 100
    },
    "amount": {
      "AMD": 4790.430015563965,
      "COST": 5923.9453125,
      "MRNA": 6814.419876098633,
      "O": 997.7354049682617,
      "GSG": 643.6000061035156,
      "RJI": 634.9999904632568
    },
    "asset": 19805.130605697632
  },
  {
    "Date": "2021-08-01",
    "quant": {
      "AMD": 51,
      "COST": 15,
      "MRNA": 29,
      "O": 15,
      "GSG": 40,
      "RJI": 100
    },
    "amount": {
      "AMD": 5415.690124511719,
      "COST": 6445.800018310547,
      "MRNA": 10254.400177001953,
      "O": 1054.3500137329102,
      "GSG": 651.9999694824219,
      "RJI": 642.9999828338623
    },
    "asset": 24465.240285873413
  }
]

# from stockdb.backdoor import *
# gen_hist_amount(myhist_list)
# print(hist_stringfy(myhist_list))

####################################################################################
# myhist_list=[
#     {
#         'Date':datetime.datetime(2020, 6, 30).date(),
#         'quant':{'GOOGL':3,'DAL':72,'ZM':9,'AMD':36},
#     },
#     {
#         'Date':datetime.datetime(2020, 9, 30).date(),
#         'quant':{'GOOGL':1,'AMD':36,'COST':7,'MRNA':10,'SHORT/OPT':3653.},
#     },
#     {
#         'Date':datetime.datetime(2020, 12, 31).date(),
#         'quant':{'AMD':39,'COST':7,'MRNA':10,'SHORT/OPT':3678.},
#     },
#     {
#         'Date':datetime.datetime(2021, 3, 31).date(),
#         'quant':{'AMD':51,'COST':15,'MRNA':29,'O':15,'GSG':40,'RJI':100},
#     },
#     {
#         'Date':datetime.datetime(2021, 6, 30).date(),
#         'quant':{'AMD':51,'COST':15,'MRNA':29,'O':15,'GSG':40,'RJI':100},
#     },
#     {
#         'Date':datetime.datetime(2021, 8, 1).date(),
#         'quant':{'AMD':51,'COST':15,'MRNA':29,'O':15,'GSG':40,'RJI':100},
#     },
# ]


def hist_stringfy(hist_list):
    new_list=[]
    for hist in hist_list:
        new_list.append(hist.copy())
        new_list[-1]['Date']=str(new_list[-1]['Date'])
    return json.dumps(new_list,indent=2)

def gen_hist_amount(hist_list):
    tickerObjs={}
    price=1
    tickerObj=None
    for hist in hist_list:
        if('amount' in hist):
            continue
        hist['amount']={}
        hist['asset']=0        
        for ticker in hist['quant']:
            if(ticker=="_cash" or ticker=="SHORT/OPT"):
                price = 1
            else:
                if(ticker in tickerObjs):
                    tickerObj=tickerObjs[ticker]
                else:
                    tickerObj=Ticker.objects.filter(ticker=ticker)
                    if(not tickerObj.exists()):
                        tickerObj = setTicker(ticker)
                    else:
                        tickerObj=tickerObj[0]
                    if(tickerObj!=None):
                        updateTicker(tickerObj)
                    tickerObjs[ticker]=tickerObj

                if(tickerObj!=None):
                    price=tickerObj.dayprice_set.filter(Date__lte=hist['Date']).order_by('-Date')[0].Close
                else:
                    price=0
                
            hist['amount'][ticker]=price*hist['quant'][ticker]
            hist['asset']+=hist['amount'][ticker]
                

# from stockdb.backdoor import *
# gen_hist_amount(myhist_list)
# print(hist_stringfy(myhist_list))
