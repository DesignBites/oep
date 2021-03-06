# Generated by Django 3.1.2 on 2020-11-20 06:05

from django.db import migrations, models
import django.db.models.deletion
import wagtail.core.fields


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailimages', '0022_uploadedimage'),
        ('toolkits', '0007_auto_20201120_0559'),
    ]

    operations = [
        migrations.AddField(
            model_name='toolkitpage',
            name='excerpt',
            field=wagtail.core.fields.RichTextField(help_text='This text will appear on the toolkits index page.', null=True),
        ),
        migrations.AddField(
            model_name='toolkitpage',
            name='image',
            field=models.ForeignKey(help_text='This image will appear on the toolkits index page.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailimages.image'),
        ),
        migrations.AlterField(
            model_name='toolkitpage',
            name='background_image',
            field=models.ForeignKey(help_text="This is the background image of the toolkit's detail page.", null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailimages.image'),
        ),
    ]
