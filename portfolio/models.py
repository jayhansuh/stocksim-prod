import datetime
import time
import pytz
ptz = pytz.timezone("UTC")

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

from stockdb.models import Ticker, DayPrice
from stockdb.makedb import updateTicker, get_last_price, setTicker
from portfolio.scheduler import quetrigger

class Player(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    def portfolio_default():
        return {"_cash": 100000. }
    portfolio = models.JSONField('portfolio',default=portfolio_default)
    pub_date = models.DateTimeField('date published')
    favrt_ticker = models.ManyToManyField(Ticker, related_name = "subscriber", blank = True)
    following = models.ManyToManyField("self", related_name = "followers", blank = True )
    
    def __str__(self):
        return self.user.username

    # Generate AssetHistory objects and call its setHistory function
    # pfchange indicates the change of portoflio in quantities (ex pfchange={date(2021,01,01):{'_cash':100000.}})
    # When pfchange = {} it assumes there is no change in quantity portfolio from the latest existing history
    def makeHistory(self,pfchange={}):

        if(self.assethistory_set.exists()):
            lasthist=self.assethistory_set.order_by('-Date')[0]
            lastdate = lasthist.Date

            if(str(lastdate) in pfchange):
                lasthist.quant = pfchange[str(lastdate)].copy()
            
            #time consuming line
            lasthist.setHistory()
            
            lasthist.save()
            
            portfolio = lasthist.quant
            lastdate += datetime.timedelta(days=1)

        else:
            portfolio = Player.portfolio_default()
            lastdate = self.pub_date.date()

        historyli=[]
        today=timezone.now().date()
        while(lastdate<=today):

            if(str(lastdate) in pfchange):
                portfolio = pfchange[str(lastdate)]

            historyli.append(
                AssetHistory(
                    player = self,
                    Date = lastdate,
                    asset = None,
                    quant = portfolio.copy(),
                    amount = None,
                    code = 0)
            )

            historyli[-1].setHistory()
            lastdate += datetime.timedelta(days=1)

        AssetHistory.objects.bulk_create(historyli)

        return

    # Generate pfchange based on exisitng trns objects and pass it to makeHistory
    # This function is a manual function especially when you reset DB,
    # because in the normal workflow makeTransaction already takes care of history generating when a transaction is placed
    def catchupHistory(self):
        pfchange = {}

        if(self.assethistory_set.filter(code__gt=0,code__lt=3).exists()):        
            lasthist=self.assethistory_set.filter(code__gt=0,code__lt=3).order_by('-Date')[0]
            portfolio = lasthist.quant.copy()
            lastdate = lasthist.Date + datetime.timedelta(days=1)
            self.assethistory_set.filter(Date__gt = lastdate).delete()
        else:
            portfolio = Player.portfolio_default()
            lastdate = self.pub_date.date()
        
        for trns in self.transaction_set.filter(
            pub_date__gte = datetime.datetime(lastdate.year,lastdate.month,lastdate.day,tzinfo=self.pub_date.tzinfo),
            validation = "SUCCESS").order_by('pub_date'):

            if(trns.pub_date.date()!= lastdate):
                pfchange[str(lastdate)]=portfolio.copy()
                lastdate=trns.pub_date.date()
            trns.applyTransaction(portfolio)
        pfchange[str(lastdate)]=portfolio.copy()        
        self.portfolio=portfolio
        self.save()
        self.makeHistory(pfchange)

    # Generate transaction object and when it is valid update portfolio and AssetHistory
    # This function is based on Transaction.applyTransaction and Player.makeHistory
    # Return a transaction code (eg "TRANSACTION_SUCCESS" "TRANSACTION_FAIL_QuantityMustBeINT")
    def makeTransaction(self,ticker,quantity):
        
        # Buy if quantity>0 and Sell if quantity<0
        # Legit transaction criteria:
        #   1. Integer qunatity (no fractional shares)
        #   2. Ticker data exists (no yfinance error)
        #   3. Consolidated model object creation/modification (no database error)

        # 1. fractional shares
        if(type(quantity)!=int):
            return "TRANSACTION_FAIL_QuantityMustBeINT"

        try:
            price=get_last_price(ticker)
            # 2. yfinance error
            if(price is None):
                return "TRANSACTION_FAIL_NoPriceInfo"

            trns=Transaction(
                player=self,
                pub_date = timezone.now(),
                ticker = ticker,
                quantity = quantity,
                price = price
            )

            res=trns.applyTransaction(self.portfolio)
            trns.save()
            if(res=="TRANSACTION_SUCCESS"):
                self.save()
                if(not Ticker.objects.filter(ticker=ticker).exists()):
                    setTicker(ticker)
                quetrigger(100)
            return res

        except Ticker.DoesNotExist:
            return "TRANSACTION_FAIL_Ticker.DoesNotExist"

        return "TRANSACTION_FAIL_UncaughtError"
    
    

class Transaction(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    pub_date = models.DateTimeField('date published',db_index=True)
    ticker = models.CharField(max_length=16)
    quantity = models.IntegerField(default=0)
    price = models.FloatField(default=0)
    validation = models.CharField(max_length=16,null=True)

    def __str__(self):
        if(self.quantity>=0):
            return " %s  BUY , %s , %s shares , at %.2f USD , ( %s ) ( %s )" % ( self.player, self.ticker, self.price, self.quantity, self.validation,self.pub_date)
        else:
            return " %s  SELL , %s , %s shares , at $%.2f USD , ( %s ) ( %s )" % ( self.player, self.ticker, self.price, -self.quantity, self.validation,self.pub_date)
    
    def viewlistformat(self):
        if(self.ticker == '_swing'):
            return " Gain , SWING TRADE GAME , for $%.2f" % (self.price)
        if(self.quantity>=0):
            return " BUY , %s , %s shares , at $%.2f , total %.2fk" % ( self.ticker, self.quantity, self.price, self.price * self.quantity/1000)
        else:
            return " SELL , %s , %s shares , at $%.2f, total %.2fk" % ( self.ticker,  -self.quantity, self.price, -self.price * self.quantity/1000)

    # Based on trns object information update a portfolio dictionary object
    # This does not save Player or AssetHistory object by itself
    # Return a transaction code (eg "TRANSACTION_SUCCESS" "TRANSACTION_FAIL_NotEnoughCash")
    def applyTransaction(self,portfolio):

        # Buy if quantity>0 and Sell if quantity<0
        # Legit transaction criteria:
        #   1. Final cash balance >= 0 (no margin transaction)
        #   2. No float precision error (ex (1e+20+1)==1e+20)
        #   3. Final equity qunatity >= 0 (no short sell)

        quantity=self.quantity
        price=self.price
        ticker=self.ticker
        
        #special transactions
        if(ticker[0]=='_'):
            if(ticker=='_swing' and (price<=1000)):
                portfolio['_cash'] += price
                self.validation="SUCCESS"
                return "TRANSACTION_SUCCESS"
            else:
                self.validation="UnknownTicker"
                return "TRANSACTION_FAIL_"+self.validation

        newcash=portfolio['_cash']-price*quantity

        # 1. margin transaction
        if(newcash<0):
            self.validation="NotEnoughCash"
            return "TRANSACTION_FAIL_"+self.validation

        # 2. float precision error
        if((portfolio['_cash']-newcash)<price*quantity):
            newcash-=newcash*(1e-15)
            if((portfolio['_cash']-newcash)<price*quantity):
                self.validation="FloatPointError"
                return "TRANSACTION_FAIL_"+self.validation

        newqunatity=quantity
        if(ticker in portfolio):
            newqunatity+=portfolio[ticker]

        # 3. short sell
        if(newqunatity<0):
            self.validation="NotEnoughShares"
            return "TRANSACTION_FAIL_"+self.validation
        
        portfolio['_cash'] = newcash
        portfolio[ticker] = newqunatity
        if(portfolio[ticker]==0):
            del portfolio[ticker]
        self.validation="SUCCESS"

        return "TRANSACTION_SUCCESS"

def isEndOfMonth(date):
    return (date+datetime.timedelta(days=1)).month!=date.month

class AssetHistory(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    Date = models.DateField(db_index=True)
    asset = models.FloatField(null=True)
    quant = models.JSONField(null=True)
    amount = models.JSONField(null=True)
    code = models.IntegerField("0:no asset,1:normal day,2:end of month,3:today",default=0,db_index=True)

    def __str__(self):
        return " %s , asset %s , ( %s )" % ( self.player, self.asset, self.Date)

    # Calculate amount portfolio and total asset based on quant portfolio and Date
    # The calculation is skipped if the date is already passed and the history is settled
    def setHistory(self,save=False):

        if(self.code == 0 or self.code == 3):
            #set code
            if(timezone.now().date()==self.Date):
                self.code=3
            elif(isEndOfMonth(self.Date)):
                self.code=2
            else:
                self.code=1

            #set amount
            self.amount={}
            for el in self.quant.keys():
                if(el=="_cash"):
                    self.amount[el]=self.quant[el]
                else:
                    try:
                        tickerObj = Ticker.objects.get(ticker=el)

                        ##TIME CONSUMING LINE
                        updateTicker(tickerObj)
                        
                        price=tickerObj.dayprice_set.filter(Date__lte=self.Date).order_by('-Date')[0].Close
                    except Ticker.DoesNotExist:

                        ##TIME CONSUMING LINE
                        tickerObj = setTicker(el)
                        if(tickerObj==None):
                            print("No price found for %s %s" % (el,str(self.Date)))
                            price=0
                        else:
                            updateTicker(tickerObj)
                            price=tickerObj.dayprice_set.filter(Date__lte=self.Date).order_by('-Date')[0].Close
                    except IndexError:
                        print("No price found for %s %s" % (el,str(self.Date)))
                        price=0
                    self.amount[el]=price*self.quant[el]
            
            #set asset
            self.asset = 0
            for val in self.amount.values():
                self.asset += val

            if(save):
                self.save()

            return

# flag=True
# for h in li:
#     newamt={}
#     for t in ['MRNA','W','NVDA','BABA','ILMN','SHOP','PDD','TTD','SPOT','NFLX','_cash']:
#         #print(t)
#         if(t in h.amount.keys()):
#             #print(h.amount[t])
#             newamt[t]=h.amount[t]
#     if(len(newamt.keys())==len(h.amount.keys())):
#         print('save',h)
#         h.amount=newamt
#         h.save()
#     else:
#         print('fail',h)
#         flag=False

