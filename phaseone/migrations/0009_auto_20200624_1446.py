# Generated by Django 2.2.6 on 2020-06-24 14:46

from django.db import migrations, models
import django.db.models.deletion
import phaseone.models


class Migration(migrations.Migration):

    dependencies = [
        ('phaseone', '0008_auto_20200524_1116'),
    ]

    operations = [
        migrations.CreateModel(
            name='CollectionPeriod',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20, unique=True)),
                ('start', models.DateField()),
                ('end', models.DateField()),
            ],
        ),
        migrations.RemoveField(
            model_name='participant',
            name='study_end',
        ),
        migrations.RemoveField(
            model_name='participant',
            name='study_start',
        ),
        migrations.AddField(
            model_name='participant',
            name='collection_period',
            field=models.ForeignKey(default=phaseone.models.default_collection_period_pk, on_delete=django.db.models.deletion.SET_DEFAULT, to='phaseone.CollectionPeriod'),
        ),
    ]
