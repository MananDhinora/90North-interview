from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Message
from django.db.models import Q
from datetime import datetime


@login_required
def chat_room(request, room_name):
    """used to retrive chat history and render the gui"""
    users = User.objects.exclude(id=request.user.id)
    chats = Message.objects.filter(
        (Q(sender=request.user) & Q(receiver__username=room_name))
        | (Q(receiver=request.user) & Q(sender__username=room_name))
    )

    chats = chats.order_by("timestamp")
    user_last_messages = []

    for user in users:
        last_message = (
            Message.objects.filter(
                Q(sender=request.user) & Q(receiver=user)
                | (Q(receiver=request.user) & Q(sender=user))
            )
            .order_by("-timestamp")
            .first()
        )

        user_last_messages.append({"user": user, "last_message": last_message})

    user_last_messages.sort(
        key=lambda x: (
            x["last_message"].timestamp if x["last_message"] else datetime.min
        ),
        reverse=True,
    )

    return render(
        request,
        "chat.html",
        {
            "room_name": room_name,
            "chats": chats,
            "users": users,
            "user_last_messages": user_last_messages,
        },
    )
