from django.urls import path
from . import views
import jwt

urlpatterns = [path("", views.home), path("logout", views.logout_view)]
