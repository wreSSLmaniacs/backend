# Generated by Django 3.1.4 on 2020-12-07 11:18

import compe.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('compe', '0005_auto_20201207_1104'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contest',
            name='input',
            field=models.FileField(blank=True, null=True, upload_to=compe.models.inuplocate),
        ),
        migrations.AlterField(
            model_name='contest',
            name='output',
            field=models.FileField(blank=True, null=True, upload_to=compe.models.outuplocate),
        ),
    ]
