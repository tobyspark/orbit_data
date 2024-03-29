# Generated by Django 2.2.6 on 2020-02-07 15:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('pilot', '0006_labelledmedia_validation'),
    ]

    operations = [
        migrations.CreateModel(
            name='Label',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(max_length=50)),
                ('validated', models.BooleanField(default=False)),
            ],
        ),
        migrations.RenameField(
            model_name='labelledmedia',
            old_name='label',
            new_name='label_original',
        ),
        migrations.AddField(
            model_name='labelledmedia',
            name='label_validated',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='pilot.Label'),
        ),
    ]
