from django.contrib import admin, messages
from django.http import HttpResponse, FileResponse
from django.shortcuts import render
from django.conf import settings
from django.urls import path
from django.db.models import Count
import json
import csv
import datetime
import os
import secrets
import string
import subprocess
import tempfile

from .models import Thing, Video, Participant, Survey
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

@admin.register(Thing)
class ThingAdmin(admin.ModelAdmin):
    '''
    ...will it do anything beyond ModelAdmin for the Thing model?
    '''
    list_display = (
        'label',
        'video_count',
        )


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    '''
    Provides export actions needed by research team.
    '''
    # actions = ['export_csv', 'export_zip', 'merge_labels']
    list_display = (
        'thing',
        'technique',
        'validation',
        )

# @admin.register(LabelledMedia)
# class LabelledMediaAdmin(admin.ModelAdmin):
#     '''
#     Provides export actions needed by research team.
#     '''
#     actions = ['export_csv', 'export_zip', 'merge_labels']
#     list_display = (
#         'label',
#         'technique',
#         'validation',
#         'participant',
#         )
#
#     def get_urls(self):
#         urls = super().get_urls()
#         my_urls = [
#             path('export-zip/', self.admin_site.admin_view(self.export_zip))
#         ]
#         return my_urls + urls
#
#     def export_csv(self, request, queryset):
#         '''
#         Return a CSV file of LabelledMedia info suitable for import into Excel
#         '''
#         response = HttpResponse(content_type='text/csv')
#         response['Content-Disposition'] = 'attachment; filename="orbit_labelledmedia.csv"'
#
#         headers = ['Participant', 'Label', 'Technique']
#
#         writer = csv.writer(response)
#         writer.writerow(headers)
#         for item in queryset:
#             writer.writerow([item.participant.id, item.label, item.get_technique_display()])
#         return response
#     export_csv.short_description = "Export CSV"
#
#     def export_zip(self, request, queryset=LabelledMedia.objects.filter(validation='C')):
#         '''
#         Return a zip file of anonymised videos with catalogue file
#         '''
#         archive_name = f"orbit_ml_dataset_export_{ datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S') }"
#
#         # Create a temporary directory, to hold export directory and zip of that directory
#         with tempfile.TemporaryDirectory() as tmpdir:
#             errors = []
#             index_data = {}
#
#             os.mkdir(os.path.join(tmpdir, archive_name))
#
#             # Process media objects
#             for item in queryset:
#                 # Export videos into temporary directory
#                 anon_name = f"{ ''.join(secrets.choice(string.ascii_lowercase) for _ in range(10)) }.mp4"
#                 command = [
#                     FFMPEG_PATH,
#                     '-loglevel', 'error',
#                     ]
#                 if item.in_time:
#                     # FFmpeg seeking information - must read
#                     # https://trac.ffmpeg.org/wiki/Seeking
#                     command += ['-ss', f'{item.in_time}']
#                 if item.out_time:
#                     command += ['-to', f'{item.out_time}']
#                 command += [
#                     '-i', item.media.path,
#                     '-vcodec', 'copy',
#                     '-an',
#                     ]
#                 command += [os.path.join(tmpdir, archive_name, anon_name)]
#                 result = subprocess.run(command)
#                 if result.returncode != 0:
#                     errors.append(f'FFmpeg failure on { item }')
#                     continue
#
#                 # Add to index
#                 (
#                     index_data
#                     .setdefault(item.participant.id, {})
#                     .setdefault(item.label, {})
#                     .setdefault(item.get_technique_display(), [])
#                     .append(anon_name)
#                 )
#
#             # Create index file
#             with open(os.path.join(tmpdir, archive_name, 'orbit_phase_one_dataset.json'), mode='xt') as index_file:
#                 json.dump(index_data, index_file)
#
#             # Zip this directory up
#             # GAH#1: Can't supply encryption password without being on tty
#             # GAH#2: Win10 afaik can't extract any decently encrypted, portable folder archive
#             export_zip_path = os.path.join(tmpdir, f'{ archive_name }.zip')
#             result = subprocess.run(
#                 [
#                     ZIP_PATH,
#                     '-r',
#                     '--compression-method', 'store', # no point in trying to compress mp4 files
#                     '--quiet',
#                     export_zip_path,
#                     archive_name, # relative path for zip sanity, enabled by setting cwd to tmpdir
#                 ],
#                 cwd=tmpdir
#             )
#             if result.returncode != 0:
#                 errors.append('Zip failure')
#
#             # Report any errors
#             if errors:
#                 self.message_user(request, '; '.join(errors), level=messages.WARNING) # This won't be displayed until page reload, natch
#                 # TODO: Logging
#
#             # Return the zip as a download
#             return FileResponse(
#                 open(export_zip_path, 'rb'),
#                 as_attachment=True,
#                 filename=f'{ archive_name }.zip',
#                 )
#     export_zip.short_description = "Export ZIP"
#
#     def merge_labels(self, request, queryset):
#         '''
#         Detect any LabelledMedia that have the same label and participant, and create a single Label for them
#         This may be no label_validated and identical label_original strings, or many label_validated objects with same labels.
#         '''
#         index_data = {}
#         for item in queryset:
#             (
#                 index_data
#                 .setdefault(item.participant.id, {})
#                 .setdefault(item.label, [])
#                 .append(item)
#             )
#         for participant_group in index_data.values():
#             for label_group in participant_group.values():
#                 # Get or create Label object
#                 message = f'P{ label_group[0].participant.id }: '
#                 label = label_group[0].label_validated
#                 if label is None:
#                     label = Label.objects.create(label=label_group[0].label_original)
#                     message += 'created '
#                 message += f"label '{ label.label }' ({ label.id }); "
#                 # Update all instances within this label group to have that label
#                 has_changed = False
#                 for item in label_group:
#                     if item.label_validated != label:
#                         if item.label_validated is not None:
#                             message += f'deleting duplicate label ({item.label_validated.id}); '
#                             item.label_validated.delete()
#                         message += 'assigning label; '
#                         item.label_validated = label
#                         item.save()
#                         has_changed = True
#                 if has_changed:
#                     self.message_user(request, message[:-2] + '.')
#         # Remove any zombie labels
#         del_info = Label.objects.annotate(count=Count('labelledmedia')).filter(count=0).delete()
#         self.message_user(request, f'Deleted { del_info[0] } labels not linked to any media')


@admin.register(Participant)
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
        return render(request, 'phaseone/consent.html', {'form': form})
    export_html.short_description = 'Show consent page'


@admin.register(Survey)
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
        return render(request, 'phaseone/survey.html', {'form': form})
    export_html.short_description = 'Show survey page'
