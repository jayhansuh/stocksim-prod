from django.shortcuts import render
from django.contrib.auth.models import User
from portfolio.models import Player

# Create your views here.
from django.contrib.auth.decorators import login_required
from stockdb.models import Ticker

import re

def mobile(request):
    """Return True if the request comes from a mobile device."""

    MOBILE_AGENT_RE=re.compile(r".*(iphone|mobile|androidtouch)",re.IGNORECASE)

    if MOBILE_AGENT_RE.match(request.META['HTTP_USER_AGENT']):
        return True
    else:
        return False

def getFavrtTickers(request, num_full = 10):

    favrt_tickers = []
    if (request.user.is_authenticated):
        try:
            username = request.user.username
            p=User.objects.get(username=username).player_set.all()[0]
            favrt_tickers = p.favrt_ticker.all()
        except:
            favrt_tickers = []
    
    ticker_list = [Ticker.objects.get(ticker='^GSPC')]
    num_in = 1

    for ticker in favrt_tickers:
        ticker_list.append(ticker)
        num_in +=1 
        if(num_in == num_full):
            break
    
    if(num_in < num_full):
        exclude_lst = ['^GSPC','_QUECONTROL','WORK']+list(favrt_tickers)
        ticker_list += list(Ticker.objects.order_by('-last_date').exclude(ticker__in=exclude_lst)[:num_full-num_in])
    
    return ticker_list

def index(request):

    template='home/homepage_hexabin.html'
    if(mobile(request) or request.GET.get('mobile')):
        print('mobile')
        template='home/homepage_mobile.html'


    return render(request, template,{
        'is_main':True,
        'ticker_list':getFavrtTickers(request),
        'title':'Home',
        'help' : request.GET.get('help')
})

def construction(request):
    return render(request, 'home/construction.html',{
        'construction_msg': "UNDER CONSTRUCTION"
})
