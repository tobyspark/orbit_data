# Generated by Django 2.2.6 on 2020-10-06 14:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('phasetwo', '0002_video_sha256'),
    ]

    operations = [
        migrations.AlterField(
            model_name='video',
            name='technique',
            field=models.CharField(choices=[('T', 'Train'), ('Z', 'Test: Zoom'), ('P', 'Test: Pan'), ('S', 'Test')], default='N', max_length=1),
        ),
    ]
