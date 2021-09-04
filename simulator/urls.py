from django.urls import path

from . import views

app_name = 'simulator'
urlpatterns = [
    path('', views.simmenu, name='simmenu'),
    path('chartsurf/', views.chartsurf_nofetch, name='chartsurf'),
    path('qlab/', views.qlab, name='qlab'),
    path('histplot/<str:protocol>/', views.historyplot, name='historyplot'),
]