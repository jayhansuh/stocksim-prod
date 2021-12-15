from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, Http404

# Create your views here.
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericRelation

from django.contrib.auth.decorators import login_required
from stockdb.models import Ticker
from portfolio.models import Player, Transaction, Feed, Like, Reply
from .models import Memo, MemoTag, PortfReview, TickerReport
from .forms import MemoForm
from portfolio.forms import ReplyForm
from django.http import JsonResponse
from stockdb.makedb import setTicker
from django.contrib.auth.models import User
from portfolio.scheduler import quetrigger
from django.core.paginator import Paginator
from itertools import chain
from portfolio.views import getBadge
from home.views import getFavrtTickers
import json

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

def getFeedList(request):
    username = request.user.username
    player = User.objects.get(username = username).player_set.all()[0]
    favrt_ticker_list = player.favrt_ticker.all()
    following_list = player.following.all()
    feed_tags = list(favrt_ticker_list) + list(following_list) + [player]
    feeds_list = Feed.objects.filter(tag__in = feed_tags).order_by('-pub_date')
    return feeds_list


def FeedsView(request):
    if not request.user.is_authenticated:
        return   HttpResponseRedirect("/accounts/login/?next=/agora/feeds") 
    else:
        username = request.user.username
        player=User.objects.get(username=username).player_set.all()[0]

        last_history=player.assethistory_set.filter(code__gt=0).order_by('-Date')[0]
        num_following = player.following.count()
        num_follower = player.followers.count()
        # feeds_list = Transaction.objects.order_by('-pub_date')
        feeds_list = getFeedList(request)
        like_list = []
        for feed in feeds_list:
            liked = feed.content_object.like.filter(user= request.user).exists()
            like_list.append(liked)


        paginator = Paginator(feeds_list, 10) # Show 2 contacts per page.
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context = {}
        context['badgeimg']=getBadge(last_history.asset)
        context['is_nav_sidebar_enabled'] =True  
        context['last_history'] = last_history
        context['asset'] = "{:.2f}".format(last_history.asset)
        context['ticker_list'] = getFavrtTickers(request, 10)
        context['page_obj']= page_obj
        context['num_following'] = num_following
        context['num_follower'] = num_follower
        context['form'] = ReplyForm()
        context['like_list'] = like_list

        return render(request, 'agora/feeds.html',context  )

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

        username = request.user.username
        p=User.objects.get(username=username).player_set.all()[0]
        subscribed = p.favrt_ticker.filter(pk = tickerObj.pk).exists()

        return render(request,'agora/tickerview.html',{
            'tickerObj' : tickerObj,
            'memo_list' : MemoForm.getMemoFormlist(tickerObj,request.user),
            'form' : MemoForm(),
            'title' : ticker,
            'subscribed': subscribed
            })
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

def AddFavorite(request,ticker):
    if request.method != 'POST':
        raise Http404("This is not a valid approach.")
    else:    
        username = request.user.username
        p=User.objects.get(username=username).player_set.all()[0]
        t = Ticker.objects.filter(ticker=ticker)[0]
        issubscribed = p.favrt_ticker.filter(pk = t.pk).exists()
        if issubscribed:
            p.favrt_ticker.remove(t)
        else:
            p.favrt_ticker.add(t)
        p.save()
    return JsonResponse({"issubscribed":  not issubscribed })

def AddLike(request):
    if request.method != 'POST':
        raise Http404("This is not a valid approach.")
    else:
        user = request.user
        req = json.loads(request.GET.get('req',"{}"))
        type = req["type"]
        id = req["objectid"]
        if type == "memo":
            post = Memo.objects.get(id = id)
        elif type == "transaction":
            post = Transaction.objects.get(id=id)
        elif type == "ticker report":
            post = TickerReport.objects.get(id=id)
        elif type == "porf review":
            post = PortfReview.objects.get(id=id)
            
        ct = ContentType.objects.get_for_model(post)
        like_set = Like.objects.filter(content_type = ct,object_id = post.id, user = user)
        feed = post.feed.get()        

        if like_set.count() ==0:
            Like.objects.create(content_object = post, user = user)
            liked = True
        elif like_set.count() == 1:
            like_set.delete()
            liked = False
        else:
            raise Http404("Something wrong: double count of the like.")
        like_count = post.like.count()
        feed.update()
        return JsonResponse({"liked": liked, "like_count": like_count})

def AddReply(request):

    if request.method == 'POST':
        form = ReplyForm(request.POST)
        if not form.is_valid():
            raise Http404("The form is not valid.")

        type = form.cleaned_data['parenttype']
        id = form.cleaned_data['parentpk']
        if type == "transaction":
            parent = Transaction.objects.get(id = id)
        elif type == "portf review":
            parent = PortfReview.objects.get(id = id)
        elif type == "ticker report":
            parent = TickerReport.objects.get(id = id) 
        else:
            raise Http404("The parent is the invalid object")
        feed = parent.feed.get()
        user = request.user
        if form.cleaned_data['flag'] =="add":
            newreply = form.makeReply(parent,user)
            newreply.save()
        elif form.cleaned_data['flag'] =="del":
            form.delReply(user)
        elif form.cleaned_data['flag'] =="show":
            pass

        feed.update()
        replylist = []
        parentinfo = {}
        parentinfo['parenttype'] = type
        parentinfo['parentid'] = id
        replylist.append(parentinfo)
        for reply in parent.reply.order_by('pub_date'):
            replydict = {}
            replydict['pub_date'] = reply.pub_date.strftime('%b, %d, %Y %H:%M %p')
            replydict['content'] = reply.content
            replydict['user'] = reply.user.username
            replydict['editable'] = (user == reply.user)
            replydict['like_count'] = reply.like.count()
            replydict['replyid'] = reply.id
            replylist.append(replydict)

        return JsonResponse(json.dumps(replylist,default = str),safe=False)  
