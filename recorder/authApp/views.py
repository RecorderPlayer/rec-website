import ip2geotools
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.datastructures import MultiValueDictKeyError
from django.utils.http import urlsafe_base64_decode
from django.utils.timezone import now
from django.views import View
from django.utils.encoding import force_str
from ip2geotools.databases.noncommercial import DbIpCity

from .forms import UserRegistrationForm, UserLogInForm, SettingsNotificationsForm, SettingsProfileForm, \
    SettingsChangePasswordForm

from .mixins import LoggedInRedirectMixin
from .models import NotificationsModel, SocialsNetworksModel, SpecialsStatusModel, UsersModel, UserDevicesModel
from paymentServicesApp.models import PremiumsModel
from .utils import send_action_email, generate_token


class RegisterUserView(View):

    def post(self, request, *args, **kwargs):
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.is_active = False
            user.is_email_verified = False
            user.save()

            user = UsersModel.objects.get_or_none(id=user.id)
            if user is not None:
                user.notifications = NotificationsModel.objects.create(user=user)
                user.premium = PremiumsModel.objects.create(user=user)
                user.special_status = SpecialsStatusModel.objects.create(user=user)
                user.social_networks = SocialsNetworksModel.objects.create(user=user)
                user.save()

            send_action_email(request, user)

            login(request, user)
            return render(request, 'authApp/signup.html', {'user': user, 'register': False})
        return render(request, 'authApp/signup.html', {'form': form, 'register': True})

    def get(self, request, *args, **kwargs):
        user_form = UserRegistrationForm()
        return render(request, 'authApp/signup.html', {'form': user_form, 'register': True})


class LogInView(View):

    def post(self, request, *args, **kwargs):

        form = UserLogInForm(request.POST)
        if form.is_valid():
            user = authenticate(
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password']
            )
            if user is not None:
                if user.is_active:
                    login(request, user)

                    # update account devices
                    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
                    if x_forwarded_for is not None:
                        ip = x_forwarded_for.split(',')[0]
                    else:
                        ip = request.META.get('REMOTE_ADDR')

                    name = request.headers.get('User-Agent').split('(')[1].split(')')[0] + \
                           request.headers.get('User-Agent').split(')')[-1]

                    devices = UserDevicesModel.objects.filter(account=user)
                    try:
                        place = DbIpCity.get(ip)
                    except ip2geotools.errors.InvalidRequestError:
                        place = None
                        country = 'Unknown'
                        coord = 'Unknown'
                    if ip not in [device.ip for device in devices] or name not in [device.name for device in devices]:
                        UserDevicesModel.objects.create(
                            account=user,
                            ip=ip,
                            name=name,
                            country=f'{place.region}, {place.country}, {place.city}' if place is not None else country,
                            coord=f'{place.latitude} {place.longitude}' if place is not None else coord,
                            is_active=True,
                            last_login=now(),
                            joined_at=now()
                        )
                    else:
                        for device in devices:
                            if device.ip == ip:
                                UserDevicesModel.objects.filter(id=device.id).update(
                                    last_login=now(),
                                    is_active=True,
                                    country=f'{place.region}, {place.country}, {place.city}',
                                    coord=f'{place.latitude} {place.longitude}',
                                )

                    redirect_to = request.path.split('/?')[-1]
                    if redirect_to == request.path:
                        return redirect('profile')
                    else:
                        return redirect(redirect_to)
                else:
                    return HttpResponse('Disabled account')
            else:
                messages.error(request, 'Email or password was wrong!')
                return render(request, 'authApp/login.html', {
                    'user': user,
                    'form': form,
                    })

    def get(self, request, *args, **kwargs):
        form = UserLogInForm()
        return render(request, 'authApp/login.html', {'form': form})


class ProfileView(View):

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return render(request, 'authApp/profile.html')
        else:
            user_form = UserRegistrationForm()
            return render(request, 'authApp/signup.html', {'form': user_form, 'register': True})


class ActivateUserView(View):

    def get(self, request, uidb64, token, **kwargs):
        try:
            user_id = force_str(urlsafe_base64_decode(uidb64))
            user = UsersModel.objects.get(pk=user_id)
        except Exception as e:
            user = None

        if user and generate_token.check_token(user, token):
            user.is_email_verified = True
            user.is_active = True
            user.save()

            return render(request, 'authApp/email_verify/confirm_template.html', {'success': True})
        return render(request, 'authApp/email_verify/confirm_template.html', {'success': False})


class SettingsNotificationsView(LoggedInRedirectMixin, View):

    # if user didn't verified
    redirect_url = '/user/login/'

    def post(self, request, *args, **kwargs):

        form = SettingsNotificationsForm(request.POST, user=request.user)
        f_nums = [f for f in form]

        if form.is_valid():
            NotificationsModel.objects.filter(user=request.user).update(
                show_notifications=form.cleaned_data['show_notifications'],
                on_subscribe=form.cleaned_data['on_subscribe'],
                on_songs_skips=form.cleaned_data['on_songs_skips'],
                on_new_following_album_created=form.cleaned_data['on_new_following_album_created'],
            )

            form = SettingsNotificationsForm(user=request.user)
            f_nums = [f for f in form]

        notifications_dict = []
        for index, field in enumerate(form.fields):
            notifications_dict.append({
                    'name': field,
                    'type': form.fields[field],
                    'verbose_name': NotificationsModel._meta.get_field(field).verbose_name,
                    'help_text': NotificationsModel._meta.get_field(field).help_text,
                    'input': f_nums[index]
                }
            )

        messages.success(request, 'Your notifications was update!')
        return render(request, 'authApp/settings/notifications.html', {
            'settings_type': 'Notifications',
            'notifications': notifications_dict
        })

    def get(self, request, *args, **kwargs):
        notifications = NotificationsModel.objects.filter(user=request.user)
        notifications = [notific for notific in notifications.values()][0]

        form = SettingsNotificationsForm(user=request.user)
        f_nums = [f for f in form]

        notifications_dict = []
        for index, field in enumerate(form.fields):
            notifications_dict.append({
                    'name': field,
                    'type': notifications[field],
                    'verbose_name': NotificationsModel._meta.get_field(field).verbose_name,
                    'help_text': NotificationsModel._meta.get_field(field).help_text,
                    'input': f_nums[index]
                }
            )

        return render(request, 'authApp/settings/notifications.html', {
            'settings_type': 'Notifications',
            'notifications': notifications_dict,
        })


class SettingsProfileView(LoggedInRedirectMixin, View):

    # if user didn't verified
    redirect_url = '/user/login/'

    def post(self, request, *args, **kwargs):
        form = SettingsProfileForm(request.POST, request.FILES, user=request.user, instance=request.user)
        if form.is_valid():
            user = UsersModel.objects.get_or_none(id=request.user.id)
            if user is not None:
                try:
                    if form.cleaned_data.get('avatar') is not None and request.FILES['avatar']:
                        user.avatar.delete(save=True)
                except MultiValueDictKeyError:
                    pass

                try:
                    if form.cleaned_data.get('banner') is not None and request.FILES['banner']:
                        user.banner.delete(save=True)
                except MultiValueDictKeyError:
                    pass

            if user.email != form.cleaned_data.get('email'):
                # save form for update email
                form.save()

                # get updated user
                user = UsersModel.objects.get_or_none(id=request.user.id)
                user.is_active = False
                user.is_email_verified = False
                user.save()

                send_action_email(request, user)
                messages.success(request, 'Your profile was update!\nTo verify your new email - check mailbox')
            else:
                messages.success(request, 'Your profile was update!')
                form.save()

            form = SettingsProfileForm(user=request.user, instance=request.user)

        if form.errors:
            messages.error(request, form.errors)
            return redirect('settings-profile')

        return render(
            request,
            'authApp/settings/profile.html',
            {
                'settings_type': 'Profile',
                'form': form
            }
        )

    def get(self, request, *args, **kwargs):
        form = SettingsProfileForm(user=request.user, instance=request.user)
        return render(
            request,
            'authApp/settings/profile.html',
            {
                'settings_type': 'Profile',
                'form': form,
            }
        )


class SettingsSecurityView(LoggedInRedirectMixin, View):

    # if user didn't verified
    redirect_url = '/user/login/'

    def get(self, request, *args, **kwargs):

        return render(
            request,
            'authApp/settings/security.html',
            {
                'settings_type': 'Security'
            }
        )


class SettingsSecurityLogsView(LoggedInRedirectMixin, View):

    # if user didn't verified
    redirect_url = '/user/login/'

    def get(self, request, *args, **kwargs):

        devices = UserDevicesModel.objects.filter(account=request.user)

        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for is not None:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')

        name = request.headers.get('User-Agent').split('(')[1].split(')')[0] + \
               request.headers.get('User-Agent').split(')')[-1]

        current_device = devices.get(ip=ip, name=name)
        return render(
            request,
            'authApp/settings/logs.html',
            {
                'settings_type': 'Security Logs',
                'devices': devices,
                'current_device': current_device
            }
        )


class SettingsSecurityChangePasswordView(LoggedInRedirectMixin, View):

    # if user didn't verified
    redirect_url = '/user/login/'

    def post(self, request, *args, **kwargs):
        form = SettingsChangePasswordForm(user=request.user, data=request.POST)

        if form.is_valid():
            form.save()
            UserDevicesModel.objects.filter(account=request.user).delete()
            messages.success(request, 'Your password was updated! ')

            return redirect('log-in')

        return render(
            request,
            'authApp/settings/change-password.html',
            {
                'settings_type': 'Change Password',
                'form': form
            }
        )

    def get(self, request, *args, **kwargs):
        instance_user = get_object_or_404(UsersModel, id=int(request.user.id))
        form = SettingsChangePasswordForm(instance_user)

        return render(
            request,
            'authApp/settings/change-password.html',
            {
                'settings_type': 'Change Password',
                'form': form
            }
        )


class SettingsSubscriptionMenuView(LoggedInRedirectMixin, View):

    # if user didn't verified
    redirect_url = '/user/login/'

    def get(self, request, *args, **kwargs):
        return render(
            request,
            'authApp/settings/subscriptions.html',
            {
                'settings_type': 'Subscription',
            }
        )
