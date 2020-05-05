from django.contrib import admin, messages
from django.http import HttpResponse, FileResponse
from django.shortcuts import render
from django.conf import settings
from django.urls import path, reverse
from django.db.models import Count
from django.contrib.humanize.templatetags.humanize import naturaltime
import json
import csv
import datetime
import os
import secrets
import string
import subprocess
import tempfile

from .models import Thing, Video, Participant, Survey
from .forms import SurveyForm

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
        'label_participant',
        'label_validated',
        'participant',
        'video_breakdown',
        'video_count',
        'created',
        )
    list_filter = (
        'created',
        )

@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    '''
    Provides export actions needed by research team.
    '''
    actions = ['export_csv', 'export_zip']

    def thing_label(self, obj):
        return obj.thing.label

    def thing_participant(self, obj):
        return obj.thing.participant

    def thing_video_breakdown(self, obj):
        return obj.thing.video_breakdown

    list_display = (
        'id',
        'thing_participant',
        'thing_label',
        'thing_video_breakdown',
        'technique',
        'validation',
        'created',
        )
    list_filter = (
        'technique',
        'validation',
        'created',
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
    actions = ['export_json', 'export_csv']
    list_display = ('id', 'things', 'videos', 'last_upload', 'survey_description')
    
    def things(self, obj):
        '''
        Count of their things, to display in column
        '''
        return Thing.objects.filter(participant=obj).count()

    def videos(self, obj):
        '''
        Count of their videos, to display in column
        '''
        return Video.objects.filter(thing__participant=obj).count()

    def last_upload(self, obj):
        '''
        Date of their last video upload, to display in column
        '''
        try:
            latest =  Video.objects.filter(thing__participant=obj).order_by('-created')[0]
        except IndexError:
            return "-"
        return latest.created


    def survey_description(self, obj):
        survey_status = 'Survey complete'
        if not obj.survey_done:
            if obj.survey_started is None:
                survey_status = f"Not started. https://orbit-data.city.ac.uk{ reverse('survey', kwargs={ 'token': obj.survey_token} ) }"
            else:
                survey_status = f"Started { naturaltime(obj.survey_started) }"
        return survey_status

    def datum(self, item):
        '''
        Dict of participant data, decrypting PII in Participant and Survey objects. Used for export.
        '''
        try:
            survey_pii = item.survey.decrypt()
        except Survey.DoesNotExist:
            survey_pii = {}

        return {
            'id': item.id,
            **item.decrypt(),
            **survey_pii,
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
        
        participant_headers = ['id', 'name', 'email']
        survey_headers = headers_from_form(SurveyForm, first_headers=['id'])

        headers = participant_headers + survey_headers[1:]

        writer = csv.writer(response)
        writer.writerow(headers)
        for item in queryset:
            datum = self.datum(item)
            writer.writerow([datum.get(x, '-') for x in headers])
    
        return response
    export_csv.short_description = "Export CSV"
