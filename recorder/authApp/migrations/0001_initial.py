# Generated by Django 4.0.5 on 2022-06-24 16:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='NotificationsModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('on_subscribe', models.BooleanField(default=True)),
                ('on_songs_skips', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name': 'Notifications table',
            },
        ),
        migrations.CreateModel(
            name='SocialsNetworksModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('instagram_link', models.CharField(default=None, max_length=256, null=True)),
                ('discord_link', models.CharField(default=None, max_length=256, null=True)),
                ('youtube_link', models.CharField(default=None, max_length=256, null=True)),
                ('twitter_link', models.CharField(default=None, max_length=256, null=True)),
                ('twitch_link', models.CharField(default=None, max_length=256, null=True)),
                ('tiktok', models.CharField(default=None, max_length=256, null=True)),
            ],
            options={
                'verbose_name': 'SocialsNetworks table',
            },
        ),
        migrations.CreateModel(
            name='SpecialsStatusModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('twitch', models.BooleanField(default=False)),
                ('instagram', models.BooleanField(default=False)),
                ('youtube', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': 'SpecialsStatus table',
            },
        ),
        migrations.CreateModel(
            name='UsersModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('crypto_wallet', models.CharField(max_length=256, unique=True)),
                ('username', models.CharField(default=None, max_length=64, null=True, unique=True)),
                ('first_name', models.CharField(max_length=64, null=True)),
                ('last_name', models.CharField(max_length=64, null=True)),
                ('created_at', models.DateTimeField(auto_now=True)),
                ('last_changes', models.DateTimeField()),
                ('avatar', models.BinaryField()),
                ('banned', models.BooleanField(default=False)),
                ('notifications', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='authApp.notificationsmodel')),
                ('social_networks', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='authApp.socialsnetworksmodel')),
                ('special_status', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='authApp.specialsstatusmodel')),
            ],
            options={
                'verbose_name': 'Users table',
            },
        ),
    ]
