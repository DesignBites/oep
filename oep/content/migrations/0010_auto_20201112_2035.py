# Generated by Django 3.1.2 on 2020-11-12 20:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0009_pagesection_link'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='page',
            name='slug',
        ),
        migrations.AddField(
            model_name='page',
            name='name',
            field=models.SlugField(default='x', unique=True),
            preserve_default=False,
        ),
    ]
