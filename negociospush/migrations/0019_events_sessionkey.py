# Generated by Django 3.0.3 on 2020-05-12 04:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('negociospush', '0018_events_eventtypes'),
    ]

    operations = [
        migrations.AddField(
            model_name='events',
            name='SessionKey',
            field=models.TextField(null=True),
        ),
    ]