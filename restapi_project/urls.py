from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("google/", include("google_apis.urls")),
    path("", include("chat_app.urls")),
    path("", include("users.urls")),
]
