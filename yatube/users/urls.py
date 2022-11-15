from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.urls import path

from . import views

app_name = 'users'

urlpatterns = [
    path(
        'logout/',
        LogoutView.as_view(template_name='users/logged_out.html'),
        name='logout'
    ),
    path('signup/', views.SignUp.as_view(), name='signup'),
    path(
        'login/',
        LoginView.as_view(template_name='users/login.html'),
        name='login'
    ),
    path(
        'password_change_form/',
        PasswordChangeView.
        as_view(template_name='users/password_change_form.html',
                success_url='users/password_change_done.html'),
        name='password_change_form'
    ),
    path(
        'password_change_done/',
        PasswordChangeView.as_view(),
        name='password_change_done'
    ),
    path(
        'password_reset_form/',
        PasswordChangeView.as_view(),
        name='password_reset_form'
    ),
]
