# -*- coding: utf-8 -*-
from crm.views import *
from django.conf.urls import url, include


app_name = 'crm'

urlpatterns = [
    url(r"^person-autocomplete/$", PersonAutocomplete.as_view(), name="person-autocomplete"),

    url(r"^$", registrations_overview, name="registrations_overview"), ## Übersicht aller in der Zukunft liegenden Veranstaltungen mit Links zu Detailansichten der Anmeldungen

    # url(r"^speichern/ajax/(?P<veranstaltung_id>\d+)", ## AJAX call from event page (with registration data) to save view
    # save_registrations_ajax, name="save_registrations_ajax"), ## AJAX call to save data from editing page

    # url(r"ajax/(?P<event_id>\d+)", ## Leitet AJAX-Abfrage von Detailansicht der Anmeldungen einer Veranstaltung an API zur Aktualisierung
    # update_registrations, name="update_registrations"),
    url(r"send_answers_participation/(?P<event_id>\d+)", ## Leitet AJAX-Abfrage von Detailansicht der Anmeldungen einer Veranstaltung an API zur Aktualisierung
    send_answers_participation, name="send_answers_participation"),

    url(r"^ajax_save", ## AJAX call from event page (with registration data) to save view
    ajax_save, name="ajax_save"), ## AJAX call to save data from editing page


    url(r"^export_excel/(?P<event_id>\d+)",
    participants_export_excel, name="participants_export_excel"),

    url(r"^all_participants_export_excel/(?P<event_id>\d+)",
    all_participants_export_excel, name="all_participants_export_excel"),

    url(r'^(?P<veranstaltung_id>\d+)$', ##
    edit_registrations, name="edit_registrations"),

    url(r'^select_room_partner/$', ##
    select_room_partner, name="select_room_partner"),


    url(r'^eingeladene/(?P<event_id>\d+)$', ##
    invited, name="invited_persons"),

    url(r"^einladen/$", invite, name="invite"),
    # url(r"^syncgravityforms/$", syncGravityForms, name="syncGravityForms"),
    # url(r"^update_future_registrations/$", update_future_registrations, name="update_future_registrations"),
    url(r"^seminar_statistics/(?P<event_id>\d+)$", event_statistics, name="seminar_statistics"),

]
