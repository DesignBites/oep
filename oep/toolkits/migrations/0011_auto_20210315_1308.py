# Generated by Django 3.1.2 on 2021-03-15 13:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('toolkits', '0010_auto_20210309_2009'),
    ]

    operations = [
        migrations.AddField(
            model_name='toolkitpage',
            name='title_fi',
            field=models.CharField(blank=True, max_length=200, null=True, verbose_name='Title (Finnish)'),
        ),
        migrations.AddField(
            model_name='toolkitspage',
            name='title_fi',
            field=models.CharField(blank=True, max_length=200, null=True, verbose_name='Title (Finnish)'),
        ),
    ]
