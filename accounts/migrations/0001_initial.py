# Generated by Django 3.2.9 on 2021-11-29 14:27

import accounts.models
import datetime
from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('username', models.CharField(max_length=50, unique=True, validators=[django.core.validators.MinLengthValidator(3)])),
                ('first_name', models.CharField(max_length=75, validators=[django.core.validators.MinLengthValidator(3)], verbose_name='first_name')),
                ('last_name', models.CharField(max_length=75, validators=[django.core.validators.MinLengthValidator(3)], verbose_name='last_name')),
                ('date_of_birth', models.DateField(null=True)),
                ('date_of_creation', models.DateField(default=datetime.datetime.today)),
                ('last_active', models.DateTimeField(default=datetime.datetime.now)),
                ('gender', models.CharField(default='Not Disclosed', max_length=25)),
                ('introduction', models.TextField(null=True)),
                ('looking_for', models.TextField(null=True)),
                ('interests', models.CharField(max_length=100, null=True)),
                ('city', models.CharField(max_length=40, null=True)),
                ('country', models.CharField(max_length=40, null=True)),
                ('main_photo', models.URLField(default='https://static-media-prod-cdn.itsre-sumo.mozilla.net/static/sumo/img/default-FFA-avatar.png', max_length=250)),
                ('is_active', models.BooleanField(default=True)),
                ('is_staff', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Photo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to=accounts.models.user_photos_path)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
