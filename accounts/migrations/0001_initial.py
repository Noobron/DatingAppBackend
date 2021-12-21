# Generated by Django 3.2.9 on 2021-12-21 13:21

import accounts.models
import datetime
from django.conf import settings
import django.contrib.postgres.fields.citext
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
from django.contrib.postgres.operations import CITextExtension


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        CITextExtension(),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('username', django.contrib.postgres.fields.citext.CICharField(max_length=50, unique=True, validators=[django.core.validators.MinLengthValidator(3)])),
                ('first_name', models.CharField(max_length=75, validators=[django.core.validators.MinLengthValidator(3)], verbose_name='first_name')),
                ('last_name', models.CharField(max_length=75, validators=[django.core.validators.MinLengthValidator(3)], verbose_name='last_name')),
                ('date_of_birth', models.DateField(validators=[accounts.models.MinAgeValidator(18)])),
                ('date_of_creation', models.DateField(default=datetime.datetime.today)),
                ('last_active', models.DateTimeField(default=django.utils.timezone.now)),
                ('gender', models.CharField(max_length=25)),
                ('introduction', models.TextField(blank=True, null=True)),
                ('looking_for', models.TextField(blank=True, null=True)),
                ('interests', models.CharField(blank=True, max_length=100, null=True)),
                ('city', models.CharField(blank=True, max_length=40, null=True)),
                ('country', models.CharField(blank=True, max_length=40, null=True)),
                ('main_photo', models.URLField(default='https://static-media-prod-cdn.itsre-sumo.mozilla.net/static/sumo/img/default-FFA-avatar.png', max_length=1000)),
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
                ('image', models.URLField(max_length=1000)),
                ('public_id', models.CharField(max_length=100, unique=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
