# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-04-02 09:55
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vacantpie', '0014_auto_20160401_0803'),
    ]

    operations = [
        migrations.AddField(
            model_name='day_type',
            name='marker',
            field=models.CharField(default='#00ff00', max_length=8),
            preserve_default=False,
        ),
    ]
