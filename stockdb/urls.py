from django.urls import path

from . import views

app_name = 'stockdb'
urlpatterns = [
    path('_get_meta', views.getMeta, name='getMeta'),
    path('_get_last_price', views.getLastPrice, name='getLastPrice'),
]