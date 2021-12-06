from django.shortcuts import render, redirect
from django.http import JsonResponse
from stockdb.models import Ticker
from stockdb.makedb import updateTicker,setTicker
from stockdb.views import indtodate, datetoind
from portfolio.models import Player, Transaction
from portfolio.scheduler import quetrigger

from django.utils import timezone
import datetime, json, random, hashlib
from django import forms

app_list=[
    {'name':'SWING TRADE GAME','url':'/simulator/chartsurf/'},
    {'name':'History Plot','url':'/simulator/histplot/datagen'},
    {'name':'QUANT LAB','url':'/simulator/qlab/'},
]
def simmenu(request):
    return render(request,'simulator/simmenu.html',{'app_list':app_list,'title':'Simulator'})

def chartsurf(request):
  tickerObj=Ticker.objects.get(ticker="^GSPC")
  return render(request,'simulator/chartsurf.html',{
            'tickerObj' : tickerObj,
            'title': 'Swing Game'})

class GainForm(forms.Form):
  OHUQ = forms.CharField(label='un', max_length=100, required=True)
  AGLW = forms.IntegerField(label="amt", required=True)


def getOHUQ(string):
  bytearr = bytes(string, 'utf-8')
  hash_object = hashlib.sha256(bytearr)
  hex_dig = hash_object.hexdigest()
  return hex_dig

def genOHUQ_old(string):
  return getOHUQ( "suhh" + string + str(timezone.now().date()))

def checkOHUQ_old(username,key):
  if(getOHUQ( "suhh" + username + str(timezone.now().date()))==key):
    return True
  return (getOHUQ( "suhh" + username + str(timezone.now().date()-datetime.timedelta(days=1)))==key)

def genOHUQ(string):
  
  salt = hex(int(random.random()*(65536-4096) + 4096))[2:]
  if(len(salt)!=4):
    salt='e5a9'
  
  timestamp=str(timezone.now())
  if(len(timestamp)!=32):
    timestamp='1900-00-00 00:00:00.000000+00:00'
  
  return timestamp + salt + getOHUQ( salt + "ITZY" + string + timestamp)

def checkOHUQ(key,hashstr):
  timestamp = hashstr[:32]
  salt = hashstr[32:36]
  hashstr = hashstr[36:]
  return (getOHUQ( salt + "ITZY" + key + timestamp)==hashstr)

def chartsurf_nofetch(request):

  alert_msg = None
  if (request.method == 'POST'):
    if(request.user.is_authenticated):
      form = GainForm(request.POST)
      if(form.is_valid() and checkOHUQ(request.user.username,form.cleaned_data['OHUQ'])):
        player = Player.objects.get(user__username=request.user.username)
        if((player.assethistory_set.filter(code__gt=0).order_by('-Date')[0]).asset>200000):
          alert_msg = 'Level greater than 2(>200k)<br>cannot earn DAILY GAIN'
        else:
          max_earning = 1000*100
          todayhist = player.transaction_set.filter(ticker='_swing',pub_date__date=timezone.now().date(),validation='SUCCESS').order_by('-pub_date')
          maxtime = timezone.now() - datetime.timedelta(seconds=109)
          if(str(maxtime)<form.cleaned_data['OHUQ'][:32] or
            (todayhist.exists() and maxtime < todayhist[0].pub_date)):
            alert_msg = 'ERROR - INVALID FORM'
          else:
            for el in todayhist.values('quantity','price'):
              max_earning -= round( el['price'] * 100)
            if( max_earning <= 0 ):
              alert_msg = 'You already reached<br>the MAX DAILY GAIN(1k)'
            else:
              earning = int(form.cleaned_data['AGLW'])
              if(earning > 0):
                trns=Transaction(player = player ,
                  pub_date = timezone.now(),
                  ticker = '_swing',
                  quantity = 1,
                  price = min( max_earning , earning ) / 100)
                alert_msg = trns.applyTransaction(player.portfolio)
                trns.save()
                if(alert_msg=="TRANSACTION_SUCCESS"):
                  player.save()
                  quetrigger(100)
                  return redirect('/simulator/chartsurf/')
      else:
        alert_msg = 'ERROR - INVALID FORM'
    else:
      alert_msg = 'LOG IN IS REQUIRED TO SAVE'

  window_size = 200
  strt_date = random.randint( 30976 , datetoind(timezone.now().date()) - 365 - window_size - 15 )
  ticker = random.choice(['^GSPC' , '^IXIC' , '^DJI'])
  
  que = Ticker.objects.get(ticker=ticker).dayprice_set.filter(Date__gte=indtodate(strt_date)).order_by('Date')[: 365 + window_size + 14]

  date_ptr=que[0].Date
  res={'strt_date':datetoind(date_ptr),
    'High':[],
    'Low':[],
    'Open':[],
    'Close':[],}

  que = que.values(*('Date','Open','Close','High','Low',))
  oneday=datetime.timedelta(days=1)
  for q in que:
      while(date_ptr<q['Date']):
          for key in ('Open','Close','High','Low',):
              res[key].append(None)
          date_ptr+=oneday
      for key in ('Open','Close','High','Low',):
          res[key].append(q[key])
      date_ptr+=oneday

  return render(request,'simulator/chartsurf_nofetch.html',{
            'fetchedDat' : res ,
            'ticker' : ticker ,
            'form' : GainForm(initial={'OHUQ':genOHUQ(request.user.username)}),
            'title': 'Swing Game',
            'alert_msg':alert_msg,
            'redirect':(alert_msg=='ERROR - INVALID FORM')})

def qlab(request):
  return render(request,'home/construction.html',{'title':'Quant Lab','construction_msg': 'Under Construcstion'})

def historyplot(request,protocol):

    req = json.loads(request.GET.get('req',"{}"))

    # parse mag_ratio
    mag_ratio = 10.
    if('mag_ratio' in req):
        mag_ratio=req['mag_ratio']
        if( not ( (type(mag_ratio) in (int,float)) and mag_ratio>0 and mag_ratio<100)):
            mag_ratio = 10.

    # parse hist_list
    hist_list=None
    if('data' in req):
        try:
            hist_list=req['data']
            if(type(hist_list)==str):
                hist_list=json.loads(hist_list)
            gen_hist_amount(hist_list)
        except:
            return render(request, 'simulator/history_datagen.html', {
                'history_list':False,
            })

    # parse protocol
    if(protocol=='plot'):
        # if there is no data then plot mine(acutal US bank history)
        if(hist_list==None):
            hist_list=myhist_list_compiled
            mag_ratio=7
        # convert date string to date object
        for hist in hist_list:
            if(type(hist['Date']) is str):
                arr=list(map(int,hist['Date'].split("-")))
                hist['Date']=datetime.datetime(arr[0],arr[1],arr[2])
        # this burrows the historyview template from the portfolio app
        return render(request, 'portfolio/historyview.html', {
            'title_nav':False,
            'mag_ratio':mag_ratio,
            'history_list':hist_list,
        })
    elif(protocol=='datagen'):
        return render(request, 'simulator/history_datagen.html', {
            'history_list':hist_list,
        })

    return render(request,'home/construction.html',{
            'css_style':'font-size:16px;',
            'construction_msg': 'Unrecognized protocol'})

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
