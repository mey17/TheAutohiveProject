import json
from channels.generic.websocket import AsyncWebsocketConsumer

class ESP8266Consumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("esp8266_group", self.channel_name)
        await self.accept()
        print(f"ESP8266 connected to WebSocket group: {self.channel_name}")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("esp8266_group", self.channel_name)
        print(f"ESP8266 disconnected from WebSocket group: {self.channel_name}")

    async def receive(self, text_data):
        print(f"Message received from ESP8266: {text_data}")

    async def send_message(self, event):
        message = event['message']
        print(f"Sending message to ESP8266: {message}")
        await self.send(text_data=json.dumps(message))