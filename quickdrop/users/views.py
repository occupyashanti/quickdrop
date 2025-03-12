from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required

# User Registration View
def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
            return redirect('register')

        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        messages.success(request, "Account created successfully. Please log in.")
        return redirect('login')

    return render(request, 'users/register.html')

# User Login View
def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')  # Redirect to dashboard on successful login
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, 'users/login.html')

# User Logout View
def user_logout(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('login')

# Dashboard (Requires Login)
@login_required(login_url='login')
def dashboard(request):
    return render(request, 'users/dashboard.html')

# Additional Pages
def home(request):
    return render(request, 'users/home.html')

def about(request):
    return render(request, 'users/about.html')

def contacts(request):
    return render(request, 'users/contacts.html')

def resources(request):
    return render(request, 'users/resources.html')

def careers(request):
    return render(request, 'users/careers.html')

def terms(request):
    return render(request, 'users/terms.html')
