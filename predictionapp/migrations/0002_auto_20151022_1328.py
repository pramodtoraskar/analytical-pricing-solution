# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('predictionapp', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='OilDescSourceKeyMapping',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sheet_name', models.CharField(max_length=100)),
                ('column_number', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='SourceKey',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('source_key', models.CharField(max_length=200)),
            ],
        ),
        migrations.AddField(
            model_name='oiltype',
            name='sheet_name',
            field=models.CharField(default=1, max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='oildescsourcekeymapping',
            name='oil_desc',
            field=models.ForeignKey(to='predictionapp.OilType'),
        ),
        migrations.AddField(
            model_name='oildescsourcekeymapping',
            name='source_key',
            field=models.ForeignKey(to='predictionapp.SourceKey'),
        ),
    ]
