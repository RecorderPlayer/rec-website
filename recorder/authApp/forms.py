from PIL import Image

from django import forms
from django.core.exceptions import ValidationError

from .models import UsersModel, NotificationsModel, image_resize
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm, PasswordChangeForm


class UserRegistrationForm(forms.ModelForm):
    email = forms.CharField(max_length=256, widget=forms.TextInput(
        attrs={
            "type": "email",
            "class": "form-control",
            "id": "floatingInput",
            "placeholder": "name@example.com"
        }
    ))

    password = forms.CharField(widget=forms.PasswordInput(
        attrs={
            "type": "password",
            "class": "form-control",
            "id": "floatingPassword",
            "placeholder": "Password"
        }
    ))

    repassword = forms.CharField(widget=forms.PasswordInput(
        attrs={
            "type": "password",
            "class": "form-control",
            "id": "floatingPassword",
            "placeholder": "Password"
        }
    ))

    class Meta:
        model = UsersModel
        fields = ('email',)

    def clean_repassword(self):
        cd = self.cleaned_data
        if cd['password'] != cd['repassword']:
            raise forms.ValidationError('Passwords don\'t match.')

        return cd['repassword']


class UserLogInForm(forms.Form):
    email = forms.CharField(max_length=256, widget=forms.TextInput(
        attrs={
            "type": "email",
            "class": "form-control",
            "id": "floatingInput",
            "placeholder": "name@example.com"
        }
    ))
    password = forms.CharField(widget=forms.PasswordInput(
        attrs={
            "type": "password",
            "class": "form-control",
            "id": "floatingPassword",
            "placeholder": "Password"
        }
    ))


class PasswordResetCustomForm(PasswordResetForm):
    email = forms.CharField(max_length=256, widget=forms.TextInput(
        attrs={
            "type": "email",
            "class": "form-control",
            "id": "floatingInput",
            "placeholder": "name@example.com"
        }
    ))


class PasswordUpdateCustomForm(SetPasswordForm):
    new_password1 = forms.CharField(widget=forms.PasswordInput(
        attrs={
            "type": "password",
            "class": "form-control",
            "id": "floatingPassword",
            "placeholder": "Password"
        }
    ))
    new_password2 = forms.CharField(widget=forms.PasswordInput(
        attrs={
            "type": "password",
            "class": "form-control",
            "id": "floatingPassword",
            "placeholder": "Password"
        }
    ))


class SettingsNotificationsForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(SettingsNotificationsForm, self).__init__(*args, **kwargs)

        notifications = NotificationsModel.objects.filter(user=self.user)
        notifications = [notific for notific in notifications.values()][0]
        for field in iter(self.fields):
            if notifications[field]:
                self.fields[field].widget.attrs.update({
                    "onchange": "document.getElementById('SettingsForm').submit()",
                    "style": "margin-top: 8px;",
                    "class": "form-check-input",
                    "type": "checkbox",
                    "role": "switch",
                    'checked': True
                })

    attrs = {
        "onchange": "document.getElementById('SettingsForm').submit()",
        "style": "margin-top: 8px;",
        "class": "form-check-input",
        "type": "checkbox",
        "role": "switch",
    }

    class Meta:
        model = NotificationsModel
        fields = ['show_notifications', 'on_subscribe', 'on_songs_skips', 'on_new_following_album_created']

    show_notifications = forms.BooleanField(widget=forms.CheckboxInput(
        attrs=attrs
    ), required=False)
    on_songs_skips = forms.BooleanField(widget=forms.CheckboxInput(
        attrs=attrs
    ), required=False)

    on_new_following_album_created = forms.BooleanField(widget=forms.CheckboxInput(
        attrs=attrs
    ), required=False)

    on_subscribe = forms.BooleanField(widget=forms.CheckboxInput(
        attrs=attrs
    ), required=False)


class SettingsProfileForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(SettingsProfileForm, self).__init__(*args, **kwargs)

        user = UsersModel.objects.filter(id=self.user.id)
        user_model_fields = [notific for notific in user.values()][0]

        for field in iter(self.fields):
            if field not in ['avatar', 'banner']:
                if user_model_fields[field] is None:
                    self.fields[field].widget.attrs.update({
                        "type": "text",
                        "class": "form-control",
                        "onchange": "document.getElementById('SettingsForm').submit()",
                        'placeholder': 'Empty'
                    })
                else:
                    pass
                    self.fields[field].widget.attrs.update({
                        "type": "text",
                        "class": "form-control",
                        "onchange": "document.getElementById('SettingsForm').submit()",
                        'value': user_model_fields[field]
                    })
            else:
                self.fields[field].widget = forms.FileInput(
                    attrs={
                        "class": "form-control",
                        "onchange": "document.getElementById('SettingsForm').submit()"
                    }
                )

    def clean(self):

        if self.cleaned_data['email'] == self.user.email:
            self.cleaned_data['email'] = self.user.email

        if UsersModel.objects.get_or_none(
                email=self.cleaned_data['email']) != self.user and UsersModel.objects.get_or_none(
            email=self.cleaned_data['email']) is not None:
            raise ValidationError('User with this email is already exist')

        if self.cleaned_data['username'] in [user.username for user in UsersModel.objects.all()]:
            raise ValidationError('User with this username is already exist')

        return self.cleaned_data

    class Meta:
        model = UsersModel
        fields = ['username', 'email', 'first_name', 'last_name', 'avatar', 'banner']


class SettingsChangePasswordForm(PasswordChangeForm):
    error_messages = {'password_incorrect': "Password incorrect - try again"}

    old_password = forms.CharField(
        required=True,
        label='Old password',
        widget=forms.PasswordInput(attrs={
            "type": "password",
            "class": "form-control",
            "id": "floatingPassword",
            "placeholder": "Password"
        }
        )
    )

    new_password1 = forms.CharField(widget=forms.PasswordInput(
        attrs={
            "type": "password",
            "class": "form-control",
            "id": "floatingPassword",
            "placeholder": "Password"
        }
    ))

    new_password2 = forms.CharField(widget=forms.PasswordInput(
        attrs={
            "type": "password",
            "class": "form-control",
            "id": "floatingPassword",
            "placeholder": "Password"
        }
    ))

    def clean(self):
        if self.cleaned_data.get('new_password1') != self.cleaned_data.get('new_password2'):
            raise ValidationError('Password should match.')
        if self.cleaned_data.get('new_password2') == self.cleaned_data.get('old_password'):
            raise ValidationError('New password shouldn\'t match with new')
        return self.cleaned_data
