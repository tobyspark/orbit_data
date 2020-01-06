from django.contrib import admin
from django.http import HttpResponse
import json

from .models import LabelledMedia, Participant, Survey

admin.site.register(LabelledMedia)

admin.site.register(Participant)

class SurveyAdmin(admin.ModelAdmin):
    
    actions = ['export']
    
    def export(self, request, queryset):
        data = { item.participant.id: item.decrypt() for item in queryset }
        return HttpResponse(
            json.dumps(data),
            content_type="application/json",
            )

admin.site.register(Survey, SurveyAdmin)