from django.shortcuts import render

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


def index(request):

    template='home/homepage.html'
    if(mobile(request) or request.GET.get('mobile')):
        print('mobile')
        template='home/homepage_mobile.html'

    ticker_list = [Ticker.objects.get(ticker='^GSPC')]

    ticker_list += list(Ticker.objects.order_by('-last_date').exclude(ticker__in=['^GSPC','_QUECONTROL','WORK'])[:9])
    return render(request, template,{
        'is_main':True,
        'ticker_list':ticker_list,
        'title':'Home',
        'help' : request.GET.get('help')
})

def construction(request):
    return render(request, 'home/construction.html',{
        'construction_msg': "UNDER CONSTRUCTION"
})
