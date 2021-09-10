from django.urls import path

from . import views

app_name = 'agora'
urlpatterns = [
    path('', views.index, name='index'),
    path('hashtag/<str:tag>', views.MemoTagsView, name='agoratag'),
    path('ticker/<str:ticker>/', views.TickerView, name='agoraticker'),
    path('ticker/<str:ticker>/addfav/', views.AddFavorite, name='addfav'),
]