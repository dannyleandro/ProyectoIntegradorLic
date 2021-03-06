# Generated by Django 3.0.3 on 2020-04-12 19:58

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('negociospush', '0012_usercode'),
    ]

    operations = [
        migrations.CreateModel(
            name='NotificationProcesses',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('SystemLoadDate', models.DateTimeField(default=datetime.datetime.now)),
                ('process', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='negociospush.Process')),
            ],
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField()),
                ('read', models.BooleanField(default=False)),
                ('sent', models.BooleanField(default=False)),
                ('SystemLoadDate', models.DateTimeField(default=datetime.datetime.now)),
                ('process', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='negociospush.Process')),
                ('recipient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
