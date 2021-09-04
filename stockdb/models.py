import datetime

from django.db import models
from django.utils import timezone

# Create your models here.
class Ticker(models.Model):
    ticker = models.CharField(max_length=16, primary_key=True)
    name = models.CharField(max_length=50,unique=True)
    sector = models.CharField(max_length=50,default="")
    exchange = models.CharField(max_length=16,default="")
    currency = models.CharField(max_length=16,default="")
    pub_date = models.DateTimeField('date published')
    last_date = models.DateTimeField('last updated date',null=True)
    last_price = models.FloatField(default=0)

    def __str__(self):
        return self.ticker

    def is_uptodate(self):
        return self.last_date.date() == timezone.now().date()# - datetime.timedelta(days=90)
    
    def to_dict(self,columns=('Open','High','Low','Close'),period="max"):
        
        if(period=='max'):
            objs=self.dayprice_set.all()
        elif(period[-1]=='d'):
            objs=self.dayprice_set.filter(Date__gt=timezone.now().date()- datetime.timedelta(days=int(period[:-1])))
        else:
            print("Ticker.to_dict unsupported period type input")
            return {}

        dictobj={}
        for el in objs.order_by('-Date').values():
            dictobj[str(el['Date'])] = { col : el.get(col, None) for col in columns }
        return dictobj

class DayPrice(models.Model):
    ticker = models.ForeignKey(Ticker, on_delete=models.CASCADE)

    Date = models.DateField()
    Open = models.FloatField(default=0,null=True)
    High = models.FloatField(default=0,null=True)
    Low = models.FloatField(default=0,null=True)
    Close = models.FloatField(default=0,null=True)

    Volume = models.FloatField(null=True)
    Dividends = models.FloatField(null=True)
    Split = models.IntegerField(null=True)

    def __str__(self):
        return "ticker %s, date %s" % (self.ticker.ticker,str(self.Date))
