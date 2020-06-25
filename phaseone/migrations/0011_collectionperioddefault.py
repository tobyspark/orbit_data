# Generated by Django 2.2.6 on 2020-06-24 22:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('phaseone', '0010_auto_20200624_1643'),
    ]

    operations = [
        migrations.CreateModel(
            name='CollectionPeriodDefault',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('period', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='phaseone.CollectionPeriod')),
            ],
        ),
    ]