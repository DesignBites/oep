# Generated by Django 3.1.2 on 2020-11-14 21:27

from django.db import migrations
import wagtail.core.fields


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0011_blogpostpage_excerpt'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blogpage',
            name='header',
            field=wagtail.core.fields.RichTextField(max_length=500),
        ),
    ]