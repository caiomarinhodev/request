# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2017-12-14 15:42
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0013_auto_20171214_1321'),
    ]

    operations = [
        migrations.AddField(
            model_name='estabelecimento',
            name='lat',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='estabelecimento',
            name='lng',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
