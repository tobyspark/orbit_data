from django import forms

class GenderWidget(forms.MultiWidget):
    def __init__(self, attrs={}):
        widgets = (
            forms.RadioSelect(
                choices=[
                    ('M', 'Male'),
                    ('F', 'Female'),
                    ],
                attrs=attrs,
                ),
            forms.TextInput(
                attrs=attrs.update({'placeholder': 'Or, how do you identify?'}),
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
        widget = GenderWidget()
        fields = (
            forms.ChoiceField(
                required=False,
                label='',
                choices=[
                    ('M', 'Male'),
                    ('F', 'Female'),
                    ],
                ),
            forms.CharField(
                required=False,
                label='',
                min_length=1,
                max_length=128,
                ),
        )
        super().__init__(widget=widget, fields=fields, required=False, **kwargs)

    def compress(self, data_list):
        if data_list:
            if data_list[0] in ['M', 'F'] and data_list[1] is '':
                return data_list[0]
            if data_list[0] == '' and len(data_list[1]) > 0:
                return data_list[1]
        return None