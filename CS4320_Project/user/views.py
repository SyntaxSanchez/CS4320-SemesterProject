#views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout as auth_logout
from django.contrib.auth.forms import AuthenticationForm
from .forms import UserRegisterForm, MonthlyIncomeForm, ExpenseForm, DebtForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Profile, Expense, Debt
from decimal import Decimal
from django.core.paginator import Paginator
from django.db.models import Sum


#################### index ####################################### 
def index(request):
    return render(request, 'index.html', {'title': 'index'})


########### register here ##################################### 
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create profile for new user
            Profile.objects.create(user=user)
            login(request, user) 
            return redirect('landingPage')  
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
            return redirect('landingPage') 
        else:
            messages.error(request, "Invalid username or password")

    form = AuthenticationForm()
    return render(request, 'login.html', {'form': form, 'title': 'Log In'})


#################### landing page #######################################
@login_required
def landingPage(request):
    # Get or create profile
    profile, created = Profile.objects.get_or_create(user=request.user)
    monthly_income = profile.monthly_income
    
    # Calculate total expenses for the current month
    total_expenses = Expense.objects.filter(
        user=request.user
    ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
    
    # Calculate remaining budget
    remaining_budget = monthly_income - total_expenses
    
    # Calculate percentage spent (avoid division by zero)
    if monthly_income > 0:
        percentage_spent = (total_expenses / monthly_income) * 100
    else:
        percentage_spent = 0
    
    # Use the income for calculations - use Decimal instead of float
    savings_goal = monthly_income * Decimal('0.20')  # 20% savings
    expenses_budget = monthly_income * Decimal('0.50')  # 50% for expenses
    
    context = {
        'title': 'Landing Page',
        'monthly_income': monthly_income,
        'total_expenses': total_expenses,
        'remaining_budget': remaining_budget,
        'percentage_spent': percentage_spent,
        'savings_goal': savings_goal,
        'expenses_budget': expenses_budget,
    }
    return render(request, 'landingPage.html', context)


#################### logout #######################################
def user_logout(request):
    auth_logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('index')


#################### account page #######################################
@login_required
def account_view(request):
    # Get or create user profile
    profile, created = Profile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = MonthlyIncomeForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Monthly income updated successfully!')
            return redirect('account')
    else:
        form = MonthlyIncomeForm(instance=profile)
    
    context = {
        'form': form,
        'user': request.user,
        'title': 'account'
    }
    return render(request, 'account.html', context)


#################### expenses page #######################################
@login_required
def expenses(request):
    if request.method == 'POST':
        # Check if deleting an expense
        if 'delete_expense_id' in request.POST:
            expense_id = request.POST.get('delete_expense_id')
            try:
                expense = Expense.objects.get(id=expense_id, user=request.user)
                expense.delete()
                messages.success(request, 'Expense deleted successfully!')
            except Expense.DoesNotExist:
                messages.error(request, 'Expense not found.')
            return redirect('expenses')
        
        # Adding a new expense
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()
            messages.success(request, 'Expense added successfully!')
            return redirect('expenses')
    else:
        form = ExpenseForm()
    
    # Get all expenses for the user
    expense_list = Expense.objects.filter(user=request.user)
    
    # Calculate total
    total_amount = expense_list.aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
    
    # Pagination (10 expenses per page)
    paginator = Paginator(expense_list, 10)
    page_number = request.GET.get('page')
    expenses_page = paginator.get_page(page_number)
    
    context = {
        'form': form,
        'expenses': expenses_page,
        'total_amount': total_amount,
    }
    return render(request, 'expenses.html', context)


#################### debt strategies page #######################################
@login_required
def debt_strategies(request):
    if request.method == 'POST':
        # Check if deleting a debt
        if 'delete_debt_id' in request.POST:
            debt_id = request.POST.get('delete_debt_id')
            try:
                debt = Debt.objects.get(id=debt_id, user=request.user)
                debt.delete()
                messages.success(request, 'Debt deleted successfully!')
            except Debt.DoesNotExist:
                messages.error(request, 'Debt not found.')
            return redirect('debt_strategies')
        
        # Adding a new debt
        form = DebtForm(request.POST)
        if form.is_valid():
            debt = form.save(commit=False)
            debt.user = request.user
            debt.save()
            messages.success(request, 'Debt added successfully!')
            return redirect('debt_strategies')
    else:
        form = DebtForm()
    
    # Get user's profile and debts
    profile, created = Profile.objects.get_or_create(user=request.user)
    debts = Debt.objects.filter(user=request.user)
    
    # Calculate total debt
    total_debt = debts.aggregate(Sum('balance'))['balance__sum'] or Decimal('0.00')
    total_minimum = debts.aggregate(Sum('minimum_payment'))['minimum_payment__sum'] or Decimal('0.00')
    
    # Get monthly expenses
    total_expenses = Expense.objects.filter(user=request.user).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
    
    # Calculate available for extra debt payment
    monthly_income = profile.monthly_income
    available_for_debt = monthly_income - total_expenses - total_minimum
    
    # Debt Snowball (smallest balance first)
    snowball_plan = []
    if available_for_debt > 0 and debts.exists():
        snowball_debts = list(debts.order_by('balance'))
        for debt in snowball_debts:
            months_to_payoff = 0
            if available_for_debt > 0:
                payment = debt.minimum_payment + available_for_debt
                months_to_payoff = int((debt.balance / payment).quantize(Decimal('1'), rounding='ROUND_UP'))
            else:
                payment = debt.minimum_payment
                if payment > 0:
                    months_to_payoff = int((debt.balance / payment).quantize(Decimal('1'), rounding='ROUND_UP'))
            
            snowball_plan.append({
                'debt': debt,
                'payment': payment,
                'months': months_to_payoff
            })
    
    # Debt Avalanche (highest interest first)
    avalanche_plan = []
    if available_for_debt > 0 and debts.exists():
        avalanche_debts = list(debts.order_by('-interest_rate'))
        for debt in avalanche_debts:
            months_to_payoff = 0
            if available_for_debt > 0:
                payment = debt.minimum_payment + available_for_debt
                months_to_payoff = int((debt.balance / payment).quantize(Decimal('1'), rounding='ROUND_UP'))
            else:
                payment = debt.minimum_payment
                if payment > 0:
                    months_to_payoff = int((debt.balance / payment).quantize(Decimal('1'), rounding='ROUND_UP'))
            
            avalanche_plan.append({
                'debt': debt,
                'payment': payment,
                'months': months_to_payoff
            })
    
    context = {
        'form': form,
        'debts': debts,
        'total_debt': total_debt,
        'total_minimum': total_minimum,
        'available_for_debt': available_for_debt,
        'monthly_income': monthly_income,
        'snowball_plan': snowball_plan,
        'avalanche_plan': avalanche_plan,
    }
    return render(request, 'debt_strategies.html', context)


#################### saving strategies page #######################################
@login_required
def saving_strategies(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    monthly_income = profile.monthly_income
    
    # Get total expenses and debts
    total_expenses = Expense.objects.filter(user=request.user).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
    total_debt_payment = Debt.objects.filter(user=request.user).aggregate(Sum('minimum_payment'))['minimum_payment__sum'] or Decimal('0.00')
    
    # Calculate 50/30/20 breakdown
    needs = monthly_income * Decimal('0.50')
    wants = monthly_income * Decimal('0.30')
    savings = monthly_income * Decimal('0.20')
    
    # Calculate actual available for savings
    actual_available = monthly_income - total_expenses - total_debt_payment
    
    # Emergency fund (3-6 months of expenses)
    emergency_fund_min = total_expenses * 3
    emergency_fund_max = total_expenses * 6
    
    # If saving the 20%, how many months to reach emergency fund
    months_to_emergency_min = 0
    months_to_emergency_max = 0
    if savings > 0:
        months_to_emergency_min = int((emergency_fund_min / savings).quantize(Decimal('1'), rounding='ROUND_UP'))
        months_to_emergency_max = int((emergency_fund_max / savings).quantize(Decimal('1'), rounding='ROUND_UP'))
    
    context = {
        'title': 'Saving Strategies',
        'monthly_income': monthly_income,
        'total_expenses': total_expenses,
        'total_debt_payment': total_debt_payment,
        'needs': needs,
        'wants': wants,
        'savings': savings,
        'actual_available': actual_available,
        'emergency_fund_min': emergency_fund_min,
        'emergency_fund_max': emergency_fund_max,
        'months_to_emergency_min': months_to_emergency_min,
        'months_to_emergency_max': months_to_emergency_max,
    }
    return render(request, 'saving_strategies.html', context)