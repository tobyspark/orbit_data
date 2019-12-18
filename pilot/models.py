from django.db import models
from datetime import datetime
import secrets

from orbit.fields import GenderField

TOKEN_BYTES = 16

class Participant(models.Model):
    id = models.IntegerField(
        primary_key=True,
        default=secrets.randbelow(10000),
        )
    email = models.EmailField(
        unique=True,
        )
    name = models.CharField(
        max_length=128,
        )
    survey_started = models.DateTimeField(
        null=True,
        )
    survey_token = models.CharField(
        default=secrets.token_urlsafe(TOKEN_BYTES),
        max_length=TOKEN_BYTES * 2, # average base64 encoding = 1.3x
        unique=True,
        )
    
    @property
    def survey_done(self):
        return Survey.objects.filter(participant=self).exists()

class Survey(models.Model):
    participant = models.ForeignKey(
        Participant,
        on_delete=models.CASCADE,
        )
    age = models.IntegerField()
    gender = models.CharField(max_length=GenderField.CHAR_LENGTH)
    vision_light_perception = models.CharField(max_length=1)
    vision_full_fov = models.BooleanField()
    vision_reduced_fov = models.BooleanField()
    vision_1to3 = models.BooleanField()
    vision_3to6 = models.BooleanField()
    vision_6tox = models.BooleanField()
    vision_more = models.TextField()
    accessibility_voiceover = models.BooleanField()
    accessibility_zoom = models.BooleanField()
    accessibility_magnifier = models.BooleanField()
    accessibility_displayaccomodations = models.BooleanField()
    accessibility_speech = models.BooleanField()
    accessibility_largetext = models.BooleanField()
    accessibility_boldtext = models.BooleanField()
    accessibility_buttonshapes = models.BooleanField()
    accessibility_reducetransparency = models.BooleanField()
    accessibility_increasecontrast = models.BooleanField()
    accessibility_reducemotion = models.BooleanField()
    accessibility_siri = models.BooleanField()
    accessibility_braille = models.BooleanField()
    accessibility_more = models.TextField()
    apps_taptapsee = models.BooleanField()
    apps_bemyeyes = models.BooleanField()
    apps_seeingai = models.BooleanField()
    apps_envision = models.BooleanField()
    apps_more = models.TextField()
    camera_usage = models.CharField(max_length=1)
    camera_photos = models.BooleanField()
    camera_videos = models.BooleanField()

class LabelledMedia(models.Model):
    label = models.CharField(max_length=50)
    media = models.FileField()
    timestamp = models.DateField(auto_now_add=True)
