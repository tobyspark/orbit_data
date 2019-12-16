from django import forms
from django.core.exceptions import ValidationError

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
                    max_length=128,
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