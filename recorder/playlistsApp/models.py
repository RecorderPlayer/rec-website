from django.core.exceptions import ValidationError
from django.db import models


class PlaylistsModel(models.Model):

    """
    Create a Playlists table for the database
    """
    name = models.CharField(max_length=64)
    description = models.TextField(null=True, blank=True)
    icon = models.ImageField(null=True, upload_to='playlists_icons/', blank=True)
    songs = models.ManyToManyField('songsApp.SongsModel', null=True, blank=True)
    rate = models.FloatField(default=0)
    author = models.ForeignKey('authApp.UsersModel', on_delete=models.CASCADE, default=None)

    class Meta:
        verbose_name = "Playlist"

    def clean(self):
        if str(self.icon).split('.')[-1] not in ['jpg', 'jpeg', 'png']:
            raise ValidationError(
                {'icon': "Icon file should be some of this formats: 'jpg', 'jpeg', 'png'"}
            )

    def __str__(self):
        return str(self.name)
