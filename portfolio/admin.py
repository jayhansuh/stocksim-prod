from django.contrib import admin

# Register your models here.

from .models import Player, Transaction, AssetHistory

admin.site.register(Player)
admin.site.register(Transaction)
admin.site.register(AssetHistory)