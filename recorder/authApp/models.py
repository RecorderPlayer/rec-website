import os
from typing import Optional

from paymentServicesApp.models import *

from django.core.exceptions import ValidationError
from django.contrib.auth.models import User, AbstractUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.files import File

from pathlib import Path
from PIL import Image
from io import BytesIO


def upload_avatar(instance, filename):
    format = filename.split('.')[-1]
    return f'users_avatars/{instance.id}.{format}'


def upload_banner(instance, filename):
    format = filename.split('.')[-1]

    return f'users_banners/{instance.id}.{format}'


def image_resize(user_id, image, width, height):
    img = Image.open(image)
    if img.width > width or img.height > height:
        output_size = (width, height)
        img.thumbnail(output_size)

        img_filename = f"{user_id}.{Path(image.file.name).name.split('.')[-1]}"
        img_suffix = img_filename.split(".")[-1]

        buffer = BytesIO()
        img.save(buffer, format=img_suffix)
        file_object = File(buffer)
        image.save(img_filename, file_object)


class CustomUserManager(BaseUserManager):

    def create_superuser(self, email, password, username):

        if username is None:
            raise TypeError('Superusers must have a username.')

        if password is None:
            raise TypeError('Superusers must have a password.')

        user = self.create_user(email, password, username)
        user.is_superuser = True
        user.is_staff = True
        user.is_email_verified = True
        user.save()

        return user

    def create_user(self, email, password, username: Optional[str] = None, first_name: Optional[str] = None, last_name: Optional[str] = None, **kwargs):

        if not username:
            raise ValidationError(_("You must provide a username."))
        if not password:
            raise ValidationError(_("You must provide a password."))

        user = self.model(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email
        )
        if password:
            user.set_password(password)
        else:
            user.set_password(self.make_random_password())
        user.save()

        PremiumsModel.objects.create(user=user)
        SpecialsStatusModel.objects.create(user=user)
        SocialsNetworksModel.objects.create(user=user)
        NotificationsModel.objects.create(user=user)
        return user

    def get_or_none(self, *args, **kwargs):
        try:
            return self.model.objects.get(**kwargs)
        except self.model.DoesNotExist:
            return None


class UsersModel(AbstractUser, PermissionsMixin):
    """
    Create a Users table for the database
    """

    password = models.CharField(max_length=256)
    email = models.EmailField(max_length=256, unique=True)
    is_email_verified = models.BooleanField(default=False)
    username = models.CharField(
        max_length=64, unique=True, null=True, blank=True)
    first_name = models.CharField(max_length=64, null=True, blank=True)
    last_name = models.CharField(max_length=64, null=True, blank=True)
    created_at = models.DateTimeField(auto_now=True)
    last_changes = models.DateTimeField(blank=True, null=True)

    avatar = models.ImageField(upload_to=upload_avatar, null=True, blank=True, default=None)
    banner = models.ImageField(upload_to=upload_banner, null=True, blank=True, default=None)

    queue = models.ManyToManyField('songsApp.SongsModel', blank=True)
    playlists = models.ManyToManyField('playlistsApp.PlaylistsModel', blank=True)
    albums = models.ManyToManyField('albumsApp.AlbumsModel', blank=True)
    banned = models.BooleanField(default=False)

    followers = models.ManyToManyField('authApp.UsersModel', related_name="FollowersUser", blank=True)
    following = models.ManyToManyField('authApp.UsersModel', related_name="FollowingUser", blank=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = "User"

    def clean(self):
        if str(self.avatar) and str(self.avatar).split('.')[-1] not in ['jpg', 'jpeg', 'png']:
            raise ValidationError(
                {'avatar': "Icon file should be some of this formats: 'jpg', 'jpeg', 'png'"}
            )

    def save(self, commit=True, *args, **kwargs):
        if commit:
            try:
                if self.avatar:
                    image_resize(self.id, self.avatar, 250, 250)
            except:
                pass
            try:
                if self.banner:
                    image_resize(self.id, self.banner, 1200, 600)
            except:
                pass
        super(UsersModel, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.email)


class NotificationsModel(models.Model):
    """
    Create a Notifications table for the database
    """
    user = models.OneToOneField('authApp.UsersModel', on_delete=models.CASCADE, default=None, null=True)
    show_notifications = models.BooleanField(
        verbose_name='Show notifications',
        help_text='Choose will u get notifications or not',
        default=True)
    on_subscribe = models.BooleanField(verbose_name='On subscribe', help_text='When someone start followed you', default=True)
    # only for desktop apps
    on_songs_skips = models.BooleanField(verbose_name='On songs skips', help_text='When start playing next song', default=True)
    on_new_following_album_created = models.BooleanField(
        verbose_name='On new following album created',
        help_text='Someone on who you were subscribe, release new album',
        default=True
    )

    class Meta:
        verbose_name = "Notification"

    def __str__(self):
        return str(self.id)


class SpecialsStatusModel(models.Model):
    """
    Create a SpecialsStatus table for the database
    """
    user = models.OneToOneField('authApp.UsersModel', on_delete=models.CASCADE, default=None, null=True)
    twitch = models.BooleanField(default=False)
    instagram = models.BooleanField(default=False)
    youtube = models.BooleanField(default=False)

    class Meta:
        verbose_name = "SpecialsStatus"
        verbose_name_plural = "SpecialsStatuses"

    def __str__(self):
        return str(self.id)


class SocialsNetworksModel(models.Model):
    """
    Create a SocialsNetworks table for the database
    """
    user = models.OneToOneField('authApp.UsersModel', on_delete=models.CASCADE, default=None, null=True)
    instagram_link = models.CharField(max_length=256, null=True, blank=True)
    discord_link = models.CharField(max_length=256, null=True, blank=True)
    youtube_link = models.CharField(max_length=256, null=True, blank=True)
    twitter_link = models.CharField(max_length=256, null=True, blank=True)
    twitch_link = models.CharField(max_length=256, null=True, blank=True)
    tiktok = models.CharField(max_length=256, null=True, blank=True)

    class Meta:
        verbose_name = "SocialsNetwork"

    def __str__(self):
        return str(self.id)


class UserDevicesModel(models.Model):

    account = models.ForeignKey('authApp.UsersModel', on_delete=models.CASCADE)

    ip = models.GenericIPAddressField(verbose_name='IP Address')
    name = models.CharField(verbose_name='Device name', max_length=128)
    country = models.CharField(verbose_name='Country name', max_length=128)
    coord = models.CharField(verbose_name='Coord', max_length=128)
    is_active = models.BooleanField(verbose_name='Is active')

    last_login = models.DateTimeField(verbose_name='Last Login')
    joined_at = models.DateTimeField(verbose_name='Joined at')

    def __str__(self):
        return str(self.ip)