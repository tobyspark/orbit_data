from django import template
from django.urls import reverse

from phasetwo.models import Video

register = template.Library()

@register.inclusion_tag('admin/phasetwo/video/submit_line.html', takes_context=True)
def video_submit_row(context):
    """
    Displays the row of buttons for delete and save.
    """
    opts = context['opts']
    change = context['change']
    is_popup = context['is_popup']
    save_as = context['save_as']

    ctx = {
        'opts': opts,
        'show_delete_link': (
            not is_popup and context['has_delete_permission'] and
            change and context.get('show_delete', True)
        ),
        'show_save_as_new': not is_popup and change and save_as,
        'show_save_and_add_another': (
            context['has_add_permission'] and not is_popup and
            (not save_as or context['add'])
        ),
        'show_save_and_continue': not is_popup and context['has_change_permission'],
        'show_save': False,
        'is_popup': is_popup,
        'preserved_filters': context.get('preserved_filters'),
    }
    if context.get('original') is not None:
        ctx['original'] = context['original']
        pk = context['original'].pk
        if Video.objects.filter(pk=pk-1).exists(): 
            ctx['prev_url'] = reverse('admin:phasetwo_video_change', args=[pk-1])
        if Video.objects.filter(pk=pk+1).exists():
            ctx['next_url'] = reverse('admin:phasetwo_video_change', args=[pk+1])
    return ctx