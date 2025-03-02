from django.db import models
from django.contrib.auth.models import User


class RefreshToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    refresh_token = models.CharField(max_length=255, unique=True)
