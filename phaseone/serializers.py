from rest_framework import serializers

from .models import Thing, Video

class ThingSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    label_validated = serializers.ReadOnlyField()
        
    class Meta:
        model = Thing
        fields = ['id', 'label_participant', 'label_validated']

class VideoSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    validation = serializers.ReadOnlyField()
    
    class Meta:
        model = Video
        fields = ['id', 'thing', 'file', 'technique', 'validation']
