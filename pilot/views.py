from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse

from .forms import ConsentForm, SurveyForm

def info(request):
    return render(request, 'pilot/participant_info.html')

def consent(request):
    if request.method == 'POST':
        form = ConsentForm(request.POST)
        if form.is_valid():
            # TODO: act on cleaned_data
            return HttpResponseRedirect(reverse('survey', kwargs={'token': 'TODO'}))
    else:
        form = ConsentForm()
    
    return render(request, 'pilot/survey.html', {'form': form})

def survey(request, token):
    if request.method == 'POST':
        form = SurveyForm(request.POST)
        if form.is_valid():
            # TODO: act on cleaned_data
            return HttpResponseRedirect(reverse('survey_done'))
    else:
        form = SurveyForm()
    
    return render(request, 'pilot/survey.html', {'form': form})

def survey_done(request):
    return render(request, 'pilot/survey_done.html')