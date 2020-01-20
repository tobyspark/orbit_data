from django.contrib import admin
from django.http import HttpResponse
import json

from .models import LabelledMedia, Participant, Survey

admin.site.register(LabelledMedia)

class ParticipantAdmin(admin.ModelAdmin):
    '''
    Provides an export action that will decrypt the participant name and email address and return as JSON
    '''
    actions = ['export_json']
    
    def data(self, queryset):
        return {
            item.id: {
                **item.decrypt(),
                'publishing_videos': item.publishing_videos,
                'publishing_recordings': item.publishing_recordings,
                'publishing_quotes': item.publishing_quotes,
                } for item in queryset
            }
    
    def export_json(self, request, queryset):
        return HttpResponse(
            json.dumps(self.data(queryset)),
            content_type="application/json",
            )

admin.site.register(Participant, ParticipantAdmin)

class SurveyAdmin(admin.ModelAdmin):
    '''
    Provides an export action that will decrypt the survey data and return as JSON
    '''
    actions = ['export_json']
    
    def data(self, queryset):
        return { item.participant.id: item.decrypt() for item in queryset }
    
    def export_json(self, request, queryset):
        return HttpResponse(
            json.dumps(self.data(queryset)),
            content_type="application/json",
            )

admin.site.register(Survey, SurveyAdmin)