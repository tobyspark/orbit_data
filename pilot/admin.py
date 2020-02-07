from django.contrib import admin
from django.http import HttpResponse
from django.shortcuts import render
from django.conf import settings
import json
import csv
import datetime
import os
import secrets
import string
import subprocess
import tempfile

from .models import LabelledMedia, Participant, Survey
from .forms import ConsentForm, SurveyForm

FFMPEG_PATH = '/usr/local/bin/ffmpeg' # FIXME: Platform/machine specific
ZIP_PATH = '/usr/bin/zip' # FIXME: Platform/machine specific

admin.site.site_header = "ORBIT Data"
admin.site.site_title = "ORBIT Data"

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

class LabelledMediaAdmin(admin.ModelAdmin):
    '''
    Provides export actions needed by research team.
    '''
    actions = ['export_zip']
    list_display = (
        'label',
        'technique',
        'validation',
        'participant',
        )
    
    def export_zip(self, request, queryset):
        '''
        Return a zip file of anonymised videos with catalogue file
        '''
        archive_name = f"orbit_ml_dataset_export_{ datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S') }"
        
        # TODO: Only export verified media objects
        
        # # Create password for exported zip
        # with open('/usr/share/dict/words') as f:
        #     words = [word.strip() for word in f]
        #     password = '-'.join(secrets.choice(words) for i in range(4))
        
        # Create a temporary directory, to then zip up as export file
        with tempfile.TemporaryDirectory() as tmpdir:
            index_data = {}
            
            os.mkdir(os.path.join(tmpdir, archive_name))
            
            # Process media objects
            for item in queryset:
                # Export videos into temporary directory
                anon_name = f"{ ''.join(secrets.choice(string.ascii_lowercase) for _ in range(10)) }.mp4"
                result = subprocess.run([
                    FFMPEG_PATH,
                    '-i', item.media.path,
                    '-vcodec', 'copy',
                    '-an',
                    os.path.join(tmpdir, archive_name, anon_name)
                    ])
                if result.returncode != 0:
                    # Handle export failure
                    print('FFmpeg failure on { item }')
                    continue
                
                # Add to index
                (
                    index_data
                    .setdefault(item.participant.id, {})
                    .setdefault(item.label, {})
                    .setdefault(item.get_technique_display(), [])
                    .append(anon_name)
                )
                
            # Create index file
            with open(os.path.join(tmpdir, archive_name, 'orbit_pilot_dataset.json'), mode='xt') as index_file:
                json.dump(index_data, index_file)
            
            # Zip this directory up
            # GAH#1: Can't supply encryption password without being on tty
            # GAH#2: Win10 afaik can't extract any decently encrypted, portable folder archive
            export_zip_path = os.path.join(settings.MEDIA_ROOT, f'{ archive_name }.zip')
            result = subprocess.run(
                [
                    ZIP_PATH,
                    '-r',
                    '--compression-method', 'store', # no point in trying to compress mp4 files
                    export_zip_path,
                    archive_name,
                ],
                cwd=tmpdir
            )
            
            self.message_user(request, f"{ 'Successfully' if result.returncode == 0 else 'Unsuccessfully' } exported zip to { export_zip_path }")

admin.site.register(LabelledMedia, LabelledMediaAdmin)

class ParticipantAdmin(admin.ModelAdmin):
    '''
    Provides export actions needed by research team. PII will be included if decryption keys loaded.
    '''
    actions = ['export_json', 'export_csv', 'export_html']
    list_display = ('id', 'survey_description')
    
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
    export_json.short_description = "Export JSON"
            
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
    export_csv.short_description = "Export CSV"
        
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
    export_html.short_description = 'Show consent page'

admin.site.register(Participant, ParticipantAdmin)

class SurveyAdmin(admin.ModelAdmin):
    '''
    Provides export actions needed by research team. PII will be included if decryption keys loaded.
    '''
    actions = ['export_json', 'export_csv', 'export_html']
    
    def datum(self, item):
        return {
            'id': item.participant.id,
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
    export_json.short_description = "Export JSON"
    
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
    export_csv.short_description = "Export CSV"
        
    def export_html(self, request, queryset):
        '''
        Return the survey page filled in with participant's data
        Caveat: this will only return the first selected participant
        '''
        form = SurveyForm(self.datum(queryset[0]))
        form.is_valid() # FIXME: Fails on gender!?
        return render(request, 'pilot/survey.html', {'form': form})
    export_html.short_description = 'Show survey page'

admin.site.register(Survey, SurveyAdmin)