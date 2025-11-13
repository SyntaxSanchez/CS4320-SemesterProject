from django.contrib import admin

# Register your models here.
from .models import Profile, Expense, Debt

@admin.register(Debt)
class DebtAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'debt_type', 'balance', 'interest_rate', 'minimum_payment')
    search_fields = ('user__username', 'name')
    list_filter = ('debt_type',)