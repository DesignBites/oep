# Generated by Django 3.1.2 on 2021-04-14 07:28

from django.db import migrations
import wagtail.core.blocks
import wagtail.core.fields
import wagtail.documents.blocks
import wagtail.images.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('toolkits', '0012_auto_20210410_0936'),
    ]

    operations = [
        migrations.AlterField(
            model_name='toolkitpage',
            name='tools',
            field=wagtail.core.fields.StreamField([('tool', wagtail.core.blocks.StructBlock([('title', wagtail.core.blocks.CharBlock(label='Title (English)')), ('title_fi', wagtail.core.blocks.CharBlock(label='Title (Finnish)', required=False)), ('thumbnail', wagtail.images.blocks.ImageChooserBlock()), ('description', wagtail.core.blocks.RichTextBlock(label='Description (English)', required=False)), ('description_fi', wagtail.core.blocks.RichTextBlock(label='Description (Finnish)', required=False)), ('url', wagtail.core.blocks.URLBlock(label='Link (English)', required=False)), ('url_fi', wagtail.core.blocks.URLBlock(label='Link (Finnish)', required=False))])), ('doc', wagtail.core.blocks.StructBlock([('title', wagtail.core.blocks.CharBlock(label='Title (English)')), ('title_fi', wagtail.core.blocks.CharBlock(label='Title (Finnish)', required=False)), ('thumbnail', wagtail.images.blocks.ImageChooserBlock()), ('description', wagtail.core.blocks.RichTextBlock(label='Description (English)', required=False)), ('description_fi', wagtail.core.blocks.RichTextBlock(label='Description (Finnish)', required=False)), ('file', wagtail.documents.blocks.DocumentChooserBlock(label='File (English)', required=False)), ('file_fi', wagtail.documents.blocks.DocumentChooserBlock(label='File (Finnish)', required=False))]))]),
        ),
    ]
