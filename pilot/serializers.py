from rest_framework import serializers

from .models import LabelledMedia

class LabelledMediaSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    timestamp = serializers.ReadOnlyField()
    label = serializers.CharField(source='label_original')
        
    class Meta:
        model = LabelledMedia
        fields = ['id', 'timestamp', 'label', 'media']
