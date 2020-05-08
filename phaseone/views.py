from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound
from django.urls import reverse
from django.db import IntegrityError
from django.utils.timezone import now
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.decorators import permission_required
from rest_framework import viewsets
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import BasePermission
from ranged_fileresponse import RangedFileResponse
from secrets import token_hex
from base64 import b64encode
import os

from .admin import ParticipantAdmin
from .forms import SurveyForm, DecryptForm
from .models import Participant, Survey, Thing, Video
from .serializers import ParticipantCreateSerializer, ThingSerializer, VideoSerializer

def survey(request, token):
    """
    The background survey page.
    Given a valid token, presents form, creates survey data and redirects to survey done.
    """
    # Check the URL corresponds to a participant
    try:
        participant = Participant.objects.get(survey_token=token)
    except Participant.DoesNotExist:
        # TODO: Log that a survey page with invalid token was hit.
        # TODO: Message the user that token was invalid.
        return HttpResponseNotFound()
    
    # Check the participant is still to complete the survey
    if participant.survey_done:
        # TODO: Log that a survey page previously completed was hit.
        # TODO: Message the user that they have already completed the survey.
        return HttpResponseRedirect(reverse('survey_done'))
    
    # Update the participant's survey started timestamp, enabling e.g. day later reminders.
    # TODO: Machinery for e.g. day later reminders
    participant.survey_started = now()
    participant.save()
    
    if request.method == 'POST':
        form = SurveyForm(request.POST)
        if form.is_valid():
            Survey.objects.create_survey(
                participant=participant,
                pii_fields=form.cleaned_data,
                )
            return HttpResponseRedirect(reverse('survey_done'))
    else:
        form = SurveyForm()
    
    return render(request, 'phaseone/survey.html', {'form': form})

def survey_done(request):
    """
    The survey done page.
    Static, no further navigation.
    """
    return render(request, 'phaseone/survey_done.html')

@permission_required('phaseone.view_video')
def video(request, filename):
    """
    Returns the video file. To be used by VideoPreviewWidget in admin's modelform. Requires permission decorator!
    """
    videopath = os.path.join(settings.MEDIA_ROOT, filename)
    
    if not os.path.exists(videopath):
        return HttpResponseNotFound()

    return RangedFileResponse(request, open(videopath, 'rb'), content_type='video/mp4')

@permission_required('phaseone.view_participant')
def participant_export(request):
    '''
    Return a CSV file of all participant data suitable for import into Excel.
    This is a clone of the admin function, modified so that the decryption key can be supplied by the user.
    Original plan was to have server backup, which could be run with decryption key loaded.
    This is not that plan, but it will work for the team. Policy: check https and access within City network.
    '''
    form = DecryptForm
    if request.method == 'POST':
        form = DecryptForm(request.POST)
        if form.is_valid():
            try:
                pem_key = f"-----BEGIN RSA PRIVATE KEY-----\r\n{ form.cleaned_data['thing'] }\r\n-----END RSA PRIVATE KEY-----"
                pa = ParticipantAdmin(Video, None)
                return pa.export_csv(request, Participant.objects.all(), pem_key)
            except:
                form.add_error(None, 'There was a problem decrypting the data.')
    return render(request, 'admin/phaseone/participant_export.html', {
        'form': form,
        'title': 'Participant Export',
        'site_title': 'ORBIT Data',
        'site_header': 'ORBIT Data'
        })

class CanCreateUserPermission(BasePermission):
    """
    Will permit if request's user has the add user permission.
    e.g. in admin pages, add this to the OrbitCamera user.
    """
    def has_permission(self, request, view):
        return request.user.has_perm('auth.add_user')

class ParticipantCreateView(CreateAPIView):
    """
    API endpoint to create a new user+participant
    Requires user add permission 
    """
    serializer_class = ParticipantCreateSerializer
    permission_classes = [CanCreateUserPermission]

    def perform_create(self, serializer):
        # Create random username and password
        username = token_hex(16)
        password = token_hex(16)
        user = User.objects.create_user(username, password=password)

        # Create participant
        pii_email = serializer.validated_data['email']
        pii_name = serializer.validated_data['name']
        max_tries = 10
        for i in range(0, max_tries):
            try:
                Participant.objects.create_participant(user, pii_email, pii_name)
                break
            except IntegrityError as error:
                # ID or token exists. Unlikely, but possible. Try again, generating new values.
                if i < max_tries - 1:
                    continue
                # We've tried enough times. Something is up.
                else:
                    print(
                        f"Can not create new participant. "
                        "Tried minting {max_tries} random IDs (and survey tokens), and hit an existing ID or token each time. "
                        "Something is either broken, or the number pool the IDs are drawn from needs to be an order of magnitude bigger. "
                        "Or you've been fantastically unlucky, and the client will try again and all should be fine.",
                        flush=True
                        ) # This should be an error log message
                    raise IntegrityError(error)

        # Create the auth credential to return as API response
        token_bytes = f'{username}:{password}'.encode()
        serializer.validated_data['auth_credential'] = 'Basic ' + b64encode(token_bytes).decode()

class ThingViewSet(viewsets.ModelViewSet):
    """
    API endpoint to view or edit the logged-in participant's Things
    """
    serializer_class = ThingSerializer
    queryset = Thing.objects.none()

    def get_queryset(self):
        user = self.request.user
        return Thing.objects.filter(participant__user=user).order_by('-created')

    def perform_create(self, serializer):
        participant = Participant.objects.get(user=self.request.user)
        serializer.save(participant=participant)

class VideoViewSet(viewsets.ModelViewSet):
    """
    API endpoint to view or edit the logged-in participant's Videos
    """
    serializer_class = VideoSerializer
    queryset = Video.objects.none()

    def get_queryset(self):
        user = self.request.user
        return Video.objects.filter(thing__participant__user=user).order_by('-created')

    def perform_create(self, serializer):
        serializer.save()
        # iOS background uploads that compplete when the app is not running do not receive the response body.
        # But they do receive the headers. Setting the record ID as a header becomes a fall-back to stop a loop of the upload succeeding but the iOS app not being able to know the ID. And so failing it. And so reuploading.
        # This is particularly pernicious, as it's likely the biggest uploads that will complete without the iOS app running.
        # https://forums.developer.apple.com/thread/84413
        self.headers.update({"orbit-id": serializer.data['id']})
