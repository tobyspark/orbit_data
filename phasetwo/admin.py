from django.contrib import admin, messages
from django.http import HttpResponse, HttpResponseRedirect, StreamingHttpResponse
from django.shortcuts import render
from django.conf import settings
from django.urls import path, reverse
from django.db.models import Count, FileField
from django.db.utils import OperationalError
from django.utils.text import slugify
from django.contrib.humanize.templatetags.humanize import naturaltime
from push_notifications.models import APNSDevice
import json
import csv
import datetime
import os
import tempfile
import zipstream

from .models import Thing, Video, Participant, Survey, CollectionPeriod, CollectionPeriodDefault, default_collection_period_pk
from .forms import SurveyForm
from orbit.fields import VideoPreviewWidget

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
    No export, see videos, but still a useful view onto the data
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
        'participant__in_study',
        'created',
        )

@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    '''
    Provides export actions needed by research team.
    '''
    # CHANGE VIEW ------

    formfield_overrides = {
        FileField: {'widget': VideoPreviewWidget}
    }


    # LIST VIEW DISPLAY ------

    def thing_label(self, obj):
        return obj.thing.label
    thing_label.admin_order_field = 'thing__label_participant'

    def thing_participant(self, obj):
        return obj.thing.participant
    thing_participant.admin_order_field = 'thing__participant'

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
        'thing__participant__in_study',
        'technique',
        'validation',
        'created',
        )


    ### LIST VIEW ACTIONS

    def get_urls(self):
        '''
        Used by the 'Export ZIP (All archived)' button
        See templates/admin/phasepne/video/change_list_object_tools.html
        '''
        urls = super().get_urls()
        my_urls = [
            path('export-zip/', self.admin_site.admin_view(self.export_zip))
        ]
        return my_urls + urls

    actions = ['export_csv', 'export_zip']

    def export_csv(self, request, queryset):
        '''
        Return a CSV file of Videos info suitable for import into Excel
        '''
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="orbit_labelledmedia.csv"'

        headers = [
            'Participant', 
            'Label', 
            'Technique', 
            'Validation', 
            'Created',
            ]

        writer = csv.writer(response)
        writer.writerow(headers)
        for item in queryset:
            writer.writerow([
                item.thing.participant.id, 
                item.thing.label, 
                item.get_technique_display(),
                item.get_validation_display(),
                item.created,
                ])
        return response
    export_csv.short_description = "Export CSV"

    def export_zip(self, request, queryset=Video.objects.filter(validation='C', thing__participant__in_study=True)):
        '''
        Return a zip file of videos with catalogue file
        '''
        archive_name = f"orbit_ml_dataset_export_{ datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S') }"

        errors = []
        index_data = {}

        export_zip = zipstream.ZipFile(allowZip64=True)
        # Process media objects
        for item in queryset:
            filename = f"{ item.thing.participant }--{ slugify(item.thing.label) }--{ item.technique }--{ os.path.basename(item.file.path) }.mp4"

            # Add to zip
            export_zip.write(
                item.file.path, 
                arcname=filename
            )

            # Add to index
            (
                index_data
                .setdefault(item.thing.participant.id, {})
                .setdefault(item.thing.label, {})
                .setdefault(item.get_technique_display(), [])
                .append(filename)
            )

        # Add index, as json
        export_zip.writestr(
            'orbit_phase_one_dataset.json',
            json.dumps(index_data).encode(),
            )

        # Return the zip as a streaming download
        response = StreamingHttpResponse(export_zip, content_type='application/zip')
        response['Content-Disposition'] = f'attachment; filename={archive_name}.zip'
        return response
    export_zip.short_description = "Export ZIP"


@admin.register(CollectionPeriod)
class CollectionPeriodAdmin(admin.ModelAdmin):
    list_display = ('name_with_default', 'start', 'end')    
    actions = ['set_as_default']

    def name_with_default(self, obj):
        if obj.pk == default_collection_period_pk():
            if obj.name:
                return f'{obj.name} (default)'
            return 'Default'
        return obj.name

    def set_as_default(self, request, queryset):
        if queryset.count() != 1:
            self.message_user(request, 'Please select only one collection period', level=messages.WARNING)
            return
        CollectionPeriodDefault.objects.filter(pk=1).update(period=queryset.first().pk)
        self.message_user(request, f"Default set to '{ queryset.first().name }'")
    set_as_default.short_description = 'Make selected period default for new Participants'


def create_participantadmin_action(period):
    def action_func(modeladmin, request, queryset):
        rows_updated = queryset.update(collection_period=period)
        modeladmin.message_user(request, f"{ rows_updated } {'participant was' if rows_updated == 1 else 'participants were'} updated to '{ period }'")
    action_func.__name__ = f'collection_period_action_{ period.pk }'
    action_func.short_description = f"Change selected participants collection period to '{ period }'"
    return action_func

@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    '''
    Provides export actions needed by research team. PII will be included if decryption keys loaded.
    '''
    export_action_name = 'export_csv_view' if settings.PII_KEY_PRIVATE is None else 'export_csv'
    try:
        actions = [export_action_name, 'send_notification'] + [create_participantadmin_action(x) for x in CollectionPeriod.objects.all()]
    except OperationalError:
        pass # DB call will block `makemigrations` if table not yet present
    list_display = ('id', 'collection_period', 'things', 'videos', 'consent', 'push','last_upload', 'survey_description',)
    list_filter = ('in_study', 'collection_period')
    readonly_fields = ('id', 'survey_started', )

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

    def consent(self, obj):
        return obj.user.date_joined.date()
    consent.admin_order_field = 'user__date_joined'

    def last_upload(self, obj):
        '''
        Date of their last video upload, to display in column
        '''
        try:
            latest =  Video.objects.filter(thing__participant=obj).order_by('-created')[0]
        except IndexError:
            return "-"
        return latest.created

    def push(self, obj):
        return '✓' if APNSDevice.objects.filter(user__phasetwo_participant=obj).exists() else ''

    def survey_description(self, obj):
        survey_status = 'Survey complete'
        if not obj.survey_done:
            if obj.survey_started is None:
                survey_status = f"Not started. https://example.com{ reverse('survey', kwargs={ 'token': obj.survey_token} ) }"
            else:
                survey_status = f"Started { naturaltime(obj.survey_started) }"
        return survey_status

    def datum(self, item, key):
        '''
        Dict of participant data, decrypting PII in Participant and Survey objects. Used for export.
        '''
        try:
            survey_pii = item.survey.decrypt(private_key_pem=key)
        except Survey.DoesNotExist:
            survey_pii = {}

        return {
            'id': item.id,
            'charity_choice': item.charity_choice,
            **item.decrypt(private_key_pem=key),
            **survey_pii,
            }
            
    def export_csv(self, request, queryset, key=settings.PII_KEY_PRIVATE):
        '''
        Return a CSV file of participant(s) data suitable for import into Excel
        '''
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="orbit_participant.csv"'
        
        participant_headers = ['id', 'name', 'email', 'charity_choice']
        survey_headers = headers_from_form(SurveyForm, first_headers=['id'])

        headers = participant_headers + survey_headers[1:]

        writer = csv.writer(response)
        writer.writerow(headers)
        for item in queryset:
            datum = self.datum(item, key)
            writer.writerow([datum.get(x, '-') for x in headers])
    
        return response
    export_csv.short_description = "Export CSV (PII decryption key is loaded into server)"

    def export_csv_view(self, request, queryset):
        return HttpResponseRedirect(reverse('participant_export'))
    export_csv_view.short_description = "Export CSV (PII decryption key must be supplied)"

    def send_notification(self, request, queryset):
        selected = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)
        return HttpResponseRedirect(reverse('participant_send_notification', kwargs={"id_list": ",".join(selected)}))        
