# Generated by Django 3.0.3 on 2020-03-09 15:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('negociospush', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='profile',
            old_name='city',
            new_name='City',
        ),
        migrations.RenameField(
            model_name='profile',
            old_name='description',
            new_name='Description',
        ),
        migrations.RenameField(
            model_name='profile',
            old_name='productCode',
            new_name='ProductCode',
        ),
        migrations.RenameField(
            model_name='profile',
            old_name='state',
            new_name='State',
        ),
        migrations.RenameField(
            model_name='profile',
            old_name='user',
            new_name='User',
        ),
    ]
