from django.urls import include, path
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r'thing', views.ThingViewSet)
router.register(r'video', views.VideoViewSet)

urlpatterns = [
    path('', views.info, name='info'),
    path('consent', views.consent, name='consent'),
    path('survey/done', views.survey_done, name='survey_done'),
    path('survey/<token>', views.survey, name='survey'),
    path('api/', include(router.urls))
]