# models.py
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    monthly_income = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return self.user.username


# Automatically create profile when user is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()


class Expense(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='expenses')
    description = models.CharField(max_length=200, help_text="What did you spend money on?")
    amount = models.DecimalField(max_digits=10, decimal_places=2, help_text="How much did you spend?")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.description} - ${self.amount}"


class Debt(models.Model):
    DEBT_TYPES = [
        ('credit_card', 'Credit Card'),
        ('student_loan', 'Student Loan'),
        ('car_loan', 'Car Loan'),
        ('mortgage', 'Mortgage'),
        ('personal_loan', 'Personal Loan'),
        ('medical', 'Medical Debt'),
        ('other', 'Other'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='debts')
    name = models.CharField(max_length=200, help_text="Name of the debt (e.g., Chase Credit Card)")
    debt_type = models.CharField(max_length=20, choices=DEBT_TYPES, default='other')
    balance = models.DecimalField(max_digits=10, decimal_places=2, help_text="Current balance owed")
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, help_text="Annual interest rate (%)")
    minimum_payment = models.DecimalField(max_digits=10, decimal_places=2, help_text="Minimum monthly payment")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['balance']
    
    def __str__(self):
        return f"{self.name} - ${self.balance}"