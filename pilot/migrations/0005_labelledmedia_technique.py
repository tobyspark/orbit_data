# Generated by Django 2.2.6 on 2020-02-05 15:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pilot', '0004_labelledmedia_participant'),
    ]

    operations = [
        migrations.AddField(
            model_name='labelledmedia',
            name='technique',
            field=models.CharField(choices=[('N', 'No technique'), ('R', 'Rotate'), ('Z', 'Zoom')], default='N', max_length=1),
        ),
    ]
