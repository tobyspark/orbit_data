from django import forms
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.utils.html import format_html

class VideoPreviewWidget(forms.widgets.FileInput):
    '''
    Use as a FileInput widget replacement. Just shows video.
    '''
    def render(self, name, value, attrs=None, **kwargs):
        video_aspect = 100 # height as a percent of width, e.g. 16:9 would be 56
        video_preview_html = format_html(
            '<video controls src="{}" style="width: 100%; height: 100%" />',
            reverse('admin_video', kwargs={'filename': value.name})
            )
        return f'{video_preview_html}'


GENDER_CHOICES = [
    ('M', 'Male'),
    ('F', 'Female'),
    ('O', 'WIDGET2_REPLACE'),
    ]

class GenderWidget(forms.MultiWidget):
    template_name = 'django/forms/widgets/gender.html'

    def __init__(self, attrs=None):
        widgets = (
            forms.RadioSelect(
                choices=GENDER_CHOICES,
                attrs={
                    'required': True,
                    },
                ),
            forms.TextInput(
                attrs={
                    'placeholder': 'Or, how do you identify?',
                    'required': False
                    },
                ),
        )
        super().__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            if value in ['M', 'F']:
                return [value, '']
            return ['', value]
        return ['', '']

class GenderField(forms.MultiValueField):
    CHAR_LENGTH=128
    
    def __init__(self, **kwargs):
        super().__init__(
            widget=GenderWidget,
            fields=(
                forms.ChoiceField(
                    required=True,
                    label='',
                    choices=GENDER_CHOICES,
                    ),
                forms.CharField(
                    required=False,
                    label='',
                    min_length=1,
                    max_length=GenderField.CHAR_LENGTH,
                    ),
                ),
            require_all_fields=False,
            required=False,
            **kwargs)

    def compress(self, data_list):
        if data_list:
            if data_list[0] in ['M', 'F'] and data_list[1] is '':
                return data_list[0]
            if data_list[0] == 'O' and len(data_list[1]) > 0:
                return data_list[1]
        raise ValidationError('Too short. Either choose M/F or be more descriptive.')