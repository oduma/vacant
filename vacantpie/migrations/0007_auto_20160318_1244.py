# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-03-18 12:44
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vacantpie', '0006_auto_20160318_0843'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='employee_day',
            unique_together=set([('employee', 'day_Type', 'day')]),
        ),
    ]
