from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.db import IntegrityError
from django.utils.timezone import now
from django.contrib.auth.models import User
from rest_framework import viewsets

from .forms import ConsentForm, SurveyForm
from .models import Participant, Survey, LabelledMedia
from .serializers import LabelledMediaSerializer

def info(request):
    """
    The participant information page.
    Static, links to consent page.
    """
    return render(request, 'pilot/participant_info.html')

def consent(request):
    """
    The consent page.
    Presents form, creates participant data and redirects to survey.
    """
    if request.method == 'POST':
        form = ConsentForm(request.POST)
        if form.is_valid():
            while True:
                try:
                    participant = Participant.objects.create_participant(
                        email=form.cleaned_data['email'],
                        name=form.cleaned_data['name'],
                    )
                    User.objects.create_user(f'{ participant.id }', password=f'FIXMEPOSTPILOT-uTbrm6jMP2UN6JdJSt1wqgM5rjkdLQwV9frdqsYeXhg')
                    return HttpResponseRedirect(reverse('survey', kwargs={'token': participant.survey_token}))
                except IntegrityError as error:
                    # ID or token exists. Try again, generating new values.
                    print(error)
                    pass
    else:
        form = ConsentForm()
    
    return render(request, 'pilot/consent.html', {'form': form})

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
                fields=form.cleaned_data,
                )
            return HttpResponseRedirect(reverse('survey_done'))
    else:
        form = SurveyForm()
    
    return render(request, 'pilot/survey.html', {'form': form})

def survey_done(request):
    """
    The survey done page.
    Static, no further navigation.
    """
    return render(request, 'pilot/survey_done.html')
    
class LabelledMediaViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows media to be viewed or edited
    """
    queryset = LabelledMedia.objects.all().order_by('-timestamp')
    serializer_class = LabelledMediaSerializer
