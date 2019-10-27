from django.db import models

class LabelledMedia(models.Model):
    label = models.CharField(max_length=50)
    media = models.FileField()
    timestamp = models.DateField(auto_now_add=True)
