# Generated by Django 3.1.2 on 2020-11-28 09:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mapper', '0004_auto_20201128_0921'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='pageinfo',
            options={'ordering': ('page',)},
        ),
        migrations.RenameField(
            model_name='pageinfo',
            old_name='page_no',
            new_name='page',
        ),
    ]
