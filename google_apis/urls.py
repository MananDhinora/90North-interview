from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("auth/login/", views.authorize, name="authorize"),
    path("auth/logout/", views.clear_credentials, name="clear_credentials"),
    path("auth/login/callback/", views.oauth2callback, name="oauth2callback"),
    path("auth/token/", views.get_auth_token, name="get_auth_token"),
    path("userinfo/", views.credentials_to_dict, name="userinfo"),
    path("google-picker/", views.google_picker, name="google_picker"),
    path(
        "google-picker/callback/",
        views.google_picker_callback,
        name="google_picker_callback",
    ),
    path("google-picker/upload/", views.upload_file, name="upload_file"),
    path("google-picker/download/", views.download_file, name="download_file"),
]
