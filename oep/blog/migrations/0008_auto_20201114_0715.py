# Generated by Django 3.1.2 on 2020-11-14 07:15

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import modelcluster.contrib.taggit
import modelcluster.fields
import wagtail.core.blocks
import wagtail.core.fields
import wagtail.images.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailimages', '0022_uploadedimage'),
        ('wagtailforms', '0004_add_verbose_name_plural'),
        ('wagtailcore', '0059_apply_collection_ordering'),
        ('taggit', '0003_taggeditem_add_unique_index'),
        ('wagtailredirects', '0006_redirect_increase_max_length'),
        ('blog', '0007_auto_20201114_0648'),
    ]

    operations = [
        migrations.CreateModel(
            name='BlogPostPage',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='wagtailcore.page')),
                ('body', wagtail.core.fields.StreamField([('heading', wagtail.core.blocks.CharBlock()), ('paragraph', wagtail.core.blocks.RichTextBlock()), ('image', wagtail.images.blocks.ImageChooserBlock()), ('columns', wagtail.core.blocks.StreamBlock([('column_1_1', wagtail.core.blocks.StructBlock([('column_0', wagtail.core.blocks.StreamBlock([('heading', wagtail.core.blocks.CharBlock(form_classname='full title', group='Common')), ('paragraph', wagtail.core.blocks.RichTextBlock(group='Common')), ('image', wagtail.images.blocks.ImageChooserBlock(group='Common'))])), ('column_1', wagtail.core.blocks.StreamBlock([('heading', wagtail.core.blocks.CharBlock(form_classname='full title', group='Common')), ('paragraph', wagtail.core.blocks.RichTextBlock(group='Common')), ('image', wagtail.images.blocks.ImageChooserBlock(group='Common'))]))], group='Columns', template='blocks/columns.html')), ('column_2_1', wagtail.core.blocks.StructBlock([('column_0', wagtail.core.blocks.StreamBlock([('heading', wagtail.core.blocks.CharBlock(form_classname='full title', group='Common')), ('paragraph', wagtail.core.blocks.RichTextBlock(group='Common')), ('image', wagtail.images.blocks.ImageChooserBlock(group='Common'))])), ('column_1', wagtail.core.blocks.StreamBlock([('heading', wagtail.core.blocks.CharBlock(form_classname='full title', group='Common')), ('paragraph', wagtail.core.blocks.RichTextBlock(group='Common')), ('image', wagtail.images.blocks.ImageChooserBlock(group='Common'))]))], group='Columns', template='blocks/columns.html')), ('column_1_2', wagtail.core.blocks.StructBlock([('column_0', wagtail.core.blocks.StreamBlock([('heading', wagtail.core.blocks.CharBlock(form_classname='full title', group='Common')), ('paragraph', wagtail.core.blocks.RichTextBlock(group='Common')), ('image', wagtail.images.blocks.ImageChooserBlock(group='Common'))])), ('column_1', wagtail.core.blocks.StreamBlock([('heading', wagtail.core.blocks.CharBlock(form_classname='full title', group='Common')), ('paragraph', wagtail.core.blocks.RichTextBlock(group='Common')), ('image', wagtail.images.blocks.ImageChooserBlock(group='Common'))]))], group='Columns', template='blocks/columns.html')), ('column_1_1_1', wagtail.core.blocks.StructBlock([('column_0', wagtail.core.blocks.StreamBlock([('heading', wagtail.core.blocks.CharBlock(form_classname='full title', group='Common')), ('paragraph', wagtail.core.blocks.RichTextBlock(group='Common')), ('image', wagtail.images.blocks.ImageChooserBlock(group='Common'))])), ('column_1', wagtail.core.blocks.StreamBlock([('heading', wagtail.core.blocks.CharBlock(form_classname='full title', group='Common')), ('paragraph', wagtail.core.blocks.RichTextBlock(group='Common')), ('image', wagtail.images.blocks.ImageChooserBlock(group='Common'))])), ('column_2', wagtail.core.blocks.StreamBlock([('heading', wagtail.core.blocks.CharBlock(form_classname='full title', group='Common')), ('paragraph', wagtail.core.blocks.RichTextBlock(group='Common')), ('image', wagtail.images.blocks.ImageChooserBlock(group='Common'))]))], group='Columns', template='blocks/columns.html'))], form_classname='full'))])),
                ('date', models.DateField(default=django.utils.timezone.now, verbose_name='Post date')),
                ('category', modelcluster.fields.ParentalKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='blog.blogcategory')),
                ('tags', modelcluster.contrib.taggit.ClusterTaggableManager(blank=True, help_text='A comma-separated list of tags.', through='blog.BlogPageTag', to='taggit.Tag', verbose_name='Tags')),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),
        migrations.RemoveField(
            model_name='blogpage',
            name='body',
        ),
        migrations.RemoveField(
            model_name='blogpage',
            name='category',
        ),
        migrations.RemoveField(
            model_name='blogpage',
            name='date',
        ),
        migrations.RemoveField(
            model_name='blogpage',
            name='tags',
        ),
        migrations.AddField(
            model_name='blogpage',
            name='header',
            field=models.CharField(default='-', max_length=500),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='blogpage',
            name='photo',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailimages.image', verbose_name='Background photo'),
        ),
        migrations.AddField(
            model_name='blogpage',
            name='text',
            field=wagtail.core.fields.RichTextField(default='-'),
            preserve_default=False,
        ),
        migrations.DeleteModel(
            name='BlogIndexPage',
        ),
    ]
