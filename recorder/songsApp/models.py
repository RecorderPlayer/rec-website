from django.core.exceptions import ValidationError
from django.db import models


class SongsModel(models.Model):
    """
    Create a Songs table for the database
    It's a temporary table for testing purposes
    In the future, it will be replaced by a blockchain
    """
    name = models.CharField(max_length=64)
    description = models.TextField(null=True)
    listening = models.BigIntegerField(default=0)
    created_at = models.DateTimeField(auto_now=True)
    author = models.CharField(max_length=256)
    song_file = models.FileField(upload_to='songs/files/')
    icon = models.ImageField(upload_to='songs/images/', null=True)
    price = models.DecimalField(max_digits=18, decimal_places=6)
    owner = models.CharField(max_length=256)

    class Meta:
        verbose_name = "Song"

    def clean(self):
        # Don't allow draft entries to have a pub_date.
        if str(self.song_file).split('.')[-1] not in ['mp3', 'ape', 'flac', 'wav']:
            raise ValidationError(
                {'song_file': "Song file should be some of this formats: 'mp3', 'ape', 'flac', 'wav'"}
            )
        if str(self.icon).split('.')[-1] not in ['jpg', 'jpeg', 'png']:
            raise ValidationError(
                {'icon': "Icon file should be some of this formats: 'jpg', 'jpeg', 'png'"}
            )

    def __str__(self):
        return str(self.name)
