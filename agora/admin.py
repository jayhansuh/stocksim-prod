from django.contrib import admin

# Register your models here.

from .models import Memo, MemoTag, PortfReview, TickerReport

admin.site.register(Memo)
admin.site.register(MemoTag)
admin.site.register(PortfReview)
admin.site.register(TickerReport)