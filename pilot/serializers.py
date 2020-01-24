from rest_framework import serializers

from .models import LabelledMedia

class LabelledMediaSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
        
    class Meta:
        model = LabelledMedia
        fields = ['id', 'label', 'media']
