from django.utils.translation import ugettext_lazy as _
from crm.models import *
from dal import autocomplete
from django import forms
from django.forms import ModelForm
from django.forms.widgets import Select

class EventForm(ModelForm):
    class Meta:
        model = Veranstaltung
        # fields = '__all__'
        exclude = ['Einladungstext','description',
        'confirmation_text','confirmed_cache','Format','Vertrag_Raummiete','Eingeladene_Personen',
        'Teilnehmerliste',"Einladung_A4",'participant_list','Ordner_Cloud','valid_form_entries_cache']

class SeminarRegistrationForm(ModelForm):

    Anrede = forms.ModelChoiceField(required=True,
    widget=forms.RadioSelect,
    queryset=None)
    Titel = forms.CharField(        
        widget=forms.TextInput(            
            attrs={'placeholder': 'Dr., Prof., vorangestellter akad. Grad'},
        ),
        required=False
    )

    ## Order and selection in __init__
    bookingoption = forms.ModelChoiceField(required=True,label="Buchungsoption",
    widget=forms.RadioSelect(attrs={"onchange":"bookingOption(event)"}),
    queryset=None) ## Queryset is set on view level

    Anmerkungen = forms.CharField(
        widget=forms.Textarea(
            attrs={'placeholder': 'Hier können Sie uns auch sonstige ergänzende Informationen zu Ihrer Teilnahme mitteilen.'}
        ),
        required=False
    )

    ## Text field not in model. The register function searches for matching text
    ## in the InvitationCode table.
    invitation_code = forms.CharField(
        required=False,label="Einladungscode"
    )

    class Meta:
        model = FormEntry
        fields = ("Anrede","Titel","Familienname","Vorname","E_Mail",
        "Straße","Zusatz_Adresse","Ort","PLZ","bookingoption","Mobiltelefon","Zweitperson_Zimmer",
        "Anmerkungen"
        )
        # labels = {"bookingoption":"Buchungsoption"}

    def __init__(self,*args,event=None,required=True,
    invitation_code_required=False,**kwargs):
        # super(ArchiveForm, self).__init__(*args, **kwargs)
        super(SeminarRegistrationForm,self).__init__(*args,**kwargs)
        bookingoptions = event.calculated_bookingoptions
        if required:
            self.fields["bookingoption"].queryset = event.calculated_bookingoptions.filter(public=True)
        else:
            self.fields["bookingoption"].queryset = event.calculated_bookingoptions
        
        self.fields["bookingoption"].required = required
        self.fields["Anrede"].queryset = Geschlecht.objects.exclude(Herr_Frau__icontains="Eheleute")
        self.event = event
        self.invitation_code_required = invitation_code_required

    def clean(self):
        '''Custom validation logic for invitation code,
        may be moved to event object (invitation_code_required logic from view should move with it).'''
        cleaned_data = super().clean()
        cleaned_data["invitation_code"] = None
        if self.invitation_code_required:
            invitation_code_string = cleaned_data.get("invitation_code",False)
            if InvitationCode.objects.filter(text=invitation_code_string).exists():
                invitation_code = InvitationCode.objects.get(text=invitation_code_string)
                ## If invitation_code.event is None, the code can be used for any event.
                if invitation_code.event == self.event or not invitation_code.event:
                    cleaned_data["invitation_code"] = invitation_code
                else:
                    raise forms.ValidationError("Der Einladungscode ist nicht für diese Veranstaltung gültig.")
            else:
                raise forms.ValidationError("Der eingegebene Einladungscode ist ungültig.")            
        
        self.cleaned_data = cleaned_data
        
        return(cleaned_data)


class RoomPartnerForm(ModelForm):
    '''Used by views.select_room_partner to present ajax save tags around list 
    of available room partners, selection logic is in view,
    display logic is in template'''
    class Meta:
        model = FormEntry
        fields = ["room_partner"]
        widgets = {
            "room_partner":Select(attrs={"onchange":"roomPartnerChange(event)"})
        }

class SeminarForm(ModelForm):
    '''Used for ajax quick edit fields above table in views.edit_registrations'''
    class Meta:
        model = Veranstaltung
        fields = ["Veranstaltungsort","Veranstaltungsraum",
        "Straße","PLZ","Ort","hotel_rooms"]

class DateInput(forms.DateInput):
    '''Date input form compatible with
    AJAX save function'''
    input_type = "date"

    def format_value(self,value):
        if value:
            return(value.strftime("%Y-%m-%dT%H")) #"yyyy-MM-dd" followed by optional ":ss" or ":ss.SSS".
        else:
            return("")

class DateTimeInput(forms.DateInput):
    '''Datetime input form compatible with
    AJAX save function'''
    input_type = "datetime-local"

    def format_value(self,value):
        if value:
            return(value.strftime("%Y-%m-%dT%H:%M:%S")) #"yyyy-MM-ddThh:mm" followed by optional ":ss" or ":ss.SSS".
        else:
            return("")

class PersonAutocompleteForm(forms.ModelForm):
    '''Django AutoComplete form for finding people by last name'''
    Familienname = forms.ModelChoiceField(queryset=Person.objects.all(),
    widget=autocomplete.ModelSelect2(url="crm:person-autocomplete"))
    class Meta:
        model = Person
        fields = ("Familienname",)

## For AutoComplete, not in use because not functional 
# class GroupForm(forms.ModelForm):
#     # persons = forms.ModelChoiceField(queryset=Person.objects.all(),
#     # widget=autocomplete.ModelSelect2Multiple(url="crm:person-autocomplete"))
#     class Meta:
#         model = Group
#         exclude = ("Fachgruppen","persons")

# class FormEntryForm(forms.ModelForm):
#     class Meta:
#         model = FormEntry
#         fields = '__all__'
#
