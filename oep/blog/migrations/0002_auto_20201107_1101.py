# Generated by Django 3.1.2 on 2020-11-07 11:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='category',
            options={'ordering': ('order',), 'verbose_name_plural': 'categories'},
        ),
    ]
