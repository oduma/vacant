# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-03-30 07:49
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vacantpie', '0008_auto_20160318_1955'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee_event',
            name='approved',
            field=models.BooleanField(default=False),
            preserve_default=False,
        ),
    ]
