from rest_framework import serializers

from .models import LabelledMedia

class LabelledMediaSerializer(serializers.HyperlinkedModelSerializer):
        
    class Meta:
        model = LabelledMedia
        fields = ['label', 'media']
