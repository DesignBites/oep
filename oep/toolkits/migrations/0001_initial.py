# Generated by Django 3.1.2 on 2020-11-16 08:39

from django.db import migrations, models
import django.db.models.deletion
import wagtail.core.blocks
import wagtail.core.fields
import wagtail.documents.blocks
import wagtail.images.blocks


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('wagtailcore', '0059_apply_collection_ordering'),
        ('wagtailimages', '0022_uploadedimage'),
    ]

    operations = [
        migrations.CreateModel(
            name='ToolkitsPage',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='wagtailcore.page')),
                ('header', wagtail.core.fields.RichTextField(max_length=500)),
                ('text', wagtail.core.fields.RichTextField()),
                ('photo', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailimages.image', verbose_name='Background photo')),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),
        migrations.CreateModel(
            name='ToolkitPage',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='wagtailcore.page')),
                ('heading', wagtail.core.fields.RichTextField(max_length=500)),
                ('description', wagtail.core.fields.RichTextField()),
                ('tools', wagtail.core.fields.StreamField([('tool', wagtail.core.blocks.StructBlock([('title', wagtail.core.blocks.CharBlock()), ('thumbnail', wagtail.images.blocks.ImageChooserBlock(required=False)), ('description', wagtail.core.blocks.RichTextBlock(required=False)), ('url', wagtail.documents.blocks.DocumentChooserBlock(required=False))])), ('doc', wagtail.core.blocks.StructBlock([('title', wagtail.core.blocks.CharBlock()), ('description', wagtail.core.blocks.RichTextBlock(required=False)), ('file', wagtail.documents.blocks.DocumentChooserBlock(required=False))]))])),
                ('cover_photo', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailimages.image')),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),
    ]
