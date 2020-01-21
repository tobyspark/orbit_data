from django.contrib import admin
from django.http import HttpResponse
from django.shortcuts import render
import json
import csv

from .models import LabelledMedia, Participant, Survey
from .forms import ConsentForm, SurveyForm

def headers_from_form(form_class, first_headers):
    '''
    Extract headers from form, ensuring order starts with first_headers, adding headers if necessary
    '''
    headers = list(form_class.base_fields.keys())
    for header in reversed(first_headers):
        try:
            headers.remove(header)
        except:
            pass # first_headers can contain headers to add
        headers.insert(0, header)
    return headers

admin.site.register(LabelledMedia)

class ParticipantAdmin(admin.ModelAdmin):
    '''
    Provides export actions needed by research team. PII will be included if decryption keys loaded.
    '''
    actions = ['export_json', 'export_csv', 'export_html']
    
    def datum(self, item):
        return {
            'id': item.id,
            **item.decrypt(),
            **{x: True for x in ConsentForm.base_fields.keys() if x.startswith('consent')},
            'publishing_videos': item.publishing_videos,
            'publishing_recordings': item.publishing_recordings,
            'publishing_quotes': item.publishing_quotes,
            }
    
    def export_json(self, request, queryset):
        '''
        Return a JSON response with participant info
        '''
        return HttpResponse(
            json.dumps({d.pop('id'): d for d in (self.datum(item) for item in queryset)}),
            content_type="application/json",
            )
            
    def export_csv(self, request, queryset):
        '''
        Return a CSV file of participant(s) data suitable for import into Excel
        '''
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="orbit_participant.csv"'
        
        headers = headers_from_form(ConsentForm, first_headers=['id', 'name', 'email'])
        
        writer = csv.writer(response)
        writer.writerow(headers)
        for item in queryset:
            datum = self.datum(item)
            writer.writerow([datum[x] for x in headers])
    
        return response
        
    def export_html(self, request, queryset):
        '''
        Return the consent page filled in with participant's data
        Caveat: this will only return the first selected participant
        '''
        item = queryset[0] # Function will only be called with a queryset of at least one item
        datum = self.datum(item)

        req_consents = {x: True for x in ConsentForm.base_fields.keys() if x.startswith('consent')}
        
        form = ConsentForm({**datum, **req_consents})
        form.is_valid()
        return render(request, 'pilot/consent.html', {'form': form})

admin.site.register(Participant, ParticipantAdmin)

class SurveyAdmin(admin.ModelAdmin):
    '''
    Provides export actions needed by research team. PII will be included if decryption keys loaded.
    '''
    actions = ['export_json', 'export_csv', 'export_html']
    
    def datum(self, item):
        return {
            'id': item.id,
            **item.decrypt(),
               }
    
    def export_json(self, request, queryset):
        '''
        Return a JSON response with participant info
        '''
        return HttpResponse(
            json.dumps({d.pop('id'): d for d in (self.datum(item) for item in queryset)}),
            content_type="application/json",
            )
    
    def export_csv(self, request, queryset):
        '''
        Return a CSV file of participant(s) data suitabled for import into Excel
        '''
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="orbit_survey.csv"'
        
        headers = headers_from_form(SurveyForm, first_headers=['id'])
        
        writer = csv.writer(response)
        writer.writerow(headers)
        for item in queryset:
            datum = self.datum(item)
            writer.writerow([datum[x] for x in headers])
    
        return response
        
    def export_html(self, request, queryset):
        '''
        Return the survey page filled in with participant's data
        Caveat: this will only return the first selected participant
        '''
        form = SurveyForm(self.datum(queryset[0]))
        form.is_valid() # FIXME: Fails on gender!?
        return render(request, 'pilot/survey.html', {'form': form})

admin.site.register(Survey, SurveyAdmin)