# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('kalabash_api', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='kalabashinstance',
            name='last_request',
            field=models.DateTimeField(default=django.utils.timezone.now, auto_now=True),
            preserve_default=True,
        ),
    ]
