# Generated by Django 3.1.2 on 2020-11-19 16:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailimages', '0022_uploadedimage'),
        ('blog', '0021_defaultthumbnail'),
    ]

    operations = [
        migrations.AlterField(
            model_name='defaultthumbnail',
            name='image',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailimages.image'),
        ),
    ]
