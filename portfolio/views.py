from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse, Http404, HttpResponseRedirect
from django.views import generic
from django.utils import timezone
from django.contrib.auth.models import User

# Create your views here.

from .models import Player, Transaction, AssetHistory
from django.contrib.auth.decorators import login_required
from .forms import TransactionForm

from stockdb.models import Ticker
from stockdb.makedb import get_last_price
from agora.models import MemoTag
from portfolio.scheduler import quetrigger

import math

appnameset={
    'overview',
    'history',
    'transactions',
}

example_username="example_user"

####################
color_order=[
    "MRNA" ,
    "W"  ,
    "MU"  ,
    "NVDA"  ,
    "INTC"  ,
    "BABA"  ,
    "OB" ,
    "VSAT" ,
    "ILMN" ,
    "SJR" ,
    "MSFT" ,
    "SHOP" ,
    "AAPL" ,
    "GOOGL" ,
    "PDD" ,
    "FB" ,
    "TTD" ,
    "SPOT" ,
    "LBTYK" ,
    "GOOG" ,
    "_cash" ,
    "NFLX" ,
    "QRVO" ]
color_order_players = ['BAILLIE_GIFFORD','BAUPOST','jj']
####################

def indexView(request):
    if(request.user.is_authenticated):
        return redirect("/portfolio/profile/"+request.user.username)
    return HttpResponseRedirect('/portfolio/history/'+example_username)

#@login_required
def redirectSubApp(request,subappname):
    if(subappname not in appnameset):
        raise Http404(subappname+" is not one of app names: "+str(list(appnameset)))
    elif(request.user.is_authenticated):
        return redirect("/portfolio/"+subappname+"/"+request.user.username)
    else:
        return redirect("/portfolio/"+subappname+"/"+example_username)

class HistoryView(generic.ListView):
    #quetrigger(100)
    #This one automatically triggers it
    template_name = 'portfolio/historyview.html'
    context_object_name = 'history_list'

    def get_context_data(self, **kwargs):
        context = super(HistoryView, self).get_context_data(**kwargs)
        context['title']='History'
        context['username']=self.kwargs['username']
        context['title_nav'] = True
        context['isfollowed'] = isfollowed(self.request,self.kwargs['username'])
        return context

    def get_queryset(self):
        #if (self.request.user.is_authenticated or self.kwargs['username']==example_username):
        player = User.objects.get(username=self.kwargs['username']).player_set.all()[0]
        #async_thread(player.makeHistory)()
        queryset = player.assethistory_set.filter(code__gte=2).order_by('Date')
        ####################
        if(self.kwargs['username'] in color_order_players):
            for last_history in queryset:
                newamt={}
                for t in color_order:
                    if(t in last_history.amount):
                        newamt[t]=last_history.amount[t]
                for t in last_history.amount:
                    if(not (t in newamt)):
                        newamt[t]=last_history.amount[t]
                if(len(newamt)==len(last_history.amount)):
                    last_history.amount = newamt
        ####################
        return queryset
        #else:
        #    return redirect("/accounts/login/?next=/portfolio/history/"+self.kwargs['username'])

def isfollowed(request,username):
    isfollowed = False
    if request.user.is_authenticated:
        myname = request.user.username
        me=User.objects.get(username=myname).player_set.all()[0]
        whotofollow = User.objects.get(username=username).player_set.all()[0]
        isfollowed = me.following.filter(pk=whotofollow.pk).exists()
    return isfollowed

def ProfileView(request,username):
    quetrigger(100)
    player=User.objects.get(username=username).player_set.all()[0]
    #async_thread(player.makeHistory)()
    last_history=player.assethistory_set.filter(code__gt=0).order_by('-Date')[0]
    ####################
    if(username in color_order_players):
        newamt={}
        for t in color_order:
            if(t in last_history.amount):
                newamt[t]=last_history.amount[t]
        for t in last_history.amount:
            if(not (t in newamt)):
                newamt[t]=last_history.amount[t]
        if(len(newamt)==len(last_history.amount)):
            last_history.amount = newamt
    ####################
    portfolioOverview=[]
    for ticker in last_history.quant:
        quantity = last_history.quant[ticker]
        value = last_history.amount[ticker]
        portfolioOverview.append({
            'ticker': ticker if ticker!='_cash' else "Cash(USD)",
            'quantity': str(quantity) if ticker!='_cash' else "NA",
            'value': value,
            'price': "{:.2f}".format(value/quantity),
            'weight': "{:.1f}".format(value/last_history.asset*100),
        })
    portfolioOverview.sort(reverse=True, key=(lambda x : x['value']))
 
    return render(request, 'portfolio/profile.html', {
                    'title':'Overview',
                    'username':username,
                    'title_nav' : {'img':getBadge(last_history.asset,'width:200px;')},
                    'last_history':last_history,
                    'transaction_list' : player.transaction_set.order_by('-pub_date'),
                    'memo_list' : MemoTag.getMemos(tag=username),
                    'asset' : last_history.asset,
                    'portfolioOverview' : portfolioOverview,
                    'isfollowed': isfollowed(request,username),
                    'portfolio' : player.portfolio,
                })

#@login_required
def PortfolioView(request,username):
    quetrigger(100)
    player=User.objects.get(username=username).player_set.all()[0]
    #async_thread(player.makeHistory)()
    last_history=player.assethistory_set.filter(code__gt=0).order_by('-Date')[0]
    ####################
    if(username in color_order_players):
        newamt={}
        for t in color_order:
            if(t in last_history.amount):
                newamt[t]=last_history.amount[t]
        for t in last_history.amount:
            if(not (t in newamt)):
                newamt[t]=last_history.amount[t]
        if(len(newamt)==len(last_history.amount)):
            last_history.amount = newamt
    ####################
    portfolioOverview=[]
    for ticker in last_history.quant:
        quantity = last_history.quant[ticker]
        value = last_history.amount[ticker]
        portfolioOverview.append({
            'ticker': ticker if ticker!='_cash' else "Cash(USD)",
            'quantity': str(quantity) if ticker!='_cash' else "NA",
            'value': value,
            'price': "{:.2f}".format(value/quantity),
            'weight': "{:.1f}".format(value/last_history.asset*100),
        })
    portfolioOverview.sort(reverse=True, key=(lambda x : x['value']))
 
    return render(request, 'portfolio/overview.html', {
                    'title':'Overview',
                    'username':username,
                    'title_nav' : {'img':getBadge(last_history.asset)},
                    'last_history':last_history,
                    'transaction_list' : player.transaction_set.order_by('-pub_date'),
                    'memo_list' : MemoTag.getMemos(tag=username),
                    'asset' : last_history.asset,
                    'portfolioOverview' : portfolioOverview,
                    'isfollowed': isfollowed(request,username),
                })

def trnsrender(request,player,form,trnsstatus):
    return render(request, 'portfolio/transactionsview.html', {
                    'title_nav' : True,
                    'transaction_list' : player.transaction_set.order_by('-pub_date')[:12],
                    'portfolio' : player.portfolio,
                    'anotheruser' : player.user.username if request.user.pk!=player.user.pk else False,
                    'trnsstatus' : trnsstatus,
                    'form' : form,
                    'title':'Transactions',
                    'username': player.user.username,
                })

#@login_required
def TransactionsView(request,username):
    trnsresult="NA"

    player=User.objects.get(username=username).player_set.all()[0]

    if (request.user.is_authenticated and request.method == 'POST'):
        form = TransactionForm(request.POST)
        if form.is_valid() and request.user.pk==player.user.pk:
            trnsresult=form.makeTransaction(player)
            if(trnsresult!="TRANSACTION_SUCCESS"):
                return trnsrender(request,player,form,trnsresult)
            return redirect("/portfolio/transactions/"+username)
        else :
            return trnsrender(request,player,form,"TRANSACTION_FAIL_InvalidForm")

    form = TransactionForm()
    return trnsrender(request,player,form,trnsresult)
    #return redirect("/accounts/login/?next=/portfolio/transactions/"+username)

#@login_required
def getPortfolio(request):
    try:
        obj=Player.objects.get(user__username = request.GET.get('username'))
    except Player.DoesNotExist:
        print("Player %s DoesNotExist"%(request.GET.get('username')),flush=True)
        return JsonResponse({"ERROR":"NO PLAYER FOUND"}, json_dumps_params={'indent': 2})
    return JsonResponse(obj.portfolio, json_dumps_params={'indent': 2})

def RankingHelp(request):
    return render(request, 'portfolio/rankinghelp.html', {
                    'title_nav' : True,
                    'title': 'Ranking Intro',
                })

def getBadge(asset,style_string="width: 25px;"):
    envelope = [
        '<a href="/portfolio/ranking/help/"><svg style="'+style_string+'" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">',
        '<path class="badge" d="',
        '" style="fill: #d2ebf9;stroke:none;filter:drop-shadow(0px 0px 14px rgb(255 255 255 / 0.7));"></path></svg></a>',
    ]
    badgelist=[
        'M 50.000 25.000 L 78.868 75.000 L 21.132 75.000 Z',
        'M 75.000 25.000 L 75.000 75.000 L 25.000 75.000 L 25.000 25.000 Z',
        "M 50.000 25.000 L 76.287 44.098 L 66.246 75.000 L 33.754 75.000 L 23.713 44.098 Z",
        "M 64.434 25.000 L 78.868 50.000 L 64.434 75.000 L 35.566 75.000 L 21.132 50.000 L 35.566 25.000 Z",
        'M 50.000 25.000 L 70.564 34.903 L 75.643 57.155 L 61.412 75.000 L 38.588 75.000 L 24.357 57.155 L 29.436 34.903 Z',
        'M 60.355 25.000 L 75.000 39.645 L 75.000 60.355 L 60.355 75.000 L 39.645 75.000 L 25.000 60.355 L 25.000 39.645 L 39.645 25.000 Z',
        'M 50.000 25.000 L 66.569 31.031 L 75.386 46.301 L 72.324 63.666 L 58.816 75.000 L 41.184 75.000 L 27.676 63.666 L 24.614 46.301 L 33.431 31.031 Z',
        'M 58.123 25.000 L 71.266 34.549 L 76.287 50.000 L 71.266 65.451 L 58.123 75.000 L 41.877 75.000 L 28.734 65.451 L 23.713 50.000 L 28.734 34.549 L 41.877 25.000 Z',
        'M 50.000 25.000 L 63.795 29.051 L 73.211 39.917 L 75.257 54.148 L 69.284 67.227 L 57.189 75.000 L 42.811 75.000 L 30.716 67.227 L 24.743 54.148 L 26.789 39.917 L 36.205 29.051 Z',
        'M 56.699 25.000 L 68.301 31.699 L 75.000 43.301 L 75.000 56.699 L 68.301 68.301 L 56.699 75.000 L 43.301 75.000 L 31.699 68.301 L 25.000 56.699 L 25.000 43.301 L 31.699 31.699 L 43.301 25.000 Z',
    ]
    n=math.floor(3 * math.log2(asset/100000))
    if(n<0):
        n=0
    if(n>len(badgelist)-1):
        return envelope[0]+'<circle style="fill: black;stroke:none;filter:drop-shadow(0px 0px 11px rgb(255 255 255 / .9));" cx="50" cy="50.000" r="25.000"></circle></svg></a>'
    return envelope[0] + envelope[1] + badgelist[n] + envelope[2]

def AddFollowing(request,username):
    if not request.user.is_authenticated:
        raise Http404("The user does not log-in")
    else:    
        myname = request.user.username
        me=User.objects.get(username=myname).player_set.all()[0]
        whotofollow = User.objects.get(username=username).player_set.all()[0]
        isfollowed = me.following.filter(pk=whotofollow.pk).exists()
        if isfollowed:
            me.following.remove(whotofollow)
        else:
            me.following.add(whotofollow)
        me.save()
    return redirect('portfolio:overview',username)