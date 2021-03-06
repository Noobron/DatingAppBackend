# Generated by Django 3.2.9 on 2021-12-30 06:58

from django.conf import settings
import django.contrib.postgres.fields.citext
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
from django.contrib.postgres.operations import CITextExtension


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        CITextExtension(),
        migrations.CreateModel(
            name='ChatMessage',
            fields=[
                ('id',
                 models.BigAutoField(auto_created=True,
                                     primary_key=True,
                                     serialize=False,
                                     verbose_name='ID')),
                ('message_type',
                 models.CharField(choices=[('text', 'Chat message type : Text')
                                           ],
                                  max_length=50)),
                ('created_at',
                 models.DateTimeField(default=django.utils.timezone.now)),
                ('seen', models.BooleanField(default=False)),
                ('content', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='ChatRoom',
            fields=[
                ('id',
                 models.BigAutoField(auto_created=True,
                                     primary_key=True,
                                     serialize=False,
                                     verbose_name='ID')),
                ('chat_room_name',
                 django.contrib.postgres.fields.citext.CICharField(
                     max_length=125, unique=True)),
                ('last_chat_message',
                 models.ForeignKey(null=True,
                                   on_delete=django.db.models.deletion.CASCADE,
                                   related_name='last_chat_message',
                                   to='chat.chatmessage')),
                ('user1',
                 models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                   related_name='user1',
                                   to=settings.AUTH_USER_MODEL)),
                ('user2',
                 models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                   related_name='user2',
                                   to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='chatmessage',
            name='chat_room',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='chat_room',
                to='chat.chatroom'),
        ),
        migrations.AddField(
            model_name='chatmessage',
            name='recipient',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='recipient',
                to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='chatmessage',
            name='sender',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='sender',
                to=settings.AUTH_USER_MODEL),
        ),
    ]
