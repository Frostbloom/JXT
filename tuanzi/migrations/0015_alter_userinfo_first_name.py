# Generated by Django 3.2.13 on 2022-05-22 06:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tuanzi', '0014_auto_20220519_1639'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userinfo',
            name='first_name',
            field=models.CharField(blank=True, max_length=150, verbose_name='first name'),
        ),
    ]