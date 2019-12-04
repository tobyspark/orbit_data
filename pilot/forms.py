from django import forms
from django.core.exceptions import ValidationError
from form_utils.forms import BetterForm

def validate_age(value):
    if value < 20: raise ValidationError('Age too young')
    if value > 100: raise ValidationError('Age too old')
    if value % 5 != 0: raise ValidationError('Age not rounded to nearest five-years')

class ConsentForm(BetterForm):
    class Meta:
        fieldsets = [
            ('Email Address', {
                'fields': [
                    'email',
                    ]}),
            ('Consent', {
                'fields': [
                    'consent1',
                    'consent2',
                    'consent3',
                    'consent4',
                    'consent5',
                    'consent6',
                    'consent7',
                    ]}),
            ('Publishing', {
                'fields': [
                    'publishing1',
                    'publishing2',
                    ]}),
            ('Signed', {
                'fields': [
                    'name',
                    ]}),
            ]
                                   
    email = forms.EmailField(
        label='',
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter your email address',
            }),
        )
    consent1 = forms.BooleanField(
        label='I confirm that I have read and understood the participant information dated [INSERT DATE AND VERSION NUMBER] for the above study. I have had the opportunity to consider the information and ask questions which have been answered satisfactorily.'
        )
    consent2 = forms.BooleanField(
        label='During the home visit, I agree to my conversation with the researcher being video recorded.'
        )
    consent3 = forms.BooleanField(
        label='During the home visit, I agree to being video recorded while taking videos of the things I select.'
        )
    consent4 = forms.BooleanField(
        label='I agree to share the videos I took during the home visit with the researcher.'
        )
    consent5 = forms.BooleanField(
        label='I understand that my participation is voluntary and that I am free to withdraw without giving a reason without being penalised or disadvantaged.'
        )
    consent6 = forms.BooleanField(
        label='I agree to City recording and processing this information about me. I understand that this information will be used only for the purposes explained in the participant information and my consent is conditional on City complying with its duties and obligations under the General Data Protection Regulation (GDPR).'
        )
    consent7 = forms.BooleanField(
        label='I agree to take part in the above study, titled: “Pilot study for meta learning for personalised object recognition aimed at visually impaired people”.'
        )
    publishing1 = forms.BooleanField(
        label='The videos that the project takes of me along with the videos I share with the project can be used for subsequent publication.'
        )
    publishing2 = forms.BooleanField(
        label='Direct quotes from the audio recordings that the project takes of me can be used for subsequent publication.'
        )
    name = forms.CharField(
        label='',
        max_length=128,
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter your name',
            }),
    )

class SurveyForm(BetterForm):
    class Meta:
        fieldsets = [
            ('Age', {
                'fields': [
                    'age',
                    ]}),
            ('Gender', {
                'fields': [
                    'genderChoice',
                    'genderIdentify',
                    ]}),
            ('Vision', {
                'fields': [
                    'vision_light_perception',
                    'vision_full_fov',
                    'vision_reduced_fov',
                    'vision_1to3',
                    'vision_3to6',
                    'vision_6tox',
                    'vision_more',
                    ]}),
            ('Accessibility', {
                'description': 'Do you use any iOS accessibility features?',
                'fields': [
                    'accessibility_voiceover',
                    'accessibility_zoom',
                    'accessibility_magnifier',
                    'accessibility_displayaccomodations',
                    'accessibility_speech',
                    'accessibility_largetext',
                    'accessibility_boldtext',
                    'accessibility_buttonshapes',
                    'accessibility_reducetransparency',
                    'accessibility_increasecontrast',
                    'accessibility_reducemotion',
                    'accessibility_siri',
                    'accessibility_braille',
                    'accessibility_more',
                    ]}),
            ('Apps', {
                'description': 'Do you use any of these apps? We are interested in apps that help you ‘see’ your surroundings in some way.',
                'fields': [
                    'apps_taptapsee',
                    'apps_bemyeyes',
                    'apps_seeingai',
                    'apps_envision',
                    'apps_more',
                    ]}),
            ('Camera', {
                'description': 'Do you use the camera app on your iPhone?',
                'fields': [
                    'camera_usage',
                    'camera_photos',
                    'camera_videos',
                    ]}),
            ]
                
    age = forms.IntegerField(
        label='',
        validators=[validate_age],
        widget=forms.NumberInput(attrs={
            'step': '5',
            'min': '20',
            'max': '100',
            'placeholder': '20, 25, 30, ...',
            }),
        )
    genderChoice = forms.ChoiceField(
        label='',
        choices=[
            ('M', 'Male'),
            ('F', 'Female'),
            ('O', 'Other'),
            ],
        widget=forms.RadioSelect,
        )
    genderIdentify = forms.CharField(
        label='',
        min_length=1,
        max_length=128,
        widget=forms.TextInput(attrs={
            'placeholder': 'How do you identify?'
            }),
        )
    vision_light_perception = forms.ChoiceField(
        label='',
        choices=[
            ('Y', 'I have light perception'),
            ('N', 'I have no light perception'),
            ],
        widget=forms.RadioSelect,
        )
    vision_full_fov = forms.BooleanField(
        label='I have full field of vision (peripheral vision)'
        )
    vision_reduced_fov = forms.BooleanField(
        label='I have severely reduced field of vision (tunnel vision)'
        )
    vision_1to3 = forms.BooleanField(
        label='I can see objects between 1 and 3 meters away'
        )
    vision_3to6 = forms.BooleanField(
        label='I can see objects between 3 and 6 meters away'
        )
    vision_6tox = forms.BooleanField(
        label='I can see objects more than 6 meters away'
        )
    vision_more = forms.CharField(
        label='',
        widget=forms.TextInput(attrs={
            'placeholder': 'Anything else? e.g. how long have you been visually impaired?',
            }),
        )
    accessibility_voiceover = forms.BooleanField(
        label='VoiceOver'
        )
    accessibility_zoom = forms.BooleanField(
        label='Zoom'
        )
    accessibility_magnifier = forms.BooleanField(
        label='Magnifier'
        )
    accessibility_displayaccomodations = forms.BooleanField(
        label='Display Accommodations'
        )
    accessibility_speech = forms.BooleanField(
        label='Speech (Speak selection, Speak Screen)'
        )
    accessibility_largetext = forms.BooleanField(
        label='Larger text'
        )
    accessibility_boldtext = forms.BooleanField(
        label='Bold text'
    )
    accessibility_buttonshapes = forms.BooleanField(
        label='Button shapes'
        )
    accessibility_reducetransparency = forms.BooleanField(
        label="Reduce transparency"
        )
    accessibility_increasecontrast = forms.BooleanField(
        label="Increase contrast"
        )
    accessibility_reducemotion = forms.BooleanField(
        label="Reduce motion"
        )
    accessibility_siri = forms.BooleanField(
        label='Siri'
        )
    accessibility_braille = forms.BooleanField(
        label='Braille display & Braille commands'
        )
    accessibility_more = forms.CharField(
        label='',
        widget=forms.TextInput(attrs={
            'placeholder': 'List any others...',
            }),
        )
    apps_taptapsee = forms.BooleanField(
        label="TapTapSee"
        )
    apps_bemyeyes = forms.BooleanField(
        label="Be my eyes"
        )
    apps_seeingai = forms.BooleanField(
        label='Seeing AI'
        )
    apps_envision = forms.BooleanField(
        label='Envision'
        )
    apps_more = forms.CharField(
        label='',
        widget=forms.TextInput(attrs={
            'placeholder': 'List any others...',
            }),
        )
    camera_usage = forms.ChoiceField(
        label="",
        choices=[
            ('N', 'Never'),
            ('O', 'Occasional use'),
            ('M', 'Most days'),
            ],
        widget=forms.RadioSelect,
        )
    camera_photos = forms.BooleanField(
        label="I take photos"
        )
    camera_videos = forms.BooleanField(
        label="I take videos"
        )
