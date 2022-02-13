from django.contrib import admin
from django.urls import path, include
from .views import login_views , chat_views, home_views
from django.conf.urls import url

urlpatterns = [
    path('', login_views.login,name='login'),
    path('signup/', login_views.signup, name='signup'),
    path('home/',home_views.home,name='home'),
    path('logout/', login_views.logout, name='logout'),
    path('home/ask/<str:room_name>', chat_views.ask, name='ask'),
]