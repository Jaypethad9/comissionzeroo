import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import User
from asgiref.sync import sync_to_async
from .models import Message

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        user1, user2 = self.room_name.replace('chat_', '').split('_')
        self.me = self.scope["user"]
        self.other_username = user2 if self.me.username.lower() == user1 else user1
        self.other_user = await self.get_user(self.other_username)

        await self.channel_layer.group_add(self.room_name, self.channel_name)
        await self.accept()


    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']

        await self.save_message(self.me, self.other_user, message)

        await self.channel_layer.group_send(
            self.room_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender': self.me.username,
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender': event['sender'],
        }))

    @staticmethod
    async def get_user(username):
        return await sync_to_async(User.objects.get)(username=username)

    @staticmethod
    async def save_message(sender, receiver, message):
        await sync_to_async(Message.objects.create)(
            sender=sender, receiver=receiver, content=message
        )
