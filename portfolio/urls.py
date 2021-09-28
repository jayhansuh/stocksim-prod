from django.urls import path

from . import views

app_name = 'portfolio'
urlpatterns = [
    path('', views.indexView, name='index'),
    path('<str:subappname>/', views.redirectSubApp, name='redirectsubapp'),
    path('overview/<str:username>/', views.PortfolioView, name='overview'),
    path('profile/<str:username>/', views.ProfileView, name='profile'),
    path('history/<str:username>/', views.HistoryView.as_view(), name='history'),
    path('transactions/<str:username>/', views.TransactionsView, name='transactions'),
    path('ranking/help/', views.RankingHelp, name='rankinghelp'),
    path('_get_portfolio', views.getPortfolio, name='getPortfolio'),
    path('overview/<str:username>/addfollow/',views.AddFollowing,name='addfollow')
]