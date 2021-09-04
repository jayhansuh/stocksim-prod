from django import forms
from .models import Player, Transaction
from stockdb.models import Ticker

#import threading

class TransactionForm(forms.Form):
    ticker = forms.CharField(label='Ticker', max_length=16, required=True)
    quantity = forms.IntegerField(label="Quantity", required=True)

    def makeTransaction(self, player):
        ticker = self.cleaned_data['ticker']
        if(ticker[0]!='_'):
            ticker=ticker.upper()
        return player.makeTransaction(ticker,self.cleaned_data['quantity'])