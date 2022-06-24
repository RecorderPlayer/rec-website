from django.db import models


class UsersModel(models.Model):
    """
    Create a Users table for the database
    """
    crypto_wallet = models.CharField(max_length=256, unique=True)
    username = models.CharField(
        max_length=64, unique=True, null=True, default=None)
    first_name = models.CharField(max_length=64, null=True)
    last_name = models.CharField(max_length=64, null=True)
    created_at = models.DateTimeField(auto_now=True)
    last_changes = models.DateTimeField()
    avatar = models.BinaryField()

    notifications = models.ForeignKey(
        'authApp.NotificationsModel', on_delete=models.CASCADE)
    # premium = models.ForeignKey('payments.PremiumsModel', on_delete=models.CASCADE)

    # queue = models.ManyToManyField('songs.SongsModel')
    # playlists = models.ManyToManyField('playlist.PlaylistsModel')
    # albums = models.ManyToManyField('albums.AlbumsModel')
    banned = models.BooleanField(default=False)
    special_status = models.ForeignKey('authApp.SpecialsStatusModel', null=True, on_delete=models.SET_NULL)
    social_networks = models.ForeignKey('authApp.SocialsNetworksModel', null=True, on_delete=models.SET_NULL)

    class Meta:
        verbose_name = "Users table"

    def __str__(self):
        return str(self.crypto_wallet)


class NotificationsModel(models.Model):
    """
    Create a Notifications table for the database
    """
    on_subscribe = models.BooleanField(default=True)
    on_songs_skips = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Notifications table"

    def __str__(self):
        return str(self.id)


class SpecialsStatusModel(models.Model):
    """
    Create a SpecialsStatus table for the database
    """

    twitch = models.BooleanField(default=False)
    instagram = models.BooleanField(default=False)
    youtube = models.BooleanField(default=False)

    class Meta:
        verbose_name = "SpecialsStatus table"

    def __str__(self):
        return str(self.id)


class SocialsNetworksModel(models.Model):
    """
    Create a SocialsNetworks table for the database
    """

    instagram_link = models.CharField(max_length=256, null=True, default=None)
    discord_link = models.CharField(max_length=256, null=True, default=None)
    youtube_link = models.CharField(max_length=256, null=True, default=None)
    twitter_link = models.CharField(max_length=256, null=True, default=None)
    twitch_link = models.CharField(max_length=256, null=True, default=None)
    tiktok = models.CharField(max_length=256, null=True, default=None)

    class Meta:
        verbose_name = "SocialsNetworks table"

    def __str__(self):
        return str(self.id)