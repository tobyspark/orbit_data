from django.urls import include, path
from rest_framework import routers
from push_notifications.api.rest_framework import APNSDeviceAuthorizedViewSet

from . import views

router = routers.DefaultRouter()
router.register(r'thing', views.ThingViewSet)
router.register(r'video', views.VideoViewSet)

urlpatterns = [
    path('survey/done', views.survey_done, name='survey_done'),
    path('survey/<token>', views.survey, name='survey'),
    path('api/', include(router.urls)),
    path('api/participant/', views.ParticipantView.as_view()),
    path('api/createparticipant/', views.ParticipantCreateView.as_view()),
    path('participant_export/', views.participant_export, name='participant_export'),
    path('device/apns/', APNSDeviceAuthorizedViewSet.as_view({'post': 'create'}), name='create_apns_device'),
]