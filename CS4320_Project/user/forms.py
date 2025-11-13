from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with that email already exists.")
        return email
        
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("A user with that username already exists.")
        return username


# forms.py
from django import forms
from .models import Profile

class MonthlyIncomeForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['monthly_income']


class MyIntegerForm(forms.Form):
    number_input = forms.IntegerField(
        label="Enter a number",
        min_value=0,  # Optional: set a minimum allowed value
        max_value=100, # Optional: set a maximum allowed value
        required=True, # Optional: make the field required (default is True)
        help_text="Please enter a whole number." # Optional: add help text
    )


from .models import Expense

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['description', 'amount']
        widgets = {
            'description': forms.TextInput(attrs={
                'placeholder': 'e.g., Groceries, Rent, Gas',
                'class': 'expense-input'
            }),
            'amount': forms.NumberInput(attrs={
                'placeholder': 'Enter amount',
                'class': 'expense-input',
                'step': '0.01',
                'min': '0'
            })
        }
        labels = {
            'description': 'Expense Description',
            'amount': 'Amount ($)'
        }
from .models import Debt

class DebtForm(forms.ModelForm):
    class Meta:
        model = Debt
        fields = ['name', 'debt_type', 'balance', 'interest_rate', 'minimum_payment']
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'e.g., Chase Credit Card',
                'class': 'debt-input'
            }),
            'debt_type': forms.Select(attrs={'class': 'debt-input'}),
            'balance': forms.NumberInput(attrs={
                'placeholder': '0.00',
                'class': 'debt-input',
                'step': '0.01',
                'min': '0'
            }),
            'interest_rate': forms.NumberInput(attrs={
                'placeholder': '0.00',
                'class': 'debt-input',
                'step': '0.01',
                'min': '0',
                'max': '100'
            }),
            'minimum_payment': forms.NumberInput(attrs={
                'placeholder': '0.00',
                'class': 'debt-input',
                'step': '0.01',
                'min': '0'
            }),
        }
        labels = {
            'name': 'Debt Name',
            'debt_type': 'Type of Debt',
            'balance': 'Current Balance ($)',
            'interest_rate': 'Interest Rate (%)',
            'minimum_payment': 'Minimum Monthly Payment ($)',
        }