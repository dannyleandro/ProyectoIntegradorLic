# Generated by Django 3.0.3 on 2020-03-27 05:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('negociospush', '0004_auto_20200327_0044'),
    ]

    operations = [
        migrations.AlterField(
            model_name='process',
            name='Amount',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=20),
        ),
    ]
