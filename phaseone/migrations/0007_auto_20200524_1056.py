# Generated by Django 2.2.6 on 2020-05-24 10:56

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('phaseone', '0006_auto_20200524_0913'),
    ]

    operations = [
        migrations.AddField(
            model_name='participant',
            name='study_end',
            field=models.DateField(blank=True, default=datetime.date(2020, 6, 30), null=True),
        ),
        migrations.AddField(
            model_name='participant',
            name='study_start',
            field=models.DateField(blank=True, default=datetime.date(2020, 5, 4), null=True),
        ),
    ]
