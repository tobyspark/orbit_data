from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.db import IntegrityError
from django.utils.timezone import now
from django.contrib.auth.models import User
from rest_framework import viewsets

from .forms import SurveyForm
from .models import Participant, Survey, Thing, Video
from .serializers import ThingSerializer, VideoSerializer

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
        return HttpResponseRedirect(reverse('info'))
    
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
    
class ThingViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Things to be viewed or edited
    """
    queryset = Thing.objects.all().order_by('-created')
    serializer_class = ThingSerializer
    
    def perform_create(self, serializer):
        participant = Participant.objects.get(id=self.request.user.username)
        serializer.save(participant=participant)

class VideoViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Videos to be viewed or edited
    """
    queryset = Video.objects.all().order_by('-created')
    serializer_class = VideoSerializer
