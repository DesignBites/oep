# Generated by Django 3.1.2 on 2020-12-14 07:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mapper', '0008_auto_20201130_1750'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Purpose',
        ),
        migrations.AddField(
            model_name='map',
            name='location',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='The primary location of the organization'),
        ),
        migrations.AlterField(
            model_name='map',
            name='size',
            field=models.PositiveSmallIntegerField(choices=[(1, '< 20'), (2, '20 - 200'), (3, '> 200')], default=3, verbose_name='Size of the organization'),
        ),
    ]
