# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-03-31 07:54
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vacantpie', '0009_employee_event_approved'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee_event',
            name='declined',
            field=models.BooleanField(default=False),
            preserve_default=False,
        ),
    ]
