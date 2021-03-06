# Generated by Django 3.1.2 on 2021-03-09 20:09

from django.db import migrations
import wagtail.core.blocks
import wagtail.core.fields
import wagtail.documents.blocks
import wagtail.images.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('toolkits', '0009_auto_20201120_1228'),
    ]

    operations = [
        migrations.AddField(
            model_name='toolkitpage',
            name='excerpt_fi',
            field=wagtail.core.fields.RichTextField(help_text='This text will appear on the toolkits index page.', null=True, verbose_name='Excerpt (Finnish)'),
        ),
        migrations.AddField(
            model_name='toolkitpage',
            name='header_fi',
            field=wagtail.core.fields.RichTextField(blank=True, max_length=500, null=True, verbose_name='Header (Finnish)'),
        ),
        migrations.AddField(
            model_name='toolkitpage',
            name='text_fi',
            field=wagtail.core.fields.RichTextField(blank=True, null=True, verbose_name='Text (Finnish)'),
        ),
        migrations.AddField(
            model_name='toolkitspage',
            name='header_fi',
            field=wagtail.core.fields.RichTextField(blank=True, max_length=500, null=True, verbose_name='Header (Finnish)'),
        ),
        migrations.AddField(
            model_name='toolkitspage',
            name='text_fi',
            field=wagtail.core.fields.RichTextField(blank=True, null=True, verbose_name='Text (Finnish)'),
        ),
        migrations.AlterField(
            model_name='toolkitpage',
            name='excerpt',
            field=wagtail.core.fields.RichTextField(help_text='This text will appear on the toolkits index page.', null=True, verbose_name='Excerpt'),
        ),
        migrations.AlterField(
            model_name='toolkitpage',
            name='header',
            field=wagtail.core.fields.RichTextField(max_length=500, verbose_name='Header (English)'),
        ),
        migrations.AlterField(
            model_name='toolkitpage',
            name='text',
            field=wagtail.core.fields.RichTextField(verbose_name='Text (English)'),
        ),
        migrations.AlterField(
            model_name='toolkitpage',
            name='tools',
            field=wagtail.core.fields.StreamField([('tool', wagtail.core.blocks.StructBlock([('title', wagtail.core.blocks.CharBlock(label='Title (English)')), ('title_fi', wagtail.core.blocks.CharBlock(label='Title (English)', required=False)), ('thumbnail', wagtail.images.blocks.ImageChooserBlock()), ('description', wagtail.core.blocks.RichTextBlock(label='Description (English)', required=False)), ('description_fi', wagtail.core.blocks.RichTextBlock(label='Description (Finnish)', required=False)), ('url', wagtail.core.blocks.URLBlock(required=False))])), ('doc', wagtail.core.blocks.StructBlock([('title', wagtail.core.blocks.CharBlock(label='Title (English)')), ('title_fi', wagtail.core.blocks.CharBlock(label='Title (English)', required=False)), ('thumbnail', wagtail.images.blocks.ImageChooserBlock()), ('description', wagtail.core.blocks.RichTextBlock(label='Description (English)', required=False)), ('description_fi', wagtail.core.blocks.RichTextBlock(label='Description (Finnish)', required=False)), ('file', wagtail.documents.blocks.DocumentChooserBlock(required=False))]))]),
        ),
        migrations.AlterField(
            model_name='toolkitspage',
            name='header',
            field=wagtail.core.fields.RichTextField(max_length=500, verbose_name='Header (English)'),
        ),
        migrations.AlterField(
            model_name='toolkitspage',
            name='text',
            field=wagtail.core.fields.RichTextField(verbose_name='Text (English)'),
        ),
    ]
