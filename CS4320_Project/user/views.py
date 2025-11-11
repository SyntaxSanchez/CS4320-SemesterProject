from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout as auth_logout
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from .forms import UserRegisterForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages


from django.db import models
from django.db.models import Q

from django.contrib.auth.models import User

from django.conf import settings



#################### index ####################################### 
def index(request):
    return render(request, 'index.html', {'title':'index'})

########### register here ##################################### 
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')

            # Automatically log the user in after signup (optional)
            login(request, user)
            return redirect('landingPage')
    else:
        form = UserRegisterForm()
    return render(request, 'register.html', {'form': form, 'title':'register here'})

################ login forms ################################################### 
def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password")
            
    form = AuthenticationForm()
    return render(request, 'login.html', {'form': form, 'title':'log in'})


@login_required
def dashboard(request):
    return render(request, 'user/dashboard.html', {'title': 'Dashboard'})

# ---------------- Logout -----------------
def user_logout(request):
    auth_logout(request)
    return redirect('homepage')
