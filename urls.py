# -*- coding: utf-8 -*-
from django.conf.urls import url, include
from django.conf import settings, urls ## https://github.com/divio/aldryn-addons/blob/master/aldryn_addons/urls.py
from aldryn_django.utils import i18n_patterns
import aldryn_addons.urls
from crm.views import *
from django.conf.urls.static import static
#from django.urls import path
# from two_factor.urls import urlpatterns as tf_urls
from django.contrib.auth import views as auth_views
from django.views.generic.base import RedirectView
urlpatterns = [

    # add your own patterns here
    url(r'^$', start,name="start"),
    # url(r'"^$"', tf_urls),
    # url(r'"^$"', tf_urls,name="tf_urls"),
    url(r"^api/(?P<arg>\w{0,50})$", upload, name="upload"),
    url(r"^sandbox/(?P<arg>\w{0,50})$", sandbox, name="sandbox"),

    url(r"^anmeldungen/", include('crm.urls'), name="anmeldungen"),

    ## For displaying events per AJAX calls from external websites
    url(r"^extern/seminare", seminars_places_available, name="seminars_external"),
    url(r"^extern/events/past", public_events_past, name="events_external_past"),
    url(r"^extern/events/future", public_events_future, name="events_external_future"),
    url(r"^extern/events/all", public_events_all, name="events_external_present"),

    ## Send generic message (in development)
    url(r"^ajax/send_message/$", send_message,name="send_message"), 
    url(r"^nachricht_versenden/$", send_message_page,name="send_message_page"), 

    ## Function for sending invitations
    url(r"^ajax/einladungen_versenden/$", email_invitation_to_person,name="send_invitations"), 
    url(r"^ajax/get_people/$", get_people,name="get_people"),

    ## Serve file with name file_name
    url(r'^data/(?P<file_name>[-\w.]+)/$', dataView),

    url(r'^jsongravity/(?P<veranstaltung_id>\d+)/', jsonGravity,name="jsonGravity"),

    ## Duplicate recognition
    url(r"^duplikate$", duplicates, name="duplicates"),
    url(r"^duplikate_zusammenführen$", merge_duplicates, name="merge_duplicates"),

    url(r"^logout/$", auth_views.logout_then_login,
    name="logout"),

    url(r"^anmelden/(?P<event_id>\d+)/$", register,
    name="register"),

    url(r"^templates/(?P<model_name>\w{0,50})/(?P<object_id>\d+)/$",
    linked_templates,
    name="linked_templates"),

    url(r"^create_specific_template/(?P<model_name>\w{0,50})/(?P<object_id>\d+)/(?P<template_id>\d+)/$",
    create_specific_template,
    name="create_specific_template"),

    ## should be generalized, external link was being appended to internal URL
    url(r"^erasmus-stiftung.de/datenschutz/$",RedirectView.as_view(url="https://erasmus-stiftung.de/datenschutz"),
    name="datenschutz")


] + aldryn_addons.urls.patterns() + i18n_patterns(
    # add your own i18n patterns here
    *aldryn_addons.urls.i18n_patterns()  # MUST be the last entry!
)
