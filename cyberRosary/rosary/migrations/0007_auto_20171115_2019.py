# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-11-15 19:19
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rosary', '0006_auto_20171115_1958'),
    ]

    operations = [
        migrations.CreateModel(
            name='Rosa',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.AddField(
            model_name='person',
            name='rosa',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='rosary.Rosa'),
        ),
    ]
