# Generated by Django 3.1.2 on 2020-11-10 06:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mapper', '0004_auto_20201109_1101'),
    ]

    operations = [
        migrations.AlterField(
            model_name='map',
            name='is_own',
            field=models.BooleanField(default=True, help_text="Uncheck the box if you are mapping another organization's network", verbose_name='This is my own organization'),
        ),
    ]
