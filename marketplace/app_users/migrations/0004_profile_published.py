# Generated by Django 3.2.13 on 2022-08-25 19:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_users', '0003_auto_20220820_0955'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='published',
            field=models.BooleanField(default=True, verbose_name='опубликовать'),
        ),
    ]
