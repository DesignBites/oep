# Generated by Django 3.1.2 on 2020-11-20 05:59

from django.db import migrations
import wagtail.core.fields


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0022_auto_20201119_1602'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blogpostpage',
            name='excerpt',
            field=wagtail.core.fields.RichTextField(blank=True, help_text='Please aim for approximately 200 characters.'),
        ),
    ]