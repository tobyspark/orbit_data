from rest_framework import serializers

from .models import LabelledMedia

class LabelledMediaSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    timestamp = serializers.ReadOnlyField()
        
    class Meta:
        model = LabelledMedia
        fields = ['id', 'timestamp', 'label', 'media']
