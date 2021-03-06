# Generated by Django 3.1.2 on 2020-11-15 11:09

from django.db import migrations
import wagtail.core.blocks
import wagtail.core.fields
import wagtail.images.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0016_auto_20201115_0915'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blogpostpage',
            name='body',
            field=wagtail.core.fields.StreamField([('heading', wagtail.core.blocks.RichTextBlock()), ('paragraph', wagtail.core.blocks.RichTextBlock()), ('image', wagtail.images.blocks.ImageChooserBlock()), ('quote', wagtail.core.blocks.BlockQuoteBlock()), ('columns', wagtail.core.blocks.StreamBlock([('column_1_1', wagtail.core.blocks.StructBlock([('column_0', wagtail.core.blocks.StreamBlock([('heading', wagtail.core.blocks.CharBlock(form_classname='full title', group='Common')), ('paragraph', wagtail.core.blocks.RichTextBlock(group='Common')), ('image', wagtail.images.blocks.ImageChooserBlock(group='Common'))])), ('column_1', wagtail.core.blocks.StreamBlock([('heading', wagtail.core.blocks.CharBlock(form_classname='full title', group='Common')), ('paragraph', wagtail.core.blocks.RichTextBlock(group='Common')), ('image', wagtail.images.blocks.ImageChooserBlock(group='Common'))]))], group='Columns', template='blocks/columns.html')), ('column_2_1', wagtail.core.blocks.StructBlock([('column_0', wagtail.core.blocks.StreamBlock([('heading', wagtail.core.blocks.CharBlock(form_classname='full title', group='Common')), ('paragraph', wagtail.core.blocks.RichTextBlock(group='Common')), ('image', wagtail.images.blocks.ImageChooserBlock(group='Common'))])), ('column_1', wagtail.core.blocks.StreamBlock([('heading', wagtail.core.blocks.CharBlock(form_classname='full title', group='Common')), ('paragraph', wagtail.core.blocks.RichTextBlock(group='Common')), ('image', wagtail.images.blocks.ImageChooserBlock(group='Common'))]))], group='Columns', template='blocks/columns.html')), ('column_1_2', wagtail.core.blocks.StructBlock([('column_0', wagtail.core.blocks.StreamBlock([('heading', wagtail.core.blocks.CharBlock(form_classname='full title', group='Common')), ('paragraph', wagtail.core.blocks.RichTextBlock(group='Common')), ('image', wagtail.images.blocks.ImageChooserBlock(group='Common'))])), ('column_1', wagtail.core.blocks.StreamBlock([('heading', wagtail.core.blocks.CharBlock(form_classname='full title', group='Common')), ('paragraph', wagtail.core.blocks.RichTextBlock(group='Common')), ('image', wagtail.images.blocks.ImageChooserBlock(group='Common'))]))], group='Columns', template='blocks/columns.html')), ('column_1_1_1', wagtail.core.blocks.StructBlock([('column_0', wagtail.core.blocks.StreamBlock([('heading', wagtail.core.blocks.CharBlock(form_classname='full title', group='Common')), ('paragraph', wagtail.core.blocks.RichTextBlock(group='Common')), ('image', wagtail.images.blocks.ImageChooserBlock(group='Common'))])), ('column_1', wagtail.core.blocks.StreamBlock([('heading', wagtail.core.blocks.CharBlock(form_classname='full title', group='Common')), ('paragraph', wagtail.core.blocks.RichTextBlock(group='Common')), ('image', wagtail.images.blocks.ImageChooserBlock(group='Common'))])), ('column_2', wagtail.core.blocks.StreamBlock([('heading', wagtail.core.blocks.CharBlock(form_classname='full title', group='Common')), ('paragraph', wagtail.core.blocks.RichTextBlock(group='Common')), ('image', wagtail.images.blocks.ImageChooserBlock(group='Common'))]))], group='Columns', template='blocks/columns.html'))], form_classname='full'))]),
        ),
    ]
