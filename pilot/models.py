from django.db import models

import secrets

TOKEN_BYTES = 16

class Participant(models.Model):
    id = models.IntegerField(primary_key=True)
    email = models.EmailField()
    name = models.CharField(max_length=128)
    survey_done = models.BooleanField(default=False)
    survey_token = models.CharField(
        default=secrets.token_urlsafe(TOKEN_BYTES),
        max_length=TOKEN_BYTES * 2, # average base64 encoding = 1.3x
        )

class LabelledMedia(models.Model):
    label = models.CharField(max_length=50)
    media = models.FileField()
    timestamp = models.DateField(auto_now_add=True)
