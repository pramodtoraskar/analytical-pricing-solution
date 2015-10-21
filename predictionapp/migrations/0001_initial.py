# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='OilType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('oil_type', models.CharField(max_length=100)),
                ('of_series', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='SeedData',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('doc_file', models.FileField(upload_to=b'seed_data/%Y/%m/%d')),
            ],
        ),
    ]
