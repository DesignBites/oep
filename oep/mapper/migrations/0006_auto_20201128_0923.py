# Generated by Django 3.1.2 on 2020-11-28 09:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mapper', '0005_auto_20201128_0922'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pageinfo',
            name='page',
            field=models.CharField(db_index=True, max_length=20, verbose_name='Page number or name'),
        ),
    ]