# Generated by Django 3.2.13 on 2022-09-10 12:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app_goods', '0007_alter_category_category_icon'),
        ('app_shops', '0003_auto_20220819_1811'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='shopproduct',
            unique_together={('shop', 'product')},
        ),
    ]