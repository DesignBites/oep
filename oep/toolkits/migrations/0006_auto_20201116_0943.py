# Generated by Django 3.1.2 on 2020-11-16 09:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('toolkits', '0005_auto_20201116_0937'),
    ]

    operations = [
        migrations.RenameField(
            model_name='toolkitpage',
            old_name='heading',
            new_name='header',
        ),
        migrations.RenameField(
            model_name='toolkitpage',
            old_name='description',
            new_name='text',
        ),
    ]
