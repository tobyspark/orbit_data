# Generated by Django 2.2.6 on 2020-05-24 11:16

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('phaseone', '0007_auto_20200524_1056'),
    ]

    operations = [
        migrations.AlterField(
            model_name='participant',
            name='study_end',
            field=models.DateField(default=datetime.date(2020, 6, 30)),
        ),
        migrations.AlterField(
            model_name='participant',
            name='study_start',
            field=models.DateField(default=datetime.date(2020, 5, 4)),
        ),
    ]
