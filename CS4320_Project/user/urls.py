from django.urls import path
from django.contrib.auth import views as auth_views
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('expenses/', views.expenses, name='expenses'),
    path('landingPage/', views.landingPage, name='landingPage'),
    path('account/', views.account_view, name='account'),
    path('debt-strategies/', views.debt_strategies, name='debt_strategies'),
    path('saving-strategies/', views.saving_strategies, name='saving_strategies'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),


    path('landingPage/', views.landingPage, name='landingPage'),

    path('password-reset/',
         auth_views.PasswordResetView.as_view(template_name='user/password_reset.html'),
         name='password_reset'),

    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(template_name='user/password_reset_done.html'),
         name='password_reset_done'),

    path('password-reset-confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name='user/password_reset_confirm.html'),
         name='password_reset_confirm'),

    path('password-reset-complete/',
         auth_views.PasswordResetCompleteView.as_view(template_name='user/password_reset_complete.html'),
         name='password_reset_complete'),
]
