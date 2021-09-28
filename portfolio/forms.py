from agora.models import Report
from django import forms
from .models import Player, Transaction, Reply
from stockdb.models import Ticker
from django.forms import ModelForm
from django.utils import timezone

#import threading

class TransactionForm(forms.Form):
    ticker = forms.CharField(label='Ticker', max_length=16, required=True)
    quantity = forms.IntegerField(label="Quantity", required=True)

    def makeTransaction(self, player):
        ticker = self.cleaned_data['ticker']
        if(ticker[0]!='_'):
            ticker=ticker.upper()
        return player.makeTransaction(ticker,self.cleaned_data['quantity'])

class ReplyForm(forms.Form):
    content = forms.CharField(max_length=280,required=True, label=False, widget=forms.Textarea(attrs={
        "rows":5,
        "placeholder":"Add a reply here (# to tag a user or a word e.g. #admin)",
        "style":"align-content:left;width:calc(100% - 15px);resize: vertical;"
}))
    #flag = forms.CharField(max_length=5,required=True, label=False, widget=forms.HiddenInput())
    #parentpk = forms.IntegerField(widget=forms.HiddenInput(),required=False)

    def makeReply(self,parent,user):
        
        kwargs={'content_object':parent,
                'user':user,
                'content':self.cleaned_data['content'],
                'pub_date':timezone.now(),}

        return Reply(**kwargs)
