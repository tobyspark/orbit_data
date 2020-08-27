from rest_framework import serializers

from .models import Thing, Video

class ParticipantCreateSerializer(serializers.Serializer):
    '''
    Accept name and email, to create a participant with
    Return auth credential, to access as that participant
    '''
    name = serializers.CharField(min_length=2, max_length=150, write_only=True)
    email = serializers.EmailField(write_only=True)
    auth_credential = serializers.CharField(read_only=True)

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
