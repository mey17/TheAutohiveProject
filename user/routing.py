from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/esp8266/$', consumers.ESP8266Consumer.as_asgi()),
]