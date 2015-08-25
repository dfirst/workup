# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_of_birth', models.DateField(help_text='\u0434\u0434/\u043c\u043c/\u0433\u0433\u0433\u0433', null=True, verbose_name='\u0414\u0430\u0442\u0430 \u0440\u043e\u0436\u0434\u0435\u043d\u0438\u044f', blank=True)),
                ('bio', models.TextField(null=True, verbose_name='\u041e \u0441\u0435\u0431\u0435', blank=True)),
                ('avatar', models.ImageField(default='avatar/default-avatar.jpg', upload_to='avatar', max_length=255, verbose_name='\u0410\u0432\u0430\u0442\u0430\u0440')),
                ('karma', models.IntegerField(default=0, verbose_name='\u041a\u0430\u0440\u043c\u0430', editable=False)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
