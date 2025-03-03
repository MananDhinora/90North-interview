from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages


def login_page(request):
    """used login to chat_app"""
    if request.user.is_authenticated:
        return redirect(f"/chat/{request.user.username}/")

    if request.method == "POST":
        username = request.POST.get("username")
        user = authenticate(
            request, username=username, password=request.POST.get("password")
        )
        if user is not None:
            login(request, user)
            messages.success(request, "Login successful!")
            return redirect(f"/chat/{user.username}/")
        else:
            messages.error(request, "Invalid email or password. Please try again.")

    return render(request, "login.html")


@login_required
def logout_page(request):
    """logout user"""
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect("/")


def signup_view(request):
    """used to make new users for chat_app"""
    if request.user.is_authenticated:
        return redirect(f"/chat/{request.user.username}/")

    if request.method == "POST":
        email = request.POST.get("email")
        username = request.POST.get("username")
        password1 = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        # Check if passwords match
        if password1 != confirm_password:
            messages.error(request, "Passwords do not match. Please try again.")
            return render(request, "signup.html")

        # Check if email is already taken
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email is already in use. Please try another.")
            return render(request, "signup.html")

        # Check if username is already taken
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username is already taken. Please choose another.")
            return render(request, "signup.html")

        # Create the new user
        user = User.objects.create_user(
            username=username, email=email, password=password1
        )
        user.save()
        messages.success(request, "Signup successful! You can now log in.")
        return redirect("login")

    return render(request, "signup.html")
