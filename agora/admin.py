from django.contrib import admin

# Register your models here.

from .models import Memo, MemoTag

admin.site.register(Memo)
admin.site.register(MemoTag)