from django.contrib import admin

# Register your models here.

from .models import Ticker, DayPrice

admin.site.register(Ticker)
admin.site.register(DayPrice)