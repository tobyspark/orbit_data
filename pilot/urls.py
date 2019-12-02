from django.urls import path

from . import views

urlpatterns = [
    path('', views.info, name='info'),
    path('consent', views.consent, name='consent'),
    path('survey/done', views.survey_done, name='survey_done'),
    path('survey/<token>', views.survey, name='survey'),
]