from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout as auth_logout
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from .forms import UserRegisterForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required

def index(request):
    return render(request, 'homepage.html', {'title':'index'})

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
    return render(request, 'user/register.html', {'form': form, 'title':'register here'})


def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('landingPage')
        else:
            messages.error(request, "Invalid username or password")
            
    form = AuthenticationForm()
    return render(request, 'user/login', {'form': form, 'title':'login'})


@login_required
def dashboard(request):
    return render(request, 'user/landingPage', {'title': 'landingPage'})


# ---------------- Logout -----------------
def user_logout(request):
    auth_logout(request)
    return redirect('index')

@login_required
def account_link(request):
    token_info = request.session.get('spotify_token')
    spotify_data = None

    if token_info:
        sp = spotipy.Spotify(auth=token_info['access_token'])
        try:
            spotify_user = sp.current_user()
            spotify_data = {
                'display_name': spotify_user.get('display_name'),
                'email': spotify_user.get('email'),
                'id': spotify_user.get('id'),
            }
        except Exception as e:
            spotify_data = {'error': str(e)}
    
    return render(request, 'user/account_link.html', {
        'title': 'Account Link',
        'spotify_data': spotify_data,
    })