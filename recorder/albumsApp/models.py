from django.core.exceptions import ValidationError
from django.db import models


class AlbumsModel(models.Model):
    """
    Create a Albums table for the database
    """
    name = models.CharField(max_length=64)
    description = models.TextField(null=True)
    icon = models.ImageField(upload_to='albums_icons/', null=True)
    songs = models.ManyToManyField('songsApp.SongsModel')
    rate = models.FloatField(default=0)
    author = models.ForeignKey('authApp.UsersModel', on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Album"

    def clean(self):
        if str(self.icon).split('.')[-1] not in ['jpg', 'jpeg', 'png']:
            raise ValidationError(
                {'icon': "Icon file should be some of this formats: 'jpg', 'jpeg', 'png'"}
            )

    def __str__(self):
        return str(self.name)