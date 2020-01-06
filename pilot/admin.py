from django.contrib import admin
from django.http import HttpResponse
import json

from .models import LabelledMedia, Participant, Survey

admin.site.register(LabelledMedia)

class ParticipantAdmin(admin.ModelAdmin):
    '''
    Provides an export action that will decrypt the participant name and email address and return as JSON
    '''
    actions = ['export']
 
    def export(self, request, queryset):
        data = { item.id: item.decrypt() for item in queryset }
        return HttpResponse(
            json.dumps(data),
            content_type="application/json",
            )

admin.site.register(Participant, ParticipantAdmin)

class SurveyAdmin(admin.ModelAdmin):
    '''
    Provides an export action that will decrypt the survey data and return as JSON
    '''
    actions = ['export']
    
    def export(self, request, queryset):
        data = { item.participant.id: item.decrypt() for item in queryset }
        return HttpResponse(
            json.dumps(data),
            content_type="application/json",
            )

admin.site.register(Survey, SurveyAdmin)