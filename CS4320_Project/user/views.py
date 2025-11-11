from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout as auth_logout
from django.contrib.auth.forms import AuthenticationForm
from .forms import UserRegisterForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Profile


#################### index ####################################### 
def index(request):
    return render(request, 'index.html', {'title': 'index'})


########### register here ##################################### 
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Auto login after register
            return redirect('landingPage')  # ✅ redirect using URL name
    else:
        form = UserRegisterForm()
    return render(request, 'register.html', {'form': form, 'title': 'Register'})


################ login forms ################################################### 
def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('landingPage')  # ✅ correct redirect
        else:
            messages.error(request, "Invalid username or password")

    form = AuthenticationForm()
    return render(request, 'login.html', {'form': form, 'title': 'Log In'})


#################### landing page #######################################
@login_required
def landingPage(request):
    try:
        monthly_income = request.user.profile.monthly_income
    except AttributeError:
        # fallback if no profile or monthly_income exists
        monthly_income = 0

    return render(request, 'landingPage.html', {
        'title': 'Landing Page',
        'monthly_income': monthly_income
    })


#################### logout #######################################
def user_logout(request):
    auth_logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('index')  # ✅ redirect to homepage (index)



# views.py
from django.shortcuts import render, redirect
from .forms import MonthlyIncomeForm
from django.contrib.auth.decorators import login_required

@login_required
def account_view(request):
    return render(request, 'Account.html', {'title': 'account'})

# views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import MonthlyIncomeForm
from .models import Profile

@login_required
def update_income(request):
    profile = request.user.profile

    if request.method == 'POST':
        form = MonthlyIncomeForm(request.POST)
        if form.is_valid():
            profile.monthly_income = form.cleaned_data['monthly_income']
            profile.save()
            return redirect('landingPage')  # or wherever you want to redirect
    else:
        form = MonthlyIncomeForm(initial={'monthly_income': profile.monthly_income})

    return render(request, 'update_income.html', {'form': form})
