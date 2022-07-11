from django.conf.urls import url
from django.urls import path, include
from . import consumers
from django.conf.urls import url

websocket_urlpatterns = [
    # path('/home/<str:pk>/ask/', consumers.AskConsumer),
    url(r'^ask/(?P<room_name>[^/]+)$', consumers.AskConsumer.as_asgi()),
    # path('home/<str:username>/groupchat', consumers.ChatConsumer.as_asgi())
]