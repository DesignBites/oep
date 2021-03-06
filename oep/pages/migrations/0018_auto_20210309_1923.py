# Generated by Django 3.1.2 on 2021-03-09 19:23

from django.db import migrations
import wagtail.core.blocks
import wagtail.core.fields
import wagtail.images.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0017_auto_20210309_1909'),
    ]

    operations = [
        migrations.AlterField(
            model_name='homepage',
            name='sections',
            field=wagtail.core.fields.StreamField([('section', wagtail.core.blocks.StructBlock([('heading', wagtail.core.blocks.RichTextBlock(form_classname='full')), ('heading_fi', wagtail.core.blocks.RichTextBlock(form_classname='full', required=False)), ('text', wagtail.core.blocks.RichTextBlock(label='Text (English)')), ('text_fi', wagtail.core.blocks.RichTextBlock(label='Text (Finnish)', required=False)), ('image', wagtail.images.blocks.ImageChooserBlock()), ('link', wagtail.core.blocks.PageChooserBlock()), ('link_text', wagtail.core.blocks.CharBlock(label='Link text (English)', required=False)), ('link_text_fi', wagtail.core.blocks.CharBlock(label='Link text (Finnish)', required=False))]))], blank=True),
        ),
    ]
