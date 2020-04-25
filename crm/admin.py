#-*- coding: utf-8 -*-
from django.contrib import admin
from adminsortable.admin import NonSortableParentAdmin, SortableStackedInline,SortableAdmin,SortableTabularInline
from .models import *
from django.utils.translation import ugettext_lazy as _
admin.site.site_header = _("Verwaltung")
admin.site.site_title = _("Intranet")

# from crm.forms import GroupForm - for autocomplete, not in use
@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    pass
#    form = GroupForm


@admin.register(Modul)
class ModulAdmin(admin.ModelAdmin):
    list_display = ["Bezeichnung","short_name","Beschreibung","Format"]
    list_editable = ["short_name","Beschreibung","Format"]

class ConsentInline(admin.TabularInline):
    model = Consent
    extra = 0
    readonly_fields = ("text",)

@admin.register(FormEntry)
class FormEntryAdmin(admin.ModelAdmin):
    model = FormEntry
    inlines = [ConsentInline]
    fieldsets = [
        ("Name",
        {"fields": [
        ("Anrede","Vorname","Familienname"),
        ("Titel","Funktion","Institution"),
        ("_person",)
        ]}),

        ("Adresse",
        {"fields":[
            ("Straße","Zusatz_Adresse"),
            ("Ort","PLZ"),        ]
        }),

        ("Kontakt",
        {"fields":[
            ("E_Mail","Mobiltelefon")]
        }),

        ("Buchung",
        {"fields":[("invitation_code",),
        ("referent","Status"),
        ("bookingoption",),
            ("Zweitperson_Zimmer","room_partner")],
        }),

        ("Anmerkungen",
        {"fields":[
            ("Anmerkungen","Anmerkungen_Sachbearbeiter")]
        }),

    ]
    search_fields = ['Familienname','Vorname','E_Mail']
    list_display = ('Familienname','Vorname','E_Mail',
    'Status','Veranstaltung')
    readonly_fields = ("JSON","entry_id","form_id",
    "date_created","date_updated","Anmerkungen",
    "invitation_code",
    "user_agent","source_url","Zweitperson_Zimmer","ip")
    ordering = ("-date_created",)
    # list_editable = ('Mobiltelefon','Zweitperson_Zimmer')

@admin.register(Rechnung)
class RechnungAdmin(admin.ModelAdmin):
    model = Rechnung
    search_fields = ['Dienstleister','Gegenstand','Rechnungsnsnummer_extern','Rechnungsbetrag']
    list_display = ('Rechnungsdatum',"Gegenstand","Dienstleister",'Rechnungsnsnummer_extern','an_Buchhaltung_weitergeleitet')
    list_editable = ('an_Buchhaltung_weitergeleitet',)

class RechnungInline(admin.TabularInline):
    model = Rechnung
    extra = 0


admin.site.register(BookingOption,SortableAdmin)

# @admin.register(BookingOption)
# class BookingOptionAdmin(admin.ModelAdmin):
#     list_display = ('roomtype','event','format','price_participant','formvalue','abbreviation')
#     list_editable = ('abbreviation','formvalue','price_participant')

class BookingOptionInline(SortableTabularInline):
    model = BookingOption
    extra = 0
    # exclude = ("formlabel",)
    # readonly_fields = ("format",)
@admin.register(Format)
class FormatAdmin(NonSortableParentAdmin):
    fieldsets = [
        (None, {
            'fields': [
    ("Bezeichnung","plural_designation"),
    ("Einlass","Beginn","Ende"),
    ("public","Maximale_Teilnehmer","email"),
    ("confirmation","denial")
    ] } ) ]
    inlines = [BookingOptionInline]

@admin.register(RoomType)
class RoomTypeAdmin(NonSortableParentAdmin):
    inlines = [BookingOptionInline]


class FormEntryInline(admin.TabularInline):
    search_fields = ['Familienname','Vorname','E_mail']
    model = FormEntry
    extra = 0
    readonly_fields = ("date_created","Veranstaltung","E_Mail","Status","bookingoption")
    fields = ('date_created','Veranstaltung','E_Mail','Status','bookingoption')

class InvitationCodeInline(admin.TabularInline):
    model = InvitationCode
    extra = 0
    exclude = ("person",)

@admin.register(Veranstaltung)
class VeranstaltungAdmin(NonSortableParentAdmin):
    readonly_fields = ["Anmeldungsseite",'id','Maximale_Teilnehmer_']
    list_display = ('Beginn','Titel','Raum_Einladung','Modul','site_ready',"site_listed","link_active")
    ordering = ('Beginn',)
    exclude = ('Eingeladene_Personen',)
    list_editable = ('Modul','site_ready',"site_listed","link_active")
    list_filter = ("Modul",'Beginn',"Bundesland","site_ready")
#    inlines = [BookingOptionInline,RechnungInline]#
    inlines = [BookingOptionInline,InvitationCodeInline]#
    ordering = ("-Beginn",)

    fieldsets = [
        ("Basisdaten", {
            'fields': [
                ('Raum_Einladung','Kostenstelle'),
                ('Titel','Inhalt'),
                ('Format','Modul'),]} ),

        ("Zeitpunkt", {
            'fields': [            
                ('Einlass',),
                ('Beginn','Ende'),]} ) ,

        ("Texte",{
            'fields': [
            # ("Einladungstext",),
            # ('confirmation_text','description'),
            # ('confirm_with_address'),
            ('Einladung_A4','Ordner_Cloud')]} ),

        ("Seite", {
            'fields': [            
            ('site_ready',"site_listed"),
            ("notice","link_active"),
            ("video"),
            ]}, ),
        
        ("Ort", {
            'fields': [
            ('Veranstaltungsort','Veranstaltungsraum'),
            ('Straße','Zusatz_Adresse'),
            ('PLZ','Ort','Bundesland'),
            ('hotel_rooms','Maximale_Teilnehmer','Maximale_Teilnehmer_'),
            ('Bemerkungen_Sachbearbeiter','Vertrag_Raummiete'),
            ("participant_list",)
            ]}
        ) ]

        # ("Ort", {
        #     'fields': [            
        #     ('Veranstaltungsort','Veranstaltungsraum'),
        #     ('Straße','Zusatz_Adresse'),
        #     ('PLZ','Ort','Bundesland'),
        #     ('hotel_rooms','Maximale_Teilnehmer','Maximale_Teilnehmer_'),
        #     ('Bemerkungen_Sachbearbeiter','Vertrag_Raummiete'),
        #     ("participant_list",) ]} )
        #     ]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "Modul":
            kwargs["queryset"] = Modul.objects.order_by('Bezeichnung')
        if db_field.name == "Format":
            kwargs["queryset"] = Format.objects.order_by('Bezeichnung')

        return super(VeranstaltungAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


class KreisInline(admin.StackedInline):
    model = Kreis
    fields = ["Name_Kreis","RegBez"]
    readonly_fields = ["Nr_Kreis"]

@admin.register(Funktion)
class FunktionAdmin(admin.ModelAdmin):
    search_fields = ['Nr_Fkt','Name_Fkt']
    ordering = ("Nr_Fkt",)
    readonly_fields = ["Übergeordnete_Fachgruppe"]
    list_filter = ("Fachgruppe",)
    list_display = ("Nr_Fkt","Name_Fkt","Fachgruppe")



class FunktionInline(admin.StackedInline):
    model = Funktion
    extra = 0
    fields = ["Name_Fkt","Nr_Fkt"]
    def get_edit_link(self, obj=None):
        if obj.pk:  # if object has already been saved and has a primary key, show link to it
            url = reverse('admin:%s_%s_change' % (obj._meta.app_label, obj._meta.model_name), args=[force_text(obj.pk)])
            return """<a href="{url}">{text}</a>""".format(
                url=url,
                text=_("Edit this %s separately") % obj._meta.verbose_name,
            )
        return _("(save and continue editing to create a link)")
    get_edit_link.short_description = _("Edit link")
    get_edit_link.allow_tags = True

# @admin.register(Bundesland)
# class BundeslandAdmin(admin.ModelAdmin):
#     ordering = ('Landesverband',)
#     inlines = [KreisInline]

class CommunicationInline(admin.TabularInline):
    model = Communication
    extra = 0
    fields = ("sent_on","E_Mail","event","category","message")
    readonly_fields = ("sent_on","message")

class PersonInline(admin.StackedInline):
    model = Person
    extra = 0
    fields = ["E_Mail"]
    # readonly_fields = ["an_name"]

@admin.register(Kreis)
class KreisAdmin(admin.ModelAdmin):
    ordering = ('Name_Kreis','Bundesland','RegBez','Nr_Kreis',)
    search_fields = ['Nr_Kreis','Name_Kreis']
    readonly_fields = ["Nr_Kreis","Bundesland"]
    list_display = ["Name_Kreis","Bundesland","Nr_Kreis","RegBez"]
    list_filter = ("Bundesland","RegBez")
    inlines = [PersonInline]

@admin.register(Fachgruppe)
class FachgruppeAdmin(admin.ModelAdmin):
    inlines = [FunktionInline]
    ordering = ('Min',)

@admin.register(PersonFunction)
class PersonFunctionAdmin(admin.ModelAdmin):
    list_filter = ("Bundesland","Fachgruppe","Funktion")
    list_display = ("Funktion","Person","Bundesland","Tel1","Tel2","Kreis")
    list_editable = ("Bundesland","Kreis")
    autocomplete_fields = ("Person",)

    def get_queryset(self,request):
        queryset = super(PersonFunctionAdmin,self).get_queryset(request)
        queryset = queryset.order_by("Person__Familienname")
        return(queryset)

# class PersonFunctionForm(forms.ModelForm):
#     class Meta:
#         model = PersonFunction
#         fields = ("Person","Funktion","Fachgruppe","Bundesland","Kreis")
#         widgets = {""}

class PersonFunctionInline(admin.TabularInline):
    model = PersonFunction
    extra = 0

    fields = ("Person","Funktion","Bundesland","Kreis")

@admin.register(Priorität)
class PriorityAdmin(admin.ModelAdmin):
    readonly_fields = ("pk",)
    fields = ("Bezeichnung","pk")
    pass
#    inlines = (MembershipInline,)
@admin.register(GravityFormular)
class GravityFormularAdmin(admin.ModelAdmin):
    pass

@admin.register(Email)
class EmailAdmin(admin.ModelAdmin):
    list_display = ("email","aktiv","Bemerkungen_Sachbearbeiter")
    search_fields = ("email",)
    pass
#    inlines = (MembershipInline,)

class EmailInline(admin.TabularInline):
    model = Email
    extra = 0

@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {
            'fields': [('Anrede','Titel'),
            ('Vorname','Familienname'),
            ('Priorität','Titel_nachgestellt'),
            ('Institution','Funktion'),
            ('E_Mail','Tel1','Tel2'),
            ('Zusatz_Adresse','Straße'),
            ('PLZ','Ort'),
            ('Kreis','Bundesland'),
            ('Quelle','Notizen'),
            ('Partei','ausschließen')],
        }),
    ]
    list_display = ('Familienname','Vorname','E_Mail','Priorität')
    list_editable = ('Priorität',)
    list_filter = ("Priorität","Bundesland","Partei")
    readonly_fields = ('an_name',)
    search_fields = ['Familienname','Vorname','E_Mail','Tel1','Notizen']
    list_display_links = ("Familienname","Vorname")
    inlines = [EmailInline,PersonFunctionInline,FormEntryInline,CommunicationInline]
    def formfield_for_dbfield(self, db_field, **kwargs):
        from django import forms
        formfield = super(PersonAdmin, self).formfield_for_dbfield(db_field, **kwargs)
        if db_field.name == 'Quelle':
            formfield.widget = forms.Textarea(attrs=formfield.widget.attrs)
        return formfield
#    form = PersonForm

class TemplateConnectionInline(admin.TabularInline):
    model = TemplateConnection
    extra = 0

@admin.register(Inheritance)
class InheritanceAdmin(admin.ModelAdmin):
    pass

@admin.register(MessagePart)
class MessagePartAdmin(SortableAdmin):
    pass

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    pass

@admin.register(DbTemplate)
class DbTemplate(SortableAdmin):
    inlines = [TemplateConnectionInline]
    list_display = ["category","message_part","name","content_model"]

@admin.register(TemplateConnection)
class TemplateConnection(admin.ModelAdmin):
    list_display = ["template","content_model","content_type","content_object"]