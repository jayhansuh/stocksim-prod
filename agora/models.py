from django.db import models

from django.utils import timezone
import datetime

from portfolio.models import Player
from stockdb.models import Ticker

import re

# Create your models here.

#URL_REGEX = re.compile(r'''((\#(\w+)|https://|http://)[^ <>'"{},.|\\^`[\]]*)''')
URL_REGEX = re.compile(r'''((https://|http://)[^ <>'"{},.|\\^`[\]]*)''')
def encode_links(unencoded_string):
    # def tagGen(match):
    #     if match.group(0).startswith('#'):
    #         link="/agora/hashtag/"+match.group(0)[1:]
    #     else:
    #         link=match.group(0)
    #     return "<a href='"+link+"'>"+match.group(0)+"</a>"
    # return URL_REGEX.sub(tagGen, unencoded_string)
    encoded_str=URL_REGEX.sub(r"<a href='\1'>\1</a>", unencoded_string)
    tags=re.findall(r"#(\w+)", unencoded_string)
    for tag in tags:
        #if not (tag in {'https','http'}):
        encoded_str=encoded_str.replace("#"+tag,"<a href='/agora/hashtag/"+tag+"'>#"+tag+"</a>")
    return encoded_str

#encode_links("https://namver/#/esg #ddfrt,#efw zd #https://namve")

class Memo(models.Model):
    ticker = models.ForeignKey(Ticker, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, null=True, on_delete=models.SET_NULL)
    author = models.CharField(max_length=32)
    content = models.CharField(max_length=280)
    pub_date = models.DateTimeField('date published',db_index=True)
    isSubMemo = models.BooleanField(default=False,db_index=True)
    deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.content
    
    @property
    def calIsSubMemo(self):
        self.isSubMemo=subMemo.objects.filter(pk=self.pk).exists()
        return self.isSubMemo

    @property
    def getInnerHTML(self):
        if(self.deleted):
            return "[ This message was deleted ]"
        return encode_links(self.content)

    def setMemoTags(self):
        existingTags=set(map(lambda x : x['tag'] , self.memotag_set.values('tag')))
        tags=re.findall(r"#(\w+)", self.getInnerHTML)
        tags.append(self.ticker.ticker)
        tags.append(self.author)
        tagObjs=[]
        for tag in set(tags):
            if not tag in existingTags:
                tagObjs.append(MemoTag(memo=self,tag=tag))
        MemoTag.objects.bulk_create(tagObjs)

class subMemo(Memo):
    parent = models.ForeignKey(Memo, on_delete=models.CASCADE, related_name="children")

class MemoTag(models.Model):
    memo = models.ForeignKey(Memo, on_delete=models.CASCADE)
    tag = models.CharField(max_length=32,db_index=True)

    def getMemos(tag):
        if(tag==None):
            memotags=MemoTag.objects.order_by('-memo__pub_date')[:14]
        else:
            memotags=MemoTag.objects.filter(tag=tag).order_by('-memo__pub_date')
        withoutRep=[]
        pkset=set()
        for memotag in memotags:
            if not memotag.memo.pk in pkset:
                pkset.add(memotag.memo.pk)
                withoutRep.append(memotag.memo)
        return withoutRep