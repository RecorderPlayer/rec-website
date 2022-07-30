from django.urls import path
from django.contrib.auth import views as auth_views

from .views import *
from .forms import *


urlpatterns = [
    path('register/', RegisterUserView.as_view(), name='register'),
    path('login/', LogInView.as_view(), name='log-in'),
    path('me/', ProfileView.as_view(), name='profile'),
    path('verify/<uidb64>/<token>/', ActivateUserView.as_view(), name='activate'),
    path('settings/notifications/', SettingsNotificationsView.as_view(), name='settings-notifications'),
    path('settings/profile/', SettingsProfileView.as_view(), name='settings-profile'),
    path('settings/security/', SettingsSecurityView.as_view(), name='settings-security'),
    path('settings/security/change-password/', SettingsSecurityChangePasswordView.as_view(), name='settings-security-change-password'),
    path('settings/security/logs/', SettingsSecurityLogsView.as_view(), name='settings-security-logs'),
    path('settings/subscription/', SettingsSubscriptionMenuView.as_view(), name='settings-subscription'),
    path(
        'password_reset/',
        auth_views.PasswordResetView.as_view(template_name='authApp/email_verify/password_reset.html',
                                             form_class=PasswordResetCustomForm),
        name='password_reset'
    ),
    path(
        'password_reset/done/',
        auth_views.PasswordResetDoneView.as_view(template_name='authApp/email_verify/sent_email.html'),
        name='password_reset_done'),
    path(
        'reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(template_name='authApp/email_verify/password_update.html',
                                                    form_class=PasswordUpdateCustomForm),
        name='password_reset_confirm'),
    path(
        'reset/done/',
        auth_views.PasswordResetCompleteView.as_view(template_name='authApp/email_verify/confirm_template.html'),
        name='password_reset_complete'
    ),
]