import json
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.contrib.auth.models import User
from .models import Message
from asgiref.sync import sync_to_async


class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        """async method that handles connecting of a user"""
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        user1 = self.scope["user"].username
        user2 = self.room_name
        self.room_group_name = f"chat_{"".join(sorted([user1, user2]))}"
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        """async method that handles disconnecting of a user"""
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        """async method that handles the recived messages"""
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        sender = self.scope["user"]
        receiver = await self.get_receiver_user()
        await self.save_message(sender, receiver, message)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "sender": sender.username,
                "receiver": receiver.username,
                "message": message,
            },
        )

    async def chat_message(self, event):
        """async method that constructs the json and sends the message"""
        message = event["message"]
        sender = event["sender"]
        receiver = event["receiver"]

        await self.send(
            text_data=json.dumps(
                {"sender": sender, "receiver": receiver, "message": message}
            )
        )

    @sync_to_async
    def save_message(self, sender, receiver, message):
        """async method that saves the messages in db"""
        Message.objects.create(sender=sender, receiver=receiver, content=message)

    @sync_to_async
    def get_receiver_user(self):
        """async method that retrices the user based on the room name"""
        return User.objects.get(username=self.room_name)
