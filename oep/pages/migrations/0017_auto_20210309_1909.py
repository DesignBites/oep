# Generated by Django 3.1.2 on 2021-03-09 19:09

from django.db import migrations
import wagtail.core.blocks
import wagtail.core.fields
import wagtail.images.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0016_auto_20210309_1857'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='homepage',
            name='language',
        ),
        migrations.AddField(
            model_name='homepage',
            name='header_fi',
            field=wagtail.core.fields.RichTextField(blank=True, max_length=500, null=True, verbose_name='Header (Finnish)'),
        ),
        migrations.AlterField(
            model_name='homepage',
            name='header',
            field=wagtail.core.fields.RichTextField(max_length=500, verbose_name='Header (English)'),
        ),
        migrations.AlterField(
            model_name='homepage',
            name='sections',
            field=wagtail.core.fields.StreamField([('section', wagtail.core.blocks.StructBlock([('heading', wagtail.core.blocks.RichTextBlock(form_classname='full')), ('text', wagtail.core.blocks.RichTextBlock(label='Text (English)')), ('text_fi', wagtail.core.blocks.RichTextBlock(label='Text (Finnish)', required=False)), ('image', wagtail.images.blocks.ImageChooserBlock()), ('link', wagtail.core.blocks.PageChooserBlock()), ('link_text', wagtail.core.blocks.CharBlock(label='Link text (English)', required=False)), ('link_text_fi', wagtail.core.blocks.CharBlock(label='Link text (Finnish)', required=False))]))], blank=True),
        ),
        migrations.AlterField(
            model_name='homepage',
            name='text',
            field=wagtail.core.fields.RichTextField(verbose_name='Text (English)'),
        ),
        migrations.AlterField(
            model_name='homepage',
            name='text_fi',
            field=wagtail.core.fields.RichTextField(blank=True, null=True, verbose_name='Text (Finnish)'),
        ),
    ]
