# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auth_test', '0002_auto_20150723_0920'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='authtestpermission',
            options={'verbose_name': 'auth_test_perms'},
        ),
    ]
