from rest_framework import serializers

from .models import LabelledMedia

class LabelledMediaSerializer(serializers.HyperlinkedModelSerializer):
    participant = serializers.PrimaryKeyRelatedField(read_only=True)
    
    class Meta:
        model = LabelledMedia
        fields = ['label', 'media', 'participant']
