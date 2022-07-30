import os
from datetime import timedelta
from dateutil.relativedelta import relativedelta

from django.http import HttpResponse
from hexbytes import HexBytes
import json
import struct

import requests
from django.contrib import messages
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views import View

from authApp.mixins import LoggedInRedirectMixin
from authApp.models import UsersModel
from django.views.generic import TemplateView, DetailView
from web3 import Web3

from dotenv import load_dotenv

from .models import SubscriptionsModel, UserPaymentsHistoryModel, PremiumsModel, PayMethodsModel, PremiumsOwnersModel
from .forms import ChoicePeriodOfSubscriptionForm

load_dotenv()


class HexJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, HexBytes):
            return obj.hex()
        return super().default(obj)


class SubscriptionView(LoggedInRedirectMixin, View):

    # if user didn't verified
    redirect_url = '/user/login/'

    def get(self, request, *args, **kwargs):
        subscriptions = SubscriptionsModel.objects.all().order_by('price')

        premium = PremiumsOwnersModel.objects.filter(owner=request.user)
        if len(premium) > 0:
            premium = premium.first()
            return render(
                request,
                'paymentServicesApp/subscription.html',
                {
                    'title': 'RecorderPlayer | Subscription',
                    'step': 'already-bought',
                    'settings': True,
                    'subscriptions': SubscriptionsModel.objects.filter(id=premium.subscription.id)
                }
            )

        return render(
            request,
            'paymentServicesApp/subscription.html',
            {
                'title': 'RecorderPlayer | Subscription',
                'subscriptions': subscriptions,
                'settings': True
            }
        )


class StepPeriodSubscriptionView(LoggedInRedirectMixin, TemplateView):

    redirect_url = '/user/login/'
    template_name = 'paymentServicesApp/buy.html'

    def get_context_data(self, **kwargs):
        context = super(StepPeriodSubscriptionView, self).get_context_data(**kwargs)

        name = kwargs.get('name')
        subscription = SubscriptionsModel.objects.filter(name=name)
        context['title'] = 'RecorderPlayer | Subscription'

        if not len(subscription) > 0:
            context['messages'] = ['Such a subscription option does not exist.']
            return context

        context['subscription'] = SubscriptionsModel.objects.filter(name=name).first()
        context['form'] = ChoicePeriodOfSubscriptionForm()
        context['step'] = 'period'
        return context

    def post(self, request, *args, **kwargs):

        form = ChoicePeriodOfSubscriptionForm(request.POST)

        name = kwargs.get('name')
        subscription = SubscriptionsModel.objects.filter(name=name)

        if not len(subscription) > 0:
            return render(request, 'paymentServicesApp/buy.html', {
                'title': 'RecorderPlayer | Buy Subscription',
                'messages': 'Such a subscription option does not exist'
            })

        if form.is_valid():
            subscription = subscription.first()
            period = form.cleaned_data['period']
            if int(period) == 3:
                discount = 5

                sale = (subscription.price * int(period))/100 * 5
                price = (subscription.price * int(period)) - sale
                price = f"{price:.{2}f}"
            elif int(period) == 12:
                discount = 10

                sale = (subscription.price * int(period))/100 * discount
                price = (subscription.price * int(period)) - sale
                price = f"{price:.{2}f}"
            else:
                price = subscription.price
                discount = None

        return render(request, 'paymentServicesApp/buy.html', {
            'title': 'RecorderPlayer | Buy Subscription',
            'step': 'payment',
            'wallet_to': os.getenv('WALLET_TO'),
            'subscription': subscription,
            'price': price,
            'period': period,
            'discount': discount
        })


class StepPaymentSubscriptionView(LoggedInRedirectMixin, TemplateView):

    redirect_url = '/user/login/'

    def get(self, request, *args, **kwargs):
        name = kwargs.get('name')
        period = request.GET.get('period')

        subscription = SubscriptionsModel.objects.filter(name=name)
        if not len(subscription) > 0:
            messages.error(request, 'Such a subscription option does not exist')
            return render(request, 'paymentServicesApp/buy.html', {
                'title': 'RecorderPlayer | Subscription'
            })

        subscription = subscription.first()
        if int(period) == 3:
            discount = 5

            sale = (subscription.price * int(period))/100 * 5
            price = (subscription.price * int(period)) - sale
            price = f"{price:.{2}f}"
        elif int(period) == 12:
            discount = 10

            sale = (subscription.price * int(period))/100 * discount
            price = (subscription.price * int(period)) - sale
            price = f"{price:.{2}f}"
        else:
            price = subscription.price
            discount = None

        usd_to_eth = requests.get('https://min-api.cryptocompare.com/data/price?fsym=ETH&tsyms=USD,EUR,ETH').json()
        price_eth = int((1/usd_to_eth['USD'] * float(price)) * 1000000000000000000)
        return render(
            request,
            'paymentServicesApp/buy.html',
            {
                'title': 'RecorderPlayer | Subscription',
                'price': price,
                'price_eth': price_eth,
                'period': period,
                'discount': discount,
                'step': 'payment',
                'wallet_to': os.getenv('WALLET_TO'),
                'subscription': SubscriptionsModel.objects.filter(name=name).first()
            }
        )

    def post(self, request, *args, **kwargs):
        name = kwargs.get('name')
        error_code = request.POST.get('error_code')
        message = request.POST.get('message')
        period = request.POST.get('period')

        subscription = SubscriptionsModel.objects.filter(name=name)
        if not len(subscription) > 0:
            messages.error(request, 'Such a subscription option does not exist')
            return render(request, 'paymentServicesApp/buy.html', {
                'title': 'RecorderPlayer | Subscription'
            })

        subscription = subscription.first()
        if int(period) == 3:
            discount = 5

            sale = (subscription.price * int(period)) / 100 * 5
            price = (subscription.price * int(period)) - sale
            price = f"{price:.{2}f}"
        elif int(period) == 12:
            discount = 10

            sale = (subscription.price * int(period)) / 100 * discount
            price = (subscription.price * int(period)) - sale
            price = f"{price:.{2}f}"
        else:
            price = subscription.price
            discount = None

        usd_to_eth = requests.get('https://min-api.cryptocompare.com/data/price?fsym=ETH&tsyms=USD,EUR,ETH').json()
        price_eth = int((1 / usd_to_eth['USD'] * float(price)) * 1000000000000000000)
        if error_code:
            message = message.split("'")[0]

            if error_code == '4001':
                message = 'The request was rejected by the user'
            elif error_code == '-32602':
                message = 'The parameters were invalid'
            elif error_code == '-32603':
                message = 'Internal error'
            messages.error(request, f'Error code: {error_code}<ul><b>{message}</b></ul>')
            return render(
                request,
                'paymentServicesApp/buy.html',
                {
                    'title': 'RecorderPlayer | Subscription',
                    'price': price,
                    'price_eth': price_eth,
                    'period': period,
                    'discount': discount,
                    'step': 'payment',
                    'wallet_to': os.getenv('WALLET_TO'),
                    'subscription': SubscriptionsModel.objects.filter(name=name).first()
                }
            )

        # connect to the web3 network
        web3 = Web3(Web3.HTTPProvider('http://127.0.0.1:7545'))
        tx_hash = request.POST.get('txHash')
        wallet_from = request.POST.get('from')

        if web3.isConnected():
            transaction = web3.eth.get_transaction(tx_hash)
            tx_dict = dict(transaction)
            transaction_json = json.dumps(tx_dict, cls=HexJsonEncoder)
            transaction_json = json.loads(transaction_json)

            payment_history = UserPaymentsHistoryModel.objects.filter(hash=transaction_json['hash'])
            message = None
            if len(payment_history) > 1:
                message = f'This transaction was already activated.'
                messages.error(request, message)
            else:

                if transaction_json['from'].lower() != wallet_from.lower():
                    message = f'This transaction was made not by this wallet {wallet_from}'
                    messages.error(request, message)
                elif transaction_json['to'].lower()[0:10] != os.getenv('WALLET_TO').lower()[0:10]:
                    message = 'This transaction was made to the wrong wallet.'
                    messages.error(request, message)

                _price = f"{float(price):.{2}f}"
                _eth_price = f"{float(transaction_json['value']) / (1 / usd_to_eth['USD']) / 1000000000000000000:.{2}f}"
                if float(_price[:-1]) > float(_eth_price[:-1]):
                    message = 'The price of this operation is lower than necessary.<br>' \
                              f"You paid ${_eth_price} but should ${_price}.\nContact with us to solve this problem."
                    messages.error(request, message)
            if message is not None:
                return render(
                    request,
                    'paymentServicesApp/buy.html',
                    {
                        'title': 'RecorderPlayer | Subscription',
                        'price': price,
                        'price_eth': price_eth,
                        'period': period,
                        'discount': discount,
                        'step': 'payment',
                        'wallet_to': os.getenv('WALLET_TO'),
                        'subscription': SubscriptionsModel.objects.filter(name=name).first()
                    }
                )
        # saving data
        now = timezone.now()

        pay_methods = PayMethodsModel.objects.filter(name='MetaMask')
        if len(pay_methods) == 1:
            pay_methods = pay_methods.first()
        else:
            pay_methods = PayMethodsModel.objects.create(name='MetaMask')
        premium_get_period = PremiumsOwnersModel.objects.filter(owner=request.user).first()
        if premium_get_period:
            timedelta_period = (now + timedelta(days=int(period) * 30))
            period_of_subscription = premium_get_period.period + relativedelta(
                months=timedelta_period.month,
                days=timedelta_period.day,
                hours=timedelta_period.hour,
                minutes=timedelta_period.minute,
                seconds=timedelta_period.second,
                microseconds=timedelta_period.microsecond
            )
        else:
            period_of_subscription = (now + timedelta(days=int(period) * 30))

        premium = PremiumsOwnersModel.objects.filter(owner=request.user)
        if len(premium) == 1:
            core = premium.update(
                activated_at=now,
                price=price,
                active=True,
                period=period_of_subscription,
                method=pay_methods,
                subscription=subscription
            )
        else:
            core = PremiumsOwnersModel.objects.create(
                owner=request.user,
                activated_at=now,
                price=price,
                active=True,
                period=period_of_subscription,
                method=pay_methods,
                subscription=subscription
            )

        PremiumsModel.objects.filter(user=request.user).update(
            owner=core
        )

        UserPaymentsHistoryModel.objects.create(
            price=price,
            method=pay_methods,
            subscription=subscription,
            made_at=now,
            period=period_of_subscription,
            wallet_from=wallet_from,
            wallet_to=os.getenv('WALLET_TO'),
            hash=tx_hash,
            account=request.user
        )

        return HttpResponse(json.dumps({'status': 'success'}), content_type="application/json")


class StepDoneSubscriptionView(LoggedInRedirectMixin, View):

    redirect_url = '/user/login/'

    def get(self, request, *args, **kwargs):
        premium = PremiumsOwnersModel.objects.filter(owner=request.user).first()
        pay_history = UserPaymentsHistoryModel.objects.filter(account=request.user).last()
        if not pay_history:
            messages.error(request, 'Error while trying to find your premium.')
            return render(
                request,
                'paymentServicesApp/buy.html',
                {
                    'title': 'RecorderPlayer | Subscription',
                    'step': 'done',
                }
            )
        return render(
            request,
            'paymentServicesApp/buy.html',
            {
                'title': 'RecorderPlayer | Subscription',
                'price': pay_history.price,
                'end_at': premium.period,
                'step': 'done',
                'from': pay_history.wallet_from,
                'hash': pay_history.hash,
                'subscription': pay_history.subscription
            }
        )
