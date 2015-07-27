# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0001_initial'),
        ('auth_test', '0001_initial'),
    ]

    operations = [
        migrations.DeleteModel(
            name='AuthTestPerms',
        ),
        migrations.CreateModel(
            name='AuthTestPermission',
            fields=[
            ],
            options={
                'proxy': True,
                'verbose_name': 'auth_test_permissions',
            },
            bases=('auth.permission',),
        ),
    ]
