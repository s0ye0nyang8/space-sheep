from django.contrib import admin
from django.urls import path, include
from .views import login_views , chat_views, home_views
from django.conf.urls import url

urlpatterns = [
    path('', home_views.home, name='home'),
    path('signup', login_views.register, name='register'),
    path('signin',login_views.login,name='login'),
    path('signout', login_views.logout, name='logout'),
    path('settings', home_views.setting, name='setting'),
    path('deregister', home_views.deregister, name='deregister'),
    path('ask/<str:room_name>', chat_views.ask, name='ask'),
    path('ask/<str:room_name>/moment', chat_views.moment, name='moment'),
]