# Generated by Django 2.2.6 on 2020-08-27 17:41

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import phasetwo.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CollectionPeriod',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=20, unique=True)),
                ('start', models.DateField()),
                ('end', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='Participant',
            fields=[
                ('enc_aes_key', models.BinaryField(max_length=16)),
                ('aes_nonce', models.BinaryField(max_length=16)),
                ('aes_mac_tag', models.BinaryField(max_length=16)),
                ('aes_ciphertext', models.BinaryField()),
                ('id', models.IntegerField(default=phasetwo.models.mint_id, primary_key=True, serialize=False)),
                ('in_study', models.BooleanField(default=True)),
                ('survey_started', models.DateTimeField(blank=True, null=True)),
                ('survey_token', models.CharField(default=phasetwo.models.mint_token, max_length=32, unique=True)),
                ('collection_period', models.ForeignKey(default=phasetwo.models.default_collection_period_pk, on_delete=django.db.models.deletion.SET_DEFAULT, to='phasetwo.CollectionPeriod')),
                ('user', models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='phasetwo_participant', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Thing',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label_participant', models.CharField(max_length=50)),
                ('label_validated', models.CharField(max_length=50)),
                ('created', models.DateField(auto_now_add=True)),
                ('participant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='phasetwo.Participant')),
            ],
        ),
        migrations.CreateModel(
            name='Video',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to=phasetwo.models.random_filename)),
                ('technique', models.CharField(choices=[('T', 'Train'), ('Z', 'Test: Zoom'), ('P', 'Test: Pan')], default='N', max_length=1)),
                ('validation', models.CharField(choices=[('-', 'Unvalidated'), ('P', 'Reject: video shows PII'), ('I', 'Reject: video inappropriate'), ('M', 'Reject: video does not feature object'), ('C', 'Video is clean')], default='-', max_length=1)),
                ('in_time', models.DecimalField(blank=True, decimal_places=2, max_digits=4, null=True)),
                ('out_time', models.DecimalField(blank=True, decimal_places=2, max_digits=4, null=True)),
                ('created', models.DateField(auto_now_add=True)),
                ('thing', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='phasetwo.Thing')),
            ],
        ),
        migrations.CreateModel(
            name='Survey',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('enc_aes_key', models.BinaryField(max_length=16)),
                ('aes_nonce', models.BinaryField(max_length=16)),
                ('aes_mac_tag', models.BinaryField(max_length=16)),
                ('aes_ciphertext', models.BinaryField()),
                ('participant', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='phasetwo.Participant')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CollectionPeriodDefault',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('period', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='phasetwo.CollectionPeriod')),
            ],
        ),
    ]
