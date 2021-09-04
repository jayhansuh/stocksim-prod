from django.shortcuts import render
from django.http import HttpResponseRedirect

# Create your views here.
from django.contrib.auth.decorators import login_required
from stockdb.models import Ticker
from portfolio.models import Player
from .models import Memo, MemoTag
from .forms import MemoForm
from django.http import JsonResponse
from stockdb.makedb import setTicker

from portfolio.scheduler import quetrigger

def index(request):
    quetrigger(100)
    context={}

    if(request.user.is_authenticated):
        pass

    context['ticker_list'] = Ticker.objects.exclude(ticker="_QUECONTROL").order_by('-last_date')[:20].values('ticker')

    player_list=[]
    for player in Player.objects.order_by('-user__last_login')[:10]:
        last_history=player.assethistory_set.order_by('-Date')[0]
        player_list.append({'name':player.user.username,'asset':last_history.asset})
        player_list[-1]['topholdings']=[]
        for ticker in sorted(last_history.amount, key=last_history.amount.__getitem__ ,reverse=True)[:5]:
            player_list[-1]['topholdings'].append({
                'ticker' : ticker if ticker!='_cash' else "Cash",
                'percent' : "{:.1f}%".format( last_history.amount[ticker]/last_history.asset *100 ),
            })
        while(len(player_list[-1]['topholdings'])<5):
            player_list[-1]['topholdings'].append(False)
    context['player_list'] = player_list
    context['memo_list'] = MemoTag.getMemos(tag=request.user.username)
    context['memo_recent_list'] = MemoTag.getMemos(tag=None)

    return render(request,'agora/index.html',context)#None tag gives recent tags

def MemoTagsView(request,tag):
    return render(request,'agora/memotag.html',{
        'memo_list' : MemoTag.getMemos(tag)})

def TickerView(request,ticker):
    quetrigger(100)
    if(not Ticker.objects.filter(ticker=ticker).exists()):
        setTicker(ticker)
        return render(request,'home/construction.html',{
            'css_style':'font-size:16px;',
            'construction_msg': ticker.upper() +' - Invalid ticker or initializing'})

    tickerObj=Ticker.objects.get(ticker=ticker)
    if(not tickerObj.dayprice_set.exists()):
        return render(request,'home/construction.html',{
            'css_style':'font-size:16px;',
            'construction_msg': ticker.upper() +' - Invalid ticker or initializing'})

    if(tickerObj.name[-5:]=='(The)'):
        tickerObj.name=tickerObj.name[:-6]
        tickerObj.save()

    if (request.user.is_authenticated):
        trnsresult="NA"
        #player=User.objects.get(username=username).player_set.all()[0]
        if request.method == 'POST':
            form = MemoForm(request.POST)
            if not form.is_valid():
                form = MemoForm()
                return render(request,'agora/tickerview.html',{
                        'tickerObj' : tickerObj,
                        'memo_list' : MemoForm.getMemoFormlist(tickerObj,request.user),
                        'form' : form,
                        'alert_msg': "ERROR: INVALID POST FORM" })
            elif form.cleaned_data['flag']=="add":
                newmemo=form.makeMemo(tickerObj,request.user)
                newmemo.save()
                newmemo.setMemoTags()
                return HttpResponseRedirect('/agora/ticker/'+ticker)
            elif form.cleaned_data['flag']=="del":
                return form.delMemo(ticker,request.user)

        return render(request,'agora/tickerview.html',{
            'tickerObj' : tickerObj,
            'memo_list' : MemoForm.getMemoFormlist(tickerObj,request.user),
            'form' : MemoForm(),
            'title' : ticker})
    #S&P 500 is the example page able to access
    elif ticker=="^GSPC":
        if request.method == 'POST':
            return render(request,'agora/tickerview.html',{
                'tickerObj' : tickerObj,
                'memo_list' : MemoForm.getMemoFormlist(tickerObj,request.user),
                'alert_msg' : "Log In is required to leave a memo",})
        return render(request,'agora/tickerview.html',{
            'tickerObj' : tickerObj,
            'memo_list' : MemoForm.getMemoFormlist(tickerObj,request.user)})

    return HttpResponseRedirect("/accounts/login/?next=/agora/ticker/"+ticker)