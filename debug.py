#with open('debug.py') as infile: exec(infile.read())   

from agora.models import *
from stockdb.models import *
from portfolio.models import *

#import sys
#import importlib
#modules=['agora.models', 'stockdb.models', 'portfolio.models']
#for module in modules:
#    importlib.reload(sys.modules[module])

#importlib.reload(agora.models)
#importlib.reload(stockdb.models)
#importlib.reload(portfolio.models)

from django.utils import timezone
import datetime

snp=Ticker.objects.get(ticker="^GSPC")
player=Player.objects.get(user__username="suhh")

memo=Memo.objects.all()[0]