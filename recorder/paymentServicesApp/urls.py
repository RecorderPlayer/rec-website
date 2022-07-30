from django.urls import path

from .views import *


urlpatterns = [
    path('', SubscriptionView.as_view(), name='subscription'),
    path('buy/<name>/', StepPeriodSubscriptionView.as_view(), name='subscription_period'),
    path('buy/payment/<name>/', StepPaymentSubscriptionView.as_view(), name='subscription_payment'),
    path('buy_done/', StepDoneSubscriptionView.as_view(), name='subscription_success'),
]