from django import forms
from .models import Memo, MemoTag, TickerReport, subMemo, PortfReview
from stockdb.models import Ticker
from django.utils import timezone

from django.shortcuts import render
from django.http import HttpResponseRedirect

class MemoForm(forms.Form):
    content = forms.CharField(max_length=280,required=True, label=False, widget=forms.Textarea(attrs={
        "rows":5,
        "placeholder":"Add a memo here (# to tag a user or a word e.g. #admin)",
        "style":"align-content:left;width:calc(100% - 15px);resize: vertical;"
}))
    flag = forms.CharField(max_length=5,required=True, label=False, widget=forms.HiddenInput())
    parentpk = forms.IntegerField(widget=forms.HiddenInput(),required=False)
    
    def delMemo(self,ticker,user):
        memo = Memo.objects.get(pk=self.cleaned_data['parentpk'])
        if(memo.player.user.pk==user.pk):
            memo.deleted = True
            memo.save()
            form = MemoForm()
            return HttpResponseRedirect('/agora/ticker/'+ticker)
        else:
            form = MemoForm()
            return render(request,'agora/TickerView.html',{
                    'memo_list' : MemoForm.getMemoFormlist(tickerObj,request.user),
                    'form' : form,
                    'alert_msg': "ERROR: YOU ARE NOT AUTHORIZED TO DELETE IT" })
       

    def makeMemo(self,tickerObj,user):
        
        kwargs={'ticker':tickerObj,
                'player':user.player_set.all()[0],
                'author':user.username,
                'content':self.cleaned_data['content'],
                'pub_date':timezone.now(),}

        if self.cleaned_data['parentpk']:
            kwargs['parent']=Memo.objects.get(pk=self.cleaned_data['parentpk'])
            kwargs['isSubMemo']=True
            return subMemo(**kwargs)
        else:
            return Memo(**kwargs)
    
    def getMemoFormlist(tickerObj,user):
        mainMemos=Memo.objects.filter(ticker=tickerObj,isSubMemo=False).order_by("-pub_date")
        memolist=[]
        for memo in mainMemos:
            memolist.append({'memo':memo,'ischild':False, 'addform':False,'parentpk':memo.pk,'delenable':(user.pk==memo.player.user.pk)})
            for child in memo.children.order_by("pub_date"):
                memolist.append({'memo':child,'ischild':True, 'addform':False ,'parentpk':memo.pk,'delenable':(user.pk==child.player.user.pk)})
            memolist[-1]['addform']=MemoForm(initial={'parentpk':memo.pk})
            if(len(memolist)>100):
                break
        return memolist
             
class TickerReportForm(forms.ModelForm):
    class Meta:
        model = TickerReport
        fields = ['title','ticker','status','content']
        widgets = {
            'title': forms.Textarea(attrs={
            "rows":1,
            "placeholder":"Ticker Report",
            "style":"align-content:left;width:calc(100% - 15px);resize: vertical;"
        }),
            'content': forms.Textarea(attrs={
            "rows":15,
            "placeholder":"Add your analysis on the ticker here. (# to tag a user or a word e.g. #admin)",
            "style":"align-content:left;width:calc(100% - 15px);resize: vertical;"
        })
        }

    def makeReport(self,user):

        kwargs={
                'title': self.cleaned_data['title'],
                'player': user.player_set.all()[0],
                'author': user,
                'pub_date':timezone.now(),
                'content':self.cleaned_data['content'],
                'status': self.cleaned_data['status'],
                'ticker': self.cleaned_data['ticker']
                }
        return TickerReport(**kwargs)
        

class PortfReviewForm(forms.ModelForm):
    class Meta:
        model = PortfReview
        fields = ['title','status','content']
        widgets = {
            'title': forms.Textarea(attrs={
            "rows":1,
            "placeholder":"Ticker Report",
            "style":"align-content:left;width:calc(100% - 15px);resize: vertical;"
        }),
            'content': forms.Textarea(attrs={
            "rows":15,
            "placeholder":"Add your analysis on the ticker here. (# to tag a user or a word e.g. #admin)",
            "style":"align-content:left;width:calc(100% - 15px);resize: vertical;"
        })
        }

