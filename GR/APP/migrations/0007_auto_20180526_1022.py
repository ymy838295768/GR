# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-05-26 10:22
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('App', '0006_foodtype'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='foodtype',
            table='axf_foodtypes',
        ),
    ]
