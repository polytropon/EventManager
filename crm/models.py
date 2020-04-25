from crm import *
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.text import slugify
from django.contrib.auth.models import User

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

import hashlib
# from gmail.send import send
from django.template.loader import get_template
# from django.template import Context
from crm.utility_routines import postcode_to_Bundesland
from datetime import datetime
# import logging
# logger = logging.getLogger(__name__)

SECRET_KEY = 'No ENVIRONMENT variable!'
from django.template.loader import render_to_string
import json
from crm import gravity
from custom_utils.sorter import multisort
from collections import OrderedDict
import math
ENVIRONMENT = os.getenv('ENVIRONMENT','No ENVIRONMENT variable!')

import logging
logger = logging.getLogger("telegram_logger")

class Fachgruppe(models.Model):
    ## Higher-level category containing number of Funktionen within a number range
    Min = models.IntegerField(blank=True,null=True) ## Lower bound of Funktion.Nr_Funktion in this Fachgruppe
    Max = models.IntegerField(blank=True,null=True) ## Upped bound
    Bezeichnung = models.CharField(max_length=100,blank=True,unique=True)
    class Meta:
        verbose_name = _("Fachgruppe")
        verbose_name_plural = _("Fachgruppen")

    def __str__(self):
        return(f"{self.Bezeichnung} ({self.Min})") ##

class Funktion(models.Model):
    '''Funktion (Ursprung: SharePoint) '''
    Nr_Fkt = models.IntegerField(blank=True,null=True) ## Index falls between Min and Max of a Fachgruppe
    Fachgruppe = models.ForeignKey(Fachgruppe,verbose_name='Funktion',on_delete=models.CASCADE)
    Name_Fkt = models.CharField(max_length=100,blank=True,unique=False) ## Should not be unique, because some Funktionen are repeated in different Fachgruppen
    class Meta:
        verbose_name = _("Funktion")
        verbose_name_plural = _("Funktionen")
    @property
    def Übergeordnete_Fachgruppe(self):
        '''TODO: Output link to edit page'''
        if hasattr(self,"Fachgruppe"):
            return(self.Fachgruppe.Bezeichnung)
        else:
            return("")
    def __str__(self):
        if self.Fachgruppe.Bezeichnung and self.Nr_Fkt:
            return(f"{self.Name_Fkt}: {self.Nr_Fkt} ({self.Fachgruppe.Bezeichnung})")
        elif self.Nr_Fkt:
            return(f"{self.Name_Fkt}: {self.Nr_Fkt}")
        elif self.Fachgruppe:
            return(f"{self.Name_Fkt} ({self.Fachgruppe.Bezeichnung})")
        else:
            return(self.Name_Fkt)

class Partei(models.Model):
    Kürzel = models.CharField(max_length=25,blank=True,unique=True)
    Langbezeichung = models.CharField(max_length=50,blank=True,unique=False)
    def __str__(self):
        return(self.Kürzel)

class Modul(models.Model):
    '''Type of seminar, e.g. Rhetorik 1, Islam'''
    Bezeichnung = models.CharField(max_length=200,blank=True,unique=True)
    short_name = models.CharField("Kurzbezeichnung",max_length=60,blank=True,
    help_text="Kürzere Bezeichnung für Modul für Verwendungszweck und interne Verwendung")
    Beschreibung = models.TextField(null=True,blank=True)
    Maximale_Teilnehmer = models.IntegerField(null=True,blank=True)
    public = models.BooleanField("öffentlich",blank=True,default=False,
    help_text="Wenn dieser Haken gesetzt ist, werden einzelne Veranstalungen dieses Moduls öffentlich auf der Seite angezeigt, sofern der Haken »Seite startklar« auch gesetzt ist.")
    
    Format = models.ForeignKey("Format",blank=False,
    null=True,verbose_name="Format dieses Moduls",
    on_delete=models.SET_NULL)

    @property
    def all_registrants(self):
        registrants = []
        for event in self.events.all():
            registrants.extend([fe.person for fe in event.FormEntries.all()])
        registrants = set(registrants)
        return(registrants)

    class Meta:
        verbose_name = "Modul"
        verbose_name_plural = "Module"
    def __str__(self):
        return(self.Bezeichnung)

class Format(models.Model):
    app_label = "crm"
    model_name = "format"

    Bezeichnung = models.CharField(max_length=25,blank=True,unique=True)
    plural_designation = models.CharField("Plural",help_text="Pluralform der Bezeichnung (Kongresse, Seminare) für z.B. Auflistungen auf der Seite",
    max_length=25,blank=True,unique=False)
    Maximale_Teilnehmer = models.IntegerField(null=True,blank=True)
    
    Einlass = models.TimeField(blank=True,null=True)
    Beginn = models.TimeField(blank=True,null=True)
    Ende = models.TimeField(blank=True,null=True)
    public = models.BooleanField("öffentlich",blank=True,default=False)
    ## Used by class Veranstaltung to choose email address from which to send
    email = models.EmailField("Absender E-Mail für automatische Nachrichten",max_length=254,null=True,blank=True)

    ## Optional, used by function get_email_template
    confirmation = models.TextField("Vorlage für Bestätigung",null=True,blank=True)
    denial = models.TextField("Vorlage für Absage",null=True,blank=True)

    class Meta:
        verbose_name = "Veranstaltungsformat"
        verbose_name_plural = "Formate"
        # app_label = "format"

    # def all(self):
    #     self.future + self.past

    def future(self):
        return(self.events.filter(Beginn__gte=datetime.today()).filter(site_ready=True).order_by("Beginn"))

    def past(self):
        return(self.events.filter(Beginn__lte=datetime.today()).order_by("-Beginn"))

    def __str__(self):
        return(self.Bezeichnung)

class Priorität(models.Model):
    app_label = "crm"
    model_name = "priorität"

    Bezeichnung = models.CharField(max_length=25,blank=True,unique=True)

    class Meta:
        verbose_name = "Priorität der Einladung"
        verbose_name_plural = "Prioritäten"
    def __str__(self):
        return(self.Bezeichnung)

class Bundesland(models.Model):
    Landesverband = models.CharField(max_length=25,blank=True,unique=True)
    LV = models.CharField(max_length=2,blank=True,unique=True)

    class Meta:
        verbose_name = "Bundesland"
        verbose_name_plural = "Bundesländer"
    def __str__(self):
        return(self.Landesverband)

class Kreis(models.Model):
    Bundesland = models.ForeignKey(Bundesland, on_delete=models.CASCADE,null=True) ## Warning: Kreis 1001 has unknown Bundesland
    Nr_Kreis = models.IntegerField(blank=True,null=True)
    RegBez = models.CharField(max_length=50,blank=True,null=True)
    Name_Kreis = models.CharField(max_length=100,blank=True,null=True)
    class Meta:
        verbose_name = _("Kreis")
        verbose_name_plural = _("Kreise")

    def __str__(self):
        return(f"{self.Nr_Kreis}: {self.Name_Kreis}")

class PostcodeRange(models.Model):
    '''Ranges of postal codes with corresponding German regions.'''
    Bundesland = models.ForeignKey(Bundesland, on_delete=models.CASCADE,null=True) ## Warning: Kreis 1001 has unknown Bundesland
    Min = models.IntegerField(blank=False,null=False)
    Max = models.IntegerField(blank=False,null=False)
    class Meta:
        verbose_name = _("PLZ")
        verbose_name_plural = _("PLZ")

class Geschlecht(models.Model):
    '''Herr/Frau/Eheleute'''
    Herr_Frau = models.CharField(max_length=8, blank=True, null=True) ## String "Herr" or "Frau"
    Endung = models.CharField(max_length=1, blank=True, null=True) ## empty string or 'e' for feminine
    class Meta:
        verbose_name = "Geschlecht für Anrede (Herr/Frau)"
        verbose_name_plural = "Geschlechter"

    def __str__(self):
        return(self.Herr_Frau)



class Person(models.Model):
    app_label = "crm"
    model_name = "person"

    Anrede = models.ForeignKey(Geschlecht, on_delete=models.SET_NULL,null=True)
    Titel = models.CharField(max_length=50,blank=True,null=True)
    Familienname = models.CharField(max_length=100,blank=True,null=True)

    Vorname = models.CharField(max_length=100,blank=True,null=True)
    Titel_nachgestellt = models.CharField(max_length=20,blank=True,null=True)
    E_Mail = models.EmailField(max_length=100,blank=True,null=True)
    Zusatz_Adresse = models.CharField(max_length=100,blank=True,null=True)
    Straße = models.CharField(max_length=100,blank=True,null=True)
    PLZ = models.CharField(max_length=50,blank=True,null=True)
    Ort = models.CharField(max_length=100,blank=True,null=True)
    Funktion = models.CharField(max_length=1000,blank=True,null=True)
    Institution = models.CharField(max_length=200,blank=True,null=True)
    Tel1 = models.CharField("Telefonnummer 1",max_length=500,blank=True,null=True)
    Tel2 = models.CharField("Telefonnummer 2",max_length=500,blank=True,null=True)
    Quelle = models.CharField(max_length=500,blank=True,null=True)

    Bundesland = models.ForeignKey(Bundesland, on_delete=models.SET_NULL,null=True,blank=True)
    Kreis = models.ForeignKey(Kreis, on_delete=models.SET_NULL,null=True,blank=True)

    Partei = models.ForeignKey(Partei, on_delete=models.SET_NULL,null=True,blank=True)
    Priorität = models.ForeignKey(Priorität, on_delete=models.SET_NULL,null=True,blank=True)
    verantwortlich = models.CharField(max_length=30,blank=True,null=True)
    ausschließen = models.DateField("ausschließen",blank=True,null=True)
    ## Legacy field from Google table included in url params for some registration links
    Index = models.IntegerField(blank=True,null=True)
    ## Index from SEWOBE exports, first column
    Lfd_Nr_SEWOBE = models.IntegerField(blank=True,null=True)

    ## ID from SharePoint records
    SharePoint_ID = models.IntegerField(blank=True,null=True)
    ## Legacy field with data from Hausberger
    Jahrgang = models.IntegerField(blank=True,null=True)

    Land = models.CharField(max_length=30,blank=True,null=True)
    Notizen = models.TextField(max_length=500,blank=True,null=True)

    date_created = models.DateTimeField("eingegangen",auto_now_add=True,null=False)
    date_updated = models.DateTimeField(auto_now_add=True,null=True)

    class Meta:
        verbose_name = "Person"
        verbose_name_plural = "Personen"

    @property
    def email(self):
        '''Return primary email, if not exists,
        look in email table and form entries for alternate emails,
        save first found as primary,
        return first email found.
        '''
        if self.E_Mail:
            return(self.E_Mail)
        else:
            emails = self.emails.filter(aktiv=True) ## Deactivated emails excluded
            if len(emails) > 0:
                self.E_Mail = emails[0].email
                self.save()
                return(emails[0].email)
            else:
                formentries = self.formentries.order_by("-date_created")
                if len(formentries) > 0:
                    email = formentries[0].E_Mail
                    self.E_Mail = email
                    self.save()
                    return(email)

    def __str__(self):
        if self.Vorname:
            return(f"{self.Familienname}, {self.Vorname}")
        elif self.Familienname:
            return(self.Familienname)
        else:
            return("")

    def save(self,*args,**kw):
        if self.Bundesland == None:
            self.kreis_to_bundesland()
        if self.Bundesland == None:
            self.plz_to_bundesland()
        super( Person, self ).save(*args,**kw)

    def initialize_event(self,event):
        '''Set temporary, non-saved attributes
        Invitiation code is required by send function because it is a template variable
        Create params link although possibly not needed'''
        return({"einladungscode":self._einladungscode(event),"params_link":
        self._params_link(event)})

    def plz_to_bundesland(self):
        if not self.Bundesland:
            if self.PLZ not in ("",None) and self.PLZ.isdigit():
                self.Bundesland = postcode_to_Bundesland(self.PLZ)

    def kreis_to_bundesland(self):
        '''If Kreis is saved, but not Bundesland in which
        Kreis is located, set Bundesland (do not save)'''
        if self.Kreis and not self.Bundesland:
            self.Bundesland = self.Kreis.Bundesland
            return(self.Bundesland)

    @property
    def _Anrede(self):
        '''Get many-to-one Geschlecht object if exists'''
        if self.Anrede != None:
            if self.Anrede.Herr_Frau == "Eheleute":
                return("Familie") ## as in "Sehr geehrte Familie xy,"
            else:
                return(self.Anrede.Herr_Frau) # Set Anrede to string "Herr" or "Frau"
        else: ## Return empty string if no Geschlecht object
            return("")

    def invitations(self,event):
        return([c for c in self.communication.all() if c.type == 1 and c.event == event])

    def last_invited(self,event):
        '''Datetime on which person last invited to event'''
        invitations = self.invitations(event)
        if invitations:
            latest_invitation = max(invitations,key = lambda invitation:invitation.sent_on)
            return(latest_invitation.sent_on)
        else:
            return(False)

    def days_since_invited(self,event):
        '''Number of days since person last invited to event'''
        timedelta_diff = datetime.now() - self.last_invited(event)
        return(timedelta_diff.days)

    def invite(self,event,reinvite_after_days=5):
        '''
        TODO: Eliminate spaghetti code, move all content to template system

        Only invite non-excluded people to future events,
        remind them after number of days "reinvite_after_days"
        '''
        ## Invitations only to future events
        return_dict = {"person_id":self.pk}
        if event.Beginn < datetime.now():
            return_dict["message"] = f"Veranstaltung liegt in der Vergangenheit, keine Einladung mehr möglich."

        elif not self.email:
            return({"message":f"Keine E-Mail vorhanden für {self.an_name}."})
        else:
            event_communication = Communication.objects.filter(event=event,person=self)
            if self.ausschließen:
                return_dict["message"] = f"Diese Person wurde am {self.ausschließen.strftime('%d.%m. um %H:%M Uhr')} von Einladungen ausgeschlossen."
            elif self.Priorität:
                if "nicht einladen" in self.Priorität.Bezeichnung:
                    return_dict["message"] = f"{self} wurde der Kategorie 'nicht einladen' zugeordnet."

            for communication in event_communication:
                if communication.type in (3,4,5):
                    choice_text = [choice[1] for choice in Communication.type_CHOICES if choice[0] == communication.type][0]
                    ## participant has cancelled, given a negative answer or already received a confirmation
                    return {"message":f"{choice_text} übermittelt {self.an_name} am {communication.sent_on.strftime('%d.%m. um %H:%M Uhr')}, keine Einladung."}
            else:
                last_invited = self.last_invited(event)
                if not last_invited:
                    subject = f"Einladung: {event.Inhalt} / {event.Beginn.strftime('%d.%m. / %H Uhr')}"
                    self.send_message(subject,event.Einladungstext,
                    test=False,event=event,type=1,
                    html_message=event.html_invitation
                    )
                    return_dict["message"] = f"Sie haben {self.an_name} eingeladen."
                else:
                    if self.days_since_invited(event) > reinvite_after_days:
                        last_invited = self.last_invited(event) ## Run before send_message, which creates new Communication record, so as show previous invitation and not new one
                        subject = f"Erinnerung: {event.Inhalt} / {event.Beginn.strftime('%d.%m. / %H Uhr')}"
                        self.send_message(subject,event.Einladungstext,
                        test=False,event=event,type=1,
                        html_message=event.html_invitation
                        )
                        return_dict["message"] = f"{self} wurde erneut eingeladen (letzte Einladung {last_invited.strftime('%d.%m. um %H:%M Uhr')})."
                    else:
                        return_dict["message"] = f"Ein Intranet-Benutzer hat {self.an_name} zum letzten Mal am {self.last_invited(event).strftime('%d.%m. um %H:%M Uhr')} eingeladen. {reinvite_after_days} Tage sind noch nicht verstrichen."
        return(return_dict)

    def send_message(self,subject,message,test=True,
    event=None,type=None,send_from_email="veranstaltungen@erasmus-stiftung.de",
    html_message=None):
        '''Create and send message to primary email address using email API
        Save Communication record for message, including type of message and event if given'''

        if ENVIRONMENT == 'local':
            test = True
        if event != None:
            self.initialize_event(event)
        message = self.message(message)
        
        if not hasattr(self,"einladungscode"):
            self.einladungscode = ""
        # assert hasattr(self,"einladungscode")
        response_dict = {"subject":subject,"message":message,
        "test":test,"an_name":self.an_name,
        "E_Mail":self.E_Mail,
        "einladungscode":self.einladungscode}
        # if test:
        #     logger.info(response_dict)
        #     return(response_dict)
        # else:
        subject = subject.replace("\n","")
        send_mail(subject, message, send_from_email, [self.email],
        html_message=html_message)
            # send(send_from_email,
            #      self.E_Mail,
            #      subject=subject,
            #      message_text=message)
        Communication.objects.create(person=self,
        event=event,message=message,type=type,medium=1,E_Mail=self.E_Mail)
        return(response_dict)

    def message(self,message):
        attributes = {attribute:getattr(self,attribute) for attribute in ("anrede","akkusativ","dativ",'an_name','einladungscode','params_link') if hasattr(self,attribute)}
        return(message.format(**attributes))

    @property
    def botschafter(self):
        'Return True if the person is an ambassador, False if not'
        if hasattr(self,"Funktion") and self.Funktion != None and self.Funktion.find("Botschafter") != -1:
            return(True)
        else:
            return(False)

    @property
    def name_with_titel(self):
        return(self.an_name.replace("Herrn","Herr"))

    @property
    def an_name(self):
        '''Return Herrn/Frau Vorname Nachname for address
        e.g. Herrn Michael Schmidt / Frau Julia Müller'''
        #If one of of the necessary fields is missing or is an empty string, return false
        for x in ("Vorname","Familienname","Anrede"):
            if not hasattr(self,x) or getattr(self,x) in ("",None):
                return("")
        else: ## If all necessary fields are present, add titles
            full_name = f"{self.Vorname} {self.Familienname}"

            ## Add academic title
            if hasattr(self,"Titel") and self.Titel not in ("",None) and self.Titel in ("Dr.","Prof."):
                full_name = self.Titel + " " + full_name

            ## Add Amtstitel
            if hasattr(self,"Titel_nachgestellt") and self.Titel_nachgestellt not in ("",None):
                full_name = f"{full_name}, {self.Titel_nachgestellt}"

            ## Add Herrn or Frau if the person is not "Sir" or Botschafter
            if not self.Titel or (not "Sir" in self.Titel and not self.botschafter):
                ad = {"Herr":"n","Frau":"","Eheleute":""}
                if self._Anrede not in ad:
        ## KNOWN BUG: If someone was mailed to anonymously, but then registers, the loop uses
        ## a person object without data from the main table, causing an error when parsing Anrede
                    logger.error('Anrede {self._Anrede} is not in Herr or Frau!')
                else:
                    ## Herrn / Frau Vorname Familienname
                    full_name = self._Anrede + ad[self._Anrede] + " " + full_name

            ## Seine Exzellenz Herr xxx
            ## https://www.sekretaria.de/bueroorganisation/korrespondenz/geschaeftsbriefe/adelige-wuerdentraeger-anschreiben/
            if self.botschafter:
                full_name = {"Herr":"Seine Exzellenz","Frau":"Ihre Exzellenz"}[self._Anrede] + "\n" + {"Herr":"Herrn Botschafter","Frau":"Frau Botschafterin"}[self._Anrede] + "\n" + full_name
        return(full_name)

    @property
    def titel(self):
        '''
        Convert Prof. (Dr. etc.) to Professor, used for Sehr geehrter Herr xx in self._Anrede,
        Return empty string if object has no attribute "Titel" or if title is not Prof., Dr. or Botschafter
        '''
        endung = {"Herr":"","Frau":"in"}[self.Anrede.Herr_Frau] ## For Frau Professorin, Frau Botschafterin
        if self.Titel in (None,""):
            return("")
        else:
            if "Prof." in self.Titel and not self.botschafter: ## Botschafter trumps professor
                return(f"Professor{endung}") ## Converts Prof. xx to Professor(in)
            elif self.botschafter: ## Botschafter(in)
                return(f"Botschafter{endung}")
            elif "Dr." in self.Titel:
                return(self.Titel)
            else: ## Other titles are disregarded, this may be changed for i.e. Bischof
                return("")

    @property
    def dativ(self):
        return({"du":"dir","Du":"Dir","Sie":"Ihnen"}[self.Artikel])

    @property
    def akkusativ(self):
        return({"du":"dich","Du":"Dich","Sie":"Sie"}[self.Artikel])

    @property
    def anrede(self):
        '''Create "Sehr geehrter Herr xy" with
        correct titles, including for ambassadors'''
        if self._Anrede in ("Herr","Frau"):
            geschlecht_m_f = {"Herr":"m","Frau":"f"}[self._Anrede]
            herr_frau = self._Anrede
        else:
            self.Artikel = "Sie"
            self._anrede = "Sehr geehrte Damen und Herren," ## Save for logger
            return("Sehr geehrte Damen und Herren,")

        endung = {"m":"r","f":""}[geschlecht_m_f] ## "e" is included

        if not hasattr(self,"Artikel"):
            self.Artikel = "Sie"

        if self.Artikel in ("du","Du"):
            name = self.Vorname

        elif self.Artikel == "Sie":
            if self.titel not in ('', None):
                name = f"{herr_frau} {self.titel} {self.Familienname}"
            else:
                name = f"{herr_frau} {self.Familienname}"

        self._anrede = f"Sehr geehrte{endung} {name},"

        if self.Titel and "Sir" in self.Titel:
            self._anrede = f"Sehr geehrter {self.titel} {self.Familienname},"

        return(self._anrede)

    def _einladungscode(self,event):
        '''run person._einladungscode before sending invitation!'''
        code = hashlib.sha224(f"{SECRET_KEY}{self.id}{event.pk}".encode()).hexdigest()[:6].upper()
        self.einladungscode = code
        return(code)

    @property
    def gravity_csv_dict(self):
        '''Return dict for creating invitation code csv file for Gravity
        invitation code add-on'. Used by function generate_codes'''
        return({"invitation_code_text":self.einladungscode,
        "invitation_count":"1", ## Can optionally be adapted to give certain people multiple codes.
        "invitation_code_name":f'{self.Index}: {self.Familienname}-{self.Vorname}'})

    def _params_link(self,event):
        '''Prepend global variable event_page, i.e. erasmus-stiftung/event/gauweiler
 to url_params to make a complete link'''
        self.params_link = f'{event.Seite}?{self.url_params}'
        return(self.params_link)
        # return(f'{event.Seite}?{self.url_params}')

    @property
    def url_params(self):
        '''Create url-encoded param string from selected items in Person dict
used by params_link.
Relies on "Erweitert->Erlaube die dynamische Befüllung" and Parametername in Gravity form to work on page.
'''
        from urllib.parse import urlencode
        url_params = {key:getattr(self,key) for key in ('Vorname','Familienname',
        'E_Mail','Titel','Anrede','Index') if getattr(self,key)} ## Filter out None, empty string
        if hasattr(self,"einladungscode"):
            url_params["einladungscode"] = self.einladungscode
        return(urlencode(url_params))

def get_email_template(event,name=""):
    '''Veranstaltung.save and FormEntry.answer_participation
    use this function to get confirmation / denial template from
    crm/email (default) or e.g. crm/seminar/ (for specific type of event)
    ## Will be made obsolete by custom_utils.templates.simple_render, which renders from string to string
    '''

    if event.Format and hasattr(event.Format,name):
        template_text = getattr(event.Format,name)
        from django.template import engines, TemplateSyntaxError
        engine = engines.all()[0]
        template = engine.from_string(template_text)

    # try:
        # template = get_template(f'crm/{event.Format.Bezeichnung.lower()}/{name}.html')
    else:
        template = get_template(f'crm/email/{name}.html')

    return(template)


class Veranstaltung(models.Model):

    app_label = 'crm' ## necessary for admin url tag
    model_name = 'veranstaltung'
    Titel = models.TextField(max_length=200,blank=True,help_text="Offizieller Titel der Veranstaltung für Einladungen")
    ## For email subject, i.e. Streitgespräch zwischen dem Papst und Merting
    Inhalt = models.CharField(max_length=200,blank=True,null=True,help_text="Inhalt der Veranstaltung für E-Mail-Betreff und URL, z.B. Streitgespräch zwischen Merting und dem Papst") ## i.e. Streitgespräch Gauweiler + Steinbach

    notice = models.CharField("Hinweis",max_length=500,blank=True,
    null=True,help_text="Organisatorischer Hinweis, z.B. Anmeldung noch nicht möglich") ##

    Einlass = models.DateTimeField(blank=True,null=True)
    Beginn = models.DateTimeField(blank=True,null=True)
    Ende = models.DateTimeField(blank=True,null=True)
    Einladungstext = models.TextField(blank=True,help_text="Text, der als E-Mail-Einladung verschickt wird - Werte in {Klammern} werden serienbriefmäßig ersetzt.")
    # html_invitation = models.TextField(blank=True,help_text="HTML, der als E-Mail-Einladung verschickt wird - Werte in {Klammern} werden serienbriefmäßig ersetzt.")

    description = models.TextField("Beschreibung",blank=True,help_text="Text für die Anzeige auf den öffentlichen Anmeldeseiten (html benutzen)")

    ## Save function sets to default template if user has not entered text
    confirmation_text = models.TextField("Bestätigungstext",blank=True,
    help_text="Text, der als Bestätigung verschickt wird - Werte in {{Klammern}} werden ersetzt.")
    Einladung_A4 = models.FileField(blank=True,help_text='Hier soll die fertige Einladung als A4-Blatt hinkommen in der Form, in der sie an die Teilnehmer verschickt werden kann.')
    participant_list = models.FileField("Teilnehmerliste",blank=True,help_text='Hier die Teilnehmerliste nach einer Veranstaltung für Dokumentationszwecke hochladen.')

    Ordner_Cloud = models.URLField(blank=True,help_text="Order in einem externen Dateiensystem mit Dokumenten zur Veranstaltung.")
    Seite = models.URLField(blank=True,help_text="Einladungsseite, falls eine spezifische URL und nicht die automatisch generierte im Feld Anmeldungsseite benutzt werden sollte (überschreibt Anmeldungsseite).")
    site_ready = models.BooleanField("Seite startklar",default=False,help_text="Ist Seite vollständig erstellt und bereit für den aktiven Betrieb?")
    site_listed = models.BooleanField("Seite in Übersichten aufgelistet",
    default=False,
    help_text="Wenn angekreuzt, wird die Seite in Übersichten wie erasmus-stiftung.de/veranstaltungen aufgelistet.")

    video = models.CharField("Link zum Video",max_length=100,blank=True,
    help_text="Link zum Video auf externer Seite, wird in externer Übersicht eingebunden, wenn vorhanden.")

    Raum_Einladung = models.CharField(max_length=100,blank=True,help_text="Geografischer Raum, in dem die Veranstaltung stattfindet (Berlin, Frankfurt, Lüneburger Heide). Wird zu Sicherheitszwecken anstatt der Adresse oder eines kleinen Ortes angegeben.")
    Veranstaltungsort = models.CharField(max_length=100,blank=True,help_text="Name der Gaststätte, Hotel oder anderer Einrichtung")
    Veranstaltungsraum = models.CharField(max_length=100,blank=True,help_text="ggf. Raum innerhalb des Veranstaltungsortes")
    Zusatz_Adresse = models.CharField(max_length=100,blank=True)
    Straße = models.CharField(max_length=100,blank=True)
    PLZ = models.CharField(max_length=10,blank=True)
    Ort = models.CharField(max_length=100,blank=True)
    Bundesland = models.ForeignKey(Bundesland,null=True,blank=True,on_delete=models.SET_NULL)
    Vertrag_Raummiete = models.FileField(blank=True)

    Eingeladene_Personen = models.ManyToManyField(Person,blank=True)
    ## Veranstaltungsformat, e.g. Kongress, Seminar, etc.
    Format = models.ForeignKey(Format,
    on_delete=models.SET_NULL,null=True,blank=False,related_name="events")
    Maximale_Teilnehmer = models.IntegerField(null=True,blank=True,
    help_text="Maximale Anzahl der Teilnehmer eingeben, sofern diese von der Anzahl rechts (von Modul oder Format) abweicht.")
    hotel_rooms = models.IntegerField("Hotelzimmer",
    null=True,
    blank=True,help_text="Anzahl der gebuchten Hotelzimmer (EZ und DZ zusammen)")

    confirm_with_address = models.BooleanField("mit Adresse bestätigen",default=True,help_text="Wenn angekreuzt, bekommen TN eine Bestätigung unter Angabe der Adresse. Wenn nicht, muss die Adresse separat mitgeteilt werden.")
    link_active = models.BooleanField("Link aktiv",default=False,help_text="Wenn angekreuzt, ist der Link auf der Übersichtsseite zur Anmeldungseite aktiv.")

    Modul = models.ForeignKey(Modul, on_delete=models.SET_NULL,
    null=True,blank=True,
    help_text="I.e. Rhetorik 1, Islam, Kommunalpolitik 2",related_name="events")
    Bemerkungen_Sachbearbeiter = models.TextField(null=True,blank=True)

    ## Cached value for calculated value confirmed
    confirmed_cache = models.IntegerField(null=True,blank=True)
    valid_form_entries_cache = models.IntegerField(null=True,blank=True)

    Kostenstelle = models.IntegerField(null=True,blank=True)

    class Meta:
        verbose_name = _("Veranstaltung")
        verbose_name_plural = _("Veranstaltungen")

    @property
    def send_from_email(self):
        # ## Send from email entered into Format.email,
        # ## e.g. seminare@erasmus-stiftung.de for Format record "Seminar"
        # if self.Format and self.Format.email:
        #     send_from_email = self.Format.email
        # elif self.Modul and self.Modul.Format and self.Modul.Format.email:
        #     send_from_email = self.Modul.Format.email
        # else:
        #     send_from_email = "veranstaltungen@erasmus-stiftung.de"
        return("info@benaustin.de")

    def statistics(self):
        '''Return dictionary with
        quantity of entries, their booking options and status
        for use in event registrations page'''

        valid_entries = self.valid_form_entries
        bookingoptions = self.calculated_bookingoptions
        stat_dict = {"Anmeldungen":len(valid_entries)}
        ## Caching, will fall away when Gravity API no longer used
        self.valid_form_entries_cache = stat_dict["Anmeldungen"]

        ## Iterable of strings, may be replaced by non-hardcoded data!!
        statusoptions = FormEntry.Statusoptionen

        for status in statusoptions:
            stat_dict[status] = len([entry for entry in valid_entries if entry.Status == status])
        
        stat_dict["confirmed_after_confirmation"] = stat_dict["bestätigt"] + stat_dict["zu bestätigen"]

        ## Cache confirmed registrations
        self.confirmed_cache = stat_dict["bestätigt"]
        ## Save cached values
        self.save()

        bookingoptions_list =[]
        
        def option_number(status_list_item):
            return( (status_list_item[0],len(status_list_item[1]) ) )
        
        rooms_dict = {option:0 for option in statusoptions}
        for option in bookingoptions:
            status_list = [ [status, [entry for entry in valid_entries if entry.Status == status and entry.bookingoption == option] ] for status in statusoptions ]
            statuses = list(map(option_number,status_list))
            ## [('', 0), ('zu bestätigen', 0), ('bestätigt', 1), ('Warteliste', 0), ('ab
            occupants = option.roomtype.occupants
            
            for status,number in statuses:
                if occupants:
                    rooms_dict[status] += number/occupants
            
            bookingoptions_list.append( {"bookingoption":option,
            "number_entries":len([entry for entry in valid_entries if entry.bookingoption == option]),
            "statuses":statuses
            })
        
        def remove_value_spaces(dict_):
            return({k.replace(" ","_"):v for k,v in dict_.items()})
        
        
        stat_dict["bookingoptions"] = bookingoptions_list
        rooms_dict["nach_Versand"] = rooms_dict["bestätigt"] + rooms_dict["zu bestätigen"]
        rooms_dict = {x:math.ceil(y) for x,y in rooms_dict.items()}
        
        rooms_dict = remove_value_spaces(rooms_dict)
        stat_dict["rooms_dict"] = rooms_dict

        ## Replace spaces to make all keys available in template
        stat_dict = remove_value_spaces(stat_dict)
        return(stat_dict)
    

    def save(self,*args,**kw):
        '''If there is no confirmation text, set to default template.
        Create Gravity form if it does not exist, update existing form.
        '''
        if not self.confirmation_text:
            template = get_email_template(self,"confirmation")
            if template.template.source:
                self.confirmation_text = template.template.source

        super( Veranstaltung, self ).save( *args, **kw )

    @property
    def calculated_bookingoptions(self):
        '''Return QuerySet with event, format or all options
        Ordered by pk so that options are shown in the order created.
        '''
        event_options = self.bookingoptions.order_by("bookingoption_order")

        if len(event_options):
            options = event_options
        elif self.Format:
            options = self.Format.bookingoptions.order_by("bookingoption_order")
        else:
            options = BookingOption.objects.order_by("bookingoption_order")
        
        return(options.order_by("bookingoption_order"))        

    @property
    def in_past(self):
        if self.Beginn > datetime.now():
            return(True)
        else:
            return(False)

    # @property
    # def invited(self):
    #     persons_set = set([c.person for c in self.communication.filter(type=1)])
    #     for p in persons_set:
    #         if p.Familienname == None:
    #             p.Familienname = ""
    #     return(sorted(persons_set,
    #     key=lambda person: person.Familienname))

    @property
    def Bezeichnung(self):
        if self.Modul and self.Titel:
            return(f"{self.Modul}: {self.Titel}")
        elif self.Modul and not self.Titel:
            return(self.Modul.Bezeichnung)
        elif self.Titel and not self.Modul and self.Format:
            return(f"{self.Format}: {self.Titel}")
        elif self.Titel and not self.Modul:
            return(self.Titel)
        elif self.Inhalt:
            return(self.Inhalt)
        else:
            return("Veranstaltung ohne Titel oder Modul.")

    def public(self):
        '''Return True if event can be publicly advertised
        and False if not'''
        if self.Beginn > datetime.now() and not self.site_ready:
            return(False)
        ## Module and format must be public
        elif self.Modul:
            if not self.Modul.public:
                return(False)
            elif self.Modul.public:
                if self.Format and self.Format.public:
                    return(True)
                elif self.Format and not self.Format.public:
                    return(False)
        elif self.Format:
            if not self.Format.public:
                return(False)
            elif self.Modul and not self.Modul.public:
                return(False)
            else:
                return(True)
        else:
            return(False)

    def send_answers_participation(self,test=True,confirm_status_none=False):
        '''
    Send answers to all registrants based on registration status
        '''
        from crm.views import send_event_message
        json_response_list = []
        for formentry in self.FormEntries.all():
            category_set = Category.objects.filter(planned=formentry.Status)
            if category_set.exists():
                category = category_set[0]
                send_event_message(formentry,category=category)
                formentry.Status = category.completed
                formentry.save()

        return(json_response_list)

    @property
    def valid_form_entries(self):
        '''Return valid FormEntry objects (for registration counts)
        Remove duplicate form entries if first name, last name and email match)
        Remove form entries from blocked email addresses
        Papierkorb not filtered out, later made invisible in template with CSS
        Sort by Übernachtung,Status
        '''
        valid_registrants = []
        removed_duplicates = []
        registrants = self.FormEntries.all()

        for registrant in registrants:
            # if not registrant.processed:
            if registrant not in removed_duplicates:

                if registrant.Status != "Papierkorb":
                    matches = self.FormEntries.filter(Veranstaltung=self).filter(Familienname=registrant.Familienname).filter(Vorname=registrant.Vorname).filter(E_Mail=registrant.E_Mail).exclude(pk=registrant.pk)
                        ## Only adds first instance of duplicate, eliminating further ones
                    if matches: removed_duplicates.extend(matches)
                else: ## Don't look for matches if Status is Papierkorb
                    matches = False
                ## If person associated with this FormEntry is not excluded
                if not registrant.person.ausschließen:
                    ## If registration email does not have positive "blocked" value
                    if not Email.objects.exclude(blocked=False).filter(email=registrant.E_Mail).exists():
                        valid_registrants.append(registrant)

                        ## TODO: Possibly insert else clause that adds blocked registrants so as to hide them with template
                # registrant.processed = True
                # registrant.save()
            else:
                valid_registrants.append(registrant)

        criteria = OrderedDict([ ("referent",(True,False)),
        ("Status",("","zu bestätigen","bestätigt",
    "Warteliste",
    "abzusagen","abgesagt",
    "in Klärung","Teilnehmer storniert",
    "Papierkorb") ) ,
    ## TODO: Order of roomtype abbreviation can be replaced by user-editable value in BookingOption
    ("roomtype_abbreviation", ("EZ","EZ-2","EZ-1","DZ","DZ-2","DZ-1","Extern") ) ,
    ("pk",False) ])
        valid_registrants = multisort(valid_registrants,criteria)

        ## Cache number of valid form entries
        if self.valid_form_entries_cache != valid_registrants:
            self.valid_form_entries_cache = len(valid_registrants)
            self.save()
        
        ## Room partner ordering logic
        sorted_by_room_partner = [] ## Main list
        added_room_partners = [] ## Record entries added to avoid repeats
        for fe in valid_registrants:
            if fe not in added_room_partners:
                sorted_by_room_partner.append(fe)
                if fe.room_partner:
                    added_room_partners.append(fe.room_partner)
                    sorted_by_room_partner.append(fe.room_partner)
                    ## If other room partner does not have reciprocal relationship, create it...
                    if not fe.room_partner.room_partner:
                        fe.room_partner.room_partner = fe
                        fe.room_partner.save()
        valid_registrants =   sorted_by_room_partner             

        return(valid_registrants)

    @property
    def Maximale_Teilnehmer_(self):
        '''Return maximum number of participants'''
        if self.Maximale_Teilnehmer != None:
            return(self.Maximale_Teilnehmer)
        elif self.Modul != None and self.Modul.Maximale_Teilnehmer != None:
            return(self.Modul.Maximale_Teilnehmer)
        elif self.Format != None and self.Format.Maximale_Teilnehmer != None:
            return(self.Format.Maximale_Teilnehmer)
        else:
            return("-")

    def parseAnmeldungen(self):
        if self.Anmeldeformular:
            new_registrations = self.Anmeldeformular.parseAnmeldungen()
            self.statistics()
            return(new_registrations)

    def Anmeldungen(self):
        '''Return the registrations via GravityFormular as JSON objects.
        Veranstaltung.FormEntries gives records from DB
        '''
        if self.Anmeldeformular:
            from crm import gravity
            # formular = GravityFormular.objects.get(self.Anmeldeformular)
            response_json = gravity.gravity_request(query=f"entries?form_ids%5B0%5D={self.Anmeldeformular.Formular_ID}&paging%5Bpage_size%5D=500&_labels=1")
            entries = response_json['entries']
            return(entries)

    def Anzahl_Anmeldungen(self):
        '''Return the number of registrations via GravityFormular
        TODO: Remove duplicates using logic from excel_utils.eventExcel
        '''
        if self.Anmeldeformular_verlinkt != None:
            return(self.Anmeldeformular_verlinkt.entries)
        else:
            return(False) ## Replaces "Kein Anmeldeformular", text belongs in template

    @property
    def Zeitangaben_mehrtätig(self):
        '''Return time block for multi-day events with line break'''
        block = ''
        if self.Beginn != None:
            from custom_utils.localization_dicts import wochentag_dict,monat_dict
            block = f"Beginn: {wochentag_dict[self.Beginn.weekday()]}{self.Beginn.strftime(', den %d.%m.%Y um %H:%M Uhr')}"
            if self.Ende != None:
                block = '\n'.join([block,f"Ende: {wochentag_dict[self.Ende.weekday()]}{self.Ende.strftime(', den %d.%m.%Y um %H:%M Uhr')}"])
        return(block)

    @property
    def Zeitangaben_mehrtätig_HTML(self):
        '''Return time block for multi-day events with HTML dividing element for use in registration form.'''
        block = ''
        if self.Beginn != None:
            from custom_utils.localization_dicts import wochentag_dict,monat_dict
            block = f"Beginn: {wochentag_dict[self.Beginn.weekday()]}{self.Beginn.strftime(', den %d.%m.%Y um %H:%M Uhr')}"
            if self.Ende != None:
                block = '</br>'.join([block,f"Ende: {wochentag_dict[self.Ende.weekday()]}{self.Ende.strftime(', den %d.%m.%Y um %H:%M Uhr')}"])
        return(block)


    @property
    def Zeitangaben(self):
        '''Return block of type:
        Sonntag, den 02. Juni 2019
        Einlaß um 18.30 Uhr
        Beginn um 19:00 Uhr
        Ende um 22:00 Uhr'''
        block = ''
        if self.Beginn != None:
            ## If no end is given or the event ends on the same day it begins...
            if not self.Ende or self.Beginn.day == self.Ende.day:
                from custom_utils.localization_dicts import wochentag_dict,monat_dict
                block = f"{wochentag_dict[self.Beginn.weekday()]}{self.Beginn.strftime(', den %d.')} {monat_dict[self.Beginn.month]} {self.Beginn.year}"
                if self.Einlass != None:
                    block = "\n".join([block,self.Einlass.strftime('Einlaß um %H:%M Uhr')])
                block = "\n".join([block,self.Beginn.strftime('Beginn um %H:%M Uhr')])
                if self.Ende != None:
                    block = '\n'.join([block,self.Ende.strftime('Ende um %H:%M Uhr')])
            else:
                block = self.Zeitangaben_mehrtätig

        return(block)

    @property
    def Zeitangaben_HTML(self):
        '''Return block of type:
        Sonntag, den 02. Juni 2019
        Einlaß um 18.30 Uhr
        Beginn um 19:00 Uhr
        Ende um 22:00 Uhr'''
        block = ''
        if self.Beginn != None:
            ## If no end is given or the event ends on the same day it begins...
            if not self.Ende or self.Beginn.day == self.Ende.day:
                from custom_utils.localization_dicts import wochentag_dict,monat_dict
                block = f"{wochentag_dict[self.Beginn.weekday()]}{self.Beginn.strftime(', den %d.')} {monat_dict[self.Beginn.month]} {self.Beginn.year}"
                if self.Einlass != None:
                    block = "</br>".join([block,self.Einlass.strftime('Einlaß um %H:%M Uhr')])
                block = "</br>".join([block,self.Beginn.strftime('Beginn um %H:%M Uhr')])
                if self.Ende != None:
                    block = '</br>'.join([block,self.Ende.strftime('Ende um %H:%M Uhr')])
            else:
                block = self.Zeitangaben_mehrtätig_HTML

        return(block)


    @property
    def Datum(self):
        '''Date or date range on one line: 03.01.-05.01.2020'''
        if not self.Ende or self.Beginn.day == self.Ende.day:
            datestring = self.Beginn.strftime('%d.%m.%Y')
        else:
            ## Date range for multi-day events
            datestring = f"{self.Beginn.strftime('%d.%m.')}-{self.Ende.strftime('%d.%m.%Y')}"
        return(datestring)

    @property
    def Anmeldungsseite(self):
        if self.Seite in ("",None) and self.pk != None:
            from django.urls import reverse
            from crm.views import register
            register_url = reverse(register,kwargs={"event_id":self.pk})
            return("https://intranet.erasmus-stiftung.de{}".format(register_url))

        #     event_url = hashlib.sha224(f"{SECRET_KEY}{self.pk}".encode()).hexdigest()[:4].lower()
        #     return(f"https://erasmus-stiftung.de/event/{event_url}")
        else:
            return(self.Seite)



    @property
    def Adresse_eine_Zeile(self):
        adresse = f"{self.Straße}, {self.PLZ} {self.Ort}"
        if self.Zusatz_Adresse:
            adresse = f"{self.Zusatz_Adresse}, {adresse}"
        return(adresse)

    def __str__(self):
        if self.Beginn:
            begin_string = self.Beginn.strftime('%d.%m.%y')
        else:
            begin_string = "keine Startzeit"
        return(f"{begin_string} – {self.Raum_Einladung}: {self.Bezeichnung}")


class GravityFormular(models.Model):
    Formular_ID = models.IntegerField(blank=True,null=False,unique=True) ## The ID originating from Gravity used for API calls
    title = models.CharField(max_length=1000,blank=True,unique=False) ## Gravity title (may be changed as long as ID is preserved, contains Veranstaltung pk because it is exported by jsonGravity)
    entries = models.IntegerField(blank=True,null=False)
    _Veranstaltung = models.OneToOneField(Veranstaltung, ## TODO: crm.GravityFormular._Veranstaltung: (fields.W342) Setting unique=True on a ForeignKey has the same effect as using a OneToOneField.
#        HINT: ForeignKey(unique=True) is usually better served by a OneToOneField.
    verbose_name='Veranstaltungen',
    on_delete=models.SET_NULL,
    null=True,related_name="Anmeldeformular_verlinkt")

    @property
    def Veranstaltung(self):
        '''Return Veranstaltung object connected with this form'''
        if self._Veranstaltung != None: ## If a value is already saved in internal variable

            return(self._Veranstaltung) ## Assume it is unchanged, return Veranstaltung value
        else: ## If value is none...
            if " " in self.title:
                v_id = self.title.split(" ")[0] ## By convention, Veranstaltung id is at beginning of title
                if v_id.isdigit() and Veranstaltung.objects.filter(pk=int(v_id)).exists(): ## Ensures that event with this pk exists before matching
                    self._Veranstaltung = Veranstaltung.objects.get(pk=int(v_id))
                    self.save() ## Save to internal variable
                    return(self.Veranstaltung) ## Return newly found Veranstaltung object

    class Meta:
        verbose_name = _("Gravity-Formular")
        verbose_name_plural = _("Gravity-Formulare")

    def Anmeldungen(self):
        '''Return the registrations via GravityFormular'''

        response_json = gravity.gravity_request(query=f"entries?form_ids%5B0%5D={self.Formular_ID}&paging%5Bpage_size%5D=500&_labels=1")
        entries = response_json['entries']
        entries.sort(key=lambda entry:entry["date_created"])
        return(entries)

    def parseAnmeldungen(self):
        '''Convert field names, save the JSON returned by Gravity api
        as FormEntry record'''

        json_entries = self.Anmeldungen()
        new_entries = [] ## List of FormEntry objects

        ## model_fields has format: ['id', 'Anrede', 'Titel', 'Vorname'...
        model_fields = [field.name for field in FormEntry._meta.get_fields() if hasattr(field,"name")]
        for json_entry in json_entries:
            if not FormEntry.objects.filter(entry_id=int(json_entry["id"])).exists():
                create_dict = {"JSON":json_entry,
                "entry_id":int(json_entry["id"]),
                "Veranstaltung":self.Veranstaltung,
                "GravityFormular":self,
                }
                ## Transfer field values "user_agent","source_url","date_created","date_updated","form_id"
                for x in json_entry:
                    if x in model_fields:
                        if json_entry[x] == "None":
                            json_entry[x] = None
                        create_dict[x] = json_entry[x]
                ## Transfer labelled field values
                ## json_entry["_labels"] has format {'9': 'Familienname', '1': 'Vorname'
                for number,label in json_entry["_labels"].items():
                    ## json_entry["_labels"] has format : {'9': 'Familienname', '1': 'Vorname', '10': 'Anrede', '11': 'Titel', '2': 'E-Mail', '20': 'Mobiltelefon', '23': 'Anschrift', '24': 'Anschrift Zusatz',
                    gravity_django_convert = {"Platz für Ihre Anmerkungen":"Anmerkungen",
                    "E-Mail":"E_Mail",
                    "Name Zweitperson Doppelzimmer":"Zweitperson_Zimmer",
                    "Anschrift":"Straße",
                    'Anschrift Zusatz':"Zusatz_Adresse",
                    'Übernachtung':"bookingoption"
                    }

                    if type(label) != dict:
                        if label in gravity_django_convert:
                            label = gravity_django_convert[label]
                    assert type(number) == str
                    if number in json_entry and label in model_fields:
                        create_dict[label] = json_entry[number]
                
                ## Convert Übernachtung text to BookingOption object
                if "bookingoption" in create_dict:
                    create_dict["bookingoption"] = self.Veranstaltung.calculated_bookingoptions.get(formvalue=create_dict["bookingoption"])

                ## Convert Anrede text string ("Herr/Frau") to Anrede object
                create_dict["Anrede"] = Geschlecht.objects.get(Herr_Frau=create_dict["Anrede"])
                if not FormEntry.objects.filter(entry_id=int(json_entry["id"])).exists():
                    # FormEntry with id {json_entry['id']} does not exist, creating with dict create_dict"
                    new_entry = FormEntry.objects.create(**create_dict)
                    new_entries.append(new_entry)
        return new_entries


    def __str__(self):
        if self._Veranstaltung != None:
            return(f"{self.Formular_ID} – {self.title} – {self._Veranstaltung.Titel}") ##
        else:
            return(f"{self.Formular_ID} – {self.title}")

class FormEntry(models.Model):
    '''Single entry in a form
    Class created for GravityFormular, but should remain flexible in case as it must be used independently of Gravity
    '''
    app_label = "crm"
    model_name = "formentry"
    Anrede = models.ForeignKey(Geschlecht, on_delete=models.CASCADE,null=True)
    Titel = models.CharField(max_length=50,blank=True,null=True)
    Vorname = models.CharField(max_length=100,blank=True)
    Familienname = models.CharField(max_length=100,blank=True)
    E_Mail = models.EmailField("E-Mail",max_length=100,blank=True,null=True)

    ## Adress fields not used in all forms
    Titel_nachgestellt = models.CharField(max_length=20,blank=True,null=True) ## Not used in standard forms
    Zusatz_Adresse = models.CharField(max_length=100,blank=True,null=True)
    Straße = models.CharField(max_length=100,blank=True,null=True)
    PLZ = models.CharField(max_length=10,blank=True,null=True)
    Ort = models.CharField(max_length=100,blank=True,null=True)
    ## Spezifisch für Seminare
    Mobiltelefon = models.CharField(max_length=150,blank=True,null=True)
    Einladungscode = models.CharField(max_length=50,blank=True,null=True)
    Funktion = models.CharField(max_length=100,blank=True,null=True)
    Institution = models.CharField(max_length=200,blank=True,null=True)
    ip = models.CharField(max_length=500,blank=True,null=True)
    Anmerkungen = models.TextField(blank=True,null=True)
    Anmerkungen_Sachbearbeiter = models.TextField(blank=True,null=True)
    # Übernachtungsoptionen = ("EZ","DZ","Extern","")
    # Übernachtung = models.CharField(max_length=150,
    # blank=True,
    # choices=[(x,x) for x in Übernachtungsoptionen])
    ## If the participant registers a second person for the room, name (not split into first and last)
    Zweitperson_Zimmer = models.CharField(max_length=150,blank=True,null=True,help_text="Die Angabe des Teilnehmers aus dem Formular in Textform – soll nicht durch Sachbearbeiter geändert werden. Stattdessen das Auswahlfeld in der Spalte 'Übernachtung' benutzen, um Zimmerpartner für interne Zwecke festzulegen.")
    room_partner = models.ForeignKey("FormEntry",
    verbose_name="Zweitperson im Zimmer",on_delete=models.CASCADE,
    null=True,blank=True)
    ## Original form JSON from Gravity
    ## To evaluate JSON....
    ## import ast
    ## ast.literal_eval(self.JSON)
    JSON = models.TextField(max_length=10000,null=False)
    GravityFormular = models.ForeignKey(GravityFormular,
    on_delete=models.CASCADE,
    null=True)
    Veranstaltung = models.ForeignKey(Veranstaltung,
    on_delete=models.CASCADE,
    null=False,related_name='FormEntries')

    Statusoptionen = ((""),("zu bestätigen"),("bestätigt"),
    ("Warteliste"),
    ("abzusagen"),("abgesagt"),
    ("in Klärung"),("Teilnehmer storniert"),
    ("Papierkorb"))

    Status = models.CharField(max_length=100,blank=True,null=True,choices=[(x,x) for x in Statusoptionen])

    ## Imported from gravity
    user_agent = models.CharField(max_length=500,blank=True,null=True)
    source_url = models.CharField(max_length=1000,blank=True,null=True)
    date_created = models.DateTimeField(verbose_name="eingegangen",null=True,blank=True)
    date_updated = models.DateTimeField(null=True,blank=True)
    entry_id = models.IntegerField(null=True,unique=True)## In JSON simply "id"
    form_id = models.IntegerField(null=True,blank=True)## Redundant, should be identical with GravityFormular.Formular_ID

    _person = models.ForeignKey(
        Person,
        help_text="Die Person, der diese Anmeldung automatisch zugeordnet wurde (oder erst aufgrund dieser Anmeldung hinterlegt wurde).",
        on_delete=models.SET_NULL,null=True,
        blank=True,related_name="formentries")
    
    
    referent = models.BooleanField(default=False,verbose_name="Referent",
    help_text="Nimmt diese Person als Referent an der Veranstaltung teil?")

    ## 'date_created': '2019-04-03 18:36:10', 'date_updated'
    ## Internal attributes of FormEntry object to be excluded from JSON and templates
    exclude_attributes = ("_Veranstaltung_cache","_state","_Anrede_cache","_GravityFormular_cache")
    # processed = models.BooleanField()

    ## Widget must limit choices to Veranstaltung.calculated_bookingoptions
    bookingoption = models.ForeignKey("BookingOption",
    related_name="formentries",
    on_delete=models.CASCADE,
    verbose_name="Buchungsoption",null=True,
    default=None,blank=True)

    invitation_code = models.ForeignKey("InvitationCode",
    verbose_name="Einladungscode",
    on_delete=models.SET_DEFAULT,
    default=None,
    related_name="formentries",
    null=True,blank=True)

    @property
    def _start(self):
        if not self.bookingoption or not self.bookingoption.start:
            if self.Veranstaltung.Beginn:
                return(self.Veranstaltung.Beginn)
        else:
            return(self.bookingoption.start)

    @property
    def _end(self):
        if not self.bookingoption or not self.bookingoption.end:
            if self.Veranstaltung.Ende:
                return(self.Veranstaltung.Ende)
        else:
            return(self.bookingoption.end)
    
    @property
    def von_bis(self):
        ## For custom Excel table will all data about registrations
        if self._start and self._end:
            return("{0} – {1}".format(self._start.strftime('%d.%m.%Y'),
            self._end.strftime('%d.%m.%Y')))
        elif self._start and not self._end:
            return(self._start.strftime('%d.%m.%Y') + " – ?")
        elif self._end and not self._start:
            return("? – " + self._start.strftime('%d.%m.%Y'))

    @property
    def Anzahl_ÜN(self):
        return(self.nights)

    @property
    def nights(self):
        '''Number of overnight stays'''

        def nights(start,end):
            ## Generic function for determining number of nights
            if start.day == end.day:
                return(0) ## If on same day, no nights
            else:
                hours = (end-start).total_seconds() / 3600
                nights_ = math.ceil(hours/24)
                return(nights_)

        if self.bookingoption and self.bookingoption.roomtype:
            ## If selected room type has no occupants, no nights
            if self.bookingoption.roomtype.occupants == 0:
                return(0)
            elif self.bookingoption.start and self.bookingoption.end:
                return(nights(self.bookingoption.start,self.bookingoption.end))
            elif self.bookingoption.nights:
                return(self.bookingoption.nights)
        else:
            v = self.Veranstaltung
            if v.Beginn and v.Ende:
                return(nights(v.Beginn,v.Ende))

    @property
    def event(self):
        return(self.Veranstaltung)

    @property
    def Eingang(self):
        '''Formatted record creation time for display on registrations page'''
        if self.date_created != None:
            return(self.date_created.strftime("%d.%m.%Y %H:%M"))
        else:
            return("Kein Datum")

    @property
    def Rolle(self):
        if self.referent:
            return("Referent")
        else:
            return("Teilnehmer")

    @property
    def Zimmerpartner(self):
        '''Stringify ForeignKey room_partner for export in Excel'''
        if self.room_partner != None:
            return(str(self.room_partner))
        else:
            return("")

    def save(self,*args,**kw):
        '''Create a Person record
        for FormEntry via property whenever saved'''
        super( FormEntry, self ).save( *args, **kw )
        self.person

    @property
    def roomtype_abbreviation(self):
        '''Returns string or None for multisort in Veranstaltung.valid_form_entries'''
        if self.bookingoption and self.bookingoption.roomtype:
            return(self.bookingoption.roomtype.abbreviation)
        else:
            return(None)

    def Übernachtung_Text(self):
        if self.bookingoption:
            if self.bookingoption.roomtype and self.bookingoption.roomtype.long_text:
                return(self.bookingoption.roomtype.long_text)
            elif not self.bookingoption.roomtype and self.bookingoption.formvalue:
                return(self.bookingoption.formvalue)
            elif self.bookingoption.abbreviation:
                return(self.bookingoption.abbreviation)
            else:
                return("")
        else:
            return("")

    def Betrag(self):
        '''Return sum to be paid by participant for confirmation.'''
    
        if self.bookingoption:
            return(f"{self.bookingoption.price_participant} €".replace(".",","))
        else:
            return(None)

    def initialize_event(self,event):
        '''Set temporary, non-saved attributes
        Invitiation code is required by send function because it is a template variable
        Create params link although possibly not needed'''
        return({"einladungscode":self.person._einladungscode(event),"params_link":
        self.person._params_link(event)})

    def Verwendungszweck(self):
        '''Human-readable payment purpose,
        later to be replaced by DATEV (max. 8 characters, not human-readable)
        '''
        if self.Veranstaltung:
            if self.Veranstaltung.Kostenstelle:
                return(str(self.Veranstaltung.Kostenstelle) + "-" + str(self.id))
            else:
                return("-" + str(self.id))
        else:
            return(f"Fehler: Formulareintrag hat keine zugeordnete Veranstaltung\nPK:{self.pk}\n{self}")

    @property
    def person(self):
        '''Match form entry to Person object
        TODO: Requires manual correction of names with incorrect capitalization, may mix up "von" and other titles
        '''
        def new_person_data():
            person_field_names = [field.name for field in Person._meta.get_fields() if field.name not in ("pk","id") and hasattr(self,field.name)]
            person_data = {field.name:getattr(self,field.name)
            for field in self._meta.get_fields() if field.name in person_field_names}
            return(person_data)

        if self._person == None:

            if self.E_Mail != None:
                ## Start by matching first + last name and email
                name_match = Person.objects.filter(Vorname=self.Vorname,
                Familienname__icontains=self.Familienname,
                E_Mail__icontains=self.E_Mail)
                if len(name_match) == 1:
                    self._person = name_match[0]
                ## TODO: add invitation code logic

            ## If email address is blocked,
            ## connect FormEntry to blocked person or create new blocked person
            if Email.objects.filter(email=self.E_Mail).exists():
                email_matches = Email.objects.filter(email=self.E_Mail)
                for email in email_matches:
                    if email.blocked:
                        if email.person:
                            self._person = email.person
                            if not self._person.ausschließen:
                                self._person.ausschließen = datetime.today()
                            break
                        else: ## Create person record with today as exclusion date
                            person_data = new_person_data()
                            person_data["ausschließen"] = datetime.today()
                            self._person = Person.objects.create(**person_data)
                            break
            

            ## Otherwise create new person and save.
            if self._person == None:
                ## If none of the searches match, create new Person object
                person_data = new_person_data()
                self._person = Person.objects.create(**person_data)

            self.save()
        return(self._person)

    def __str__(self):
        return(f"{self.Familienname}, {self.Vorname}")

    def JSON_dict(self):
        import copy
        from django.core.serializers.json import DjangoJSONEncoder
        json_dict = copy.copy(self.__dict__)

        for x in self.exclude_attributes:
            if x in json_dict:
                del json_dict[x]
        json_dict["Anrede"] = self.Anrede.Herr_Frau

        return json.dumps(
  json_dict,
  sort_keys=True,
  indent=1,
  cls=DjangoJSONEncoder
)
        # return(json.dumps(json_dict))
        # return(self.__dict__)

    class Meta:
        verbose_name = _("Formulareintrag")
        verbose_name_plural = _("Formulareinträge")

    @property
    def Mobilnummer(self):
        return(self.Mobiltelefon)

class Consent(models.Model):
    '''Consent to terms and services,
    GDPR'''
    date_created = models.DateTimeField("erteilt",auto_now_add=True,null=False)
    ## Text should be saved when consent given and not changed
    text = models.TextField(max_length=500,blank=False,null=False)
    ## Linked to FormEntry, not Person to avoid mixing consent in case of incorrect data merges
    formentry = models.ForeignKey(FormEntry, on_delete=models.CASCADE, null=True)
    
    ## Template saved on creation to allow grouping consent records
    ## by foreign key
    dbtemplate = models.ForeignKey("DbTemplate", on_delete=models.SET_NULL, null=True,
    help_text="Vorlage, die zur Erzeugung des Textes benutzt wurde.")


class Communication(models.Model):
    Anrede = models.ForeignKey(Geschlecht, on_delete=models.CASCADE,null=True)

    ## Normed field to replace type
    category = models.ForeignKey("Category", on_delete=models.CASCADE,null=True)

    Titel = models.CharField(max_length=50,blank=True,)
    Vorname = models.CharField(max_length=100,blank=True)
    Familienname = models.CharField(max_length=100,blank=True)
    subject = models.CharField("Betreff",max_length=5000,blank=True,null=True)
    message = models.CharField("Inhalt",max_length=5000,blank=True,null=True)
    sent_on = models.DateTimeField("Zeitpunkt Versand",auto_now_add=True,null=True)
    person = models.ForeignKey(Person,on_delete=models.CASCADE,null=True,verbose_name="Person",related_name="communication")
    formentry = models.ForeignKey(FormEntry,on_delete=models.CASCADE,null=True,verbose_name="Formulareintrag")
    event = models.ForeignKey(Veranstaltung,on_delete=models.CASCADE,null=True,blank=True,related_name="communication")
    E_Mail = models.EmailField(max_length=100,blank=True)
    answered = models.BooleanField("beantwortet",default=False)

    medium_CHOICES = ((1,_("E-Mail")),
    (2,_("Telefon")),
    (3,_("Brief")),
    (4,_("persönlich")),
    (5,_("sonstiges"))
    )
    medium = models.IntegerField("Kommunikationsmittel",null=False,blank=True,choices=medium_CHOICES)

    # ## To be replaced by normed field category
    # type_CHOICES = ((1,_("Einladung")),
    # (2,_("Eingangsbestätigung Anmeldung")), # confirmation of received registration
    # (3,_("Teilnahmebestätigung")), # confirmation of participation
    # (4,_("Absage an TN")),
    # (5,_("Storno durch TN")),
    # (6,_("sonstiges"))
    # )
    # type = models.IntegerField("Art der Kommunikation",null=False,blank=False,choices=type_CHOICES)

    class Meta:
        verbose_name = _("Kommunikation")
        verbose_name_plural = _("Kommunikation")
    
    def save(self,*args,**kw):
        if not self.medium and self.E_Mail:
            self.medium = 1
        super( Communication, self ).save( *args, **kw )


class Rechnung(models.Model):
    # Rechnungsnsnummer_intern = models.CharField(max_length=100,blank=True,null=True)
    Rechnungsnsnummer_extern = models.CharField(max_length=100,blank=True,null=True) ## Lower bound of Funktion.Nr_Funktion in this Fachgruppe
    Dienstleister = models.CharField(max_length=500,blank=True)
    Gegenstand = models.CharField(max_length=500,blank=True)
    Digitale_Rechnung = models.FileField(blank=True,
    help_text='Rechnung hier hochladen')

    Rechnungsdatum = models.DateField(auto_now_add=True,null=True,blank=True)
    Rechnungsbetrag = models.DecimalField(max_digits=10, decimal_places=2,blank=True,null=True)
    an_Buchhaltung_weitergeleitet = models.DateField(auto_now_add=False,null=True,blank=True)
    Datum_beglichen = models.DateField(auto_now_add=False,null=True,blank=True)
    ## Higher-level category containing number of Funktionen within a number range
    Veranstaltung = models.ForeignKey(Veranstaltung,
    on_delete=models.DO_NOTHING,
    null=False,related_name='Rechnungen')
    Bemerkungen_Sachbearbeiter = models.TextField(null=True,blank=True)

    class Meta:
        verbose_name = _("Rechnung")
        verbose_name_plural = _("Rechnungen")

    def __str__(self):
        return(f"{self.Rechnungsdatum} / {self.Rechnungsbetrag} / {self.Gegenstand} / {self.Dienstleister})") ##

class PersonFunction(models.Model):
    model_name = "personfunction"
    Person = models.ForeignKey(Person,verbose_name='Person',
    on_delete=models.CASCADE)
    Funktion = models.ForeignKey(Funktion,verbose_name='Funktion',
    on_delete=models.CASCADE,null=False)

    Fachgruppe = models.ForeignKey(Fachgruppe,verbose_name='Fachgruppe',
    on_delete=models.SET_NULL,null=True,blank=True)

    Bundesland = models.ForeignKey(Bundesland,verbose_name='Bundesland',
    on_delete=models.SET_NULL,null=True,blank=True)

    Bemerkungen_Sachbearbeiter = models.TextField(null=True,blank=True)
    Kreis = models.ForeignKey(Kreis, on_delete=models.SET_NULL,null=True,blank=True)

    # ## SharePoint throwaway fields for import...
    # ID_FunktionId = models.IntegerField(null=True,blank=True)
    # ID_PersonId = models.IntegerField(null=True,blank=True)

    class Meta:
        verbose_name = _("Funktion einer Person")
        verbose_name_plural = _("Funktionen von Personen")

    @property
    def Tel1(self):
        return(self.Person.Tel1)
    @property
    def Tel2(self):
        return(self.Person.Tel2)

    @property
    def Familienname(self):
        return(self.Person.Familienname)

    def save(self,*args,**kw):
        '''Cache Fachgruppe and Bundesland for sorting when saving'''
        self.cache_Bundesland()
        if self.Funktion:
            self.Fachgruppe = self.Funktion.Fachgruppe
        if self.Kreis:
            self.Bundesland = self.Kreis.Bundesland
        super( PersonFunction, self ).save( *args, **kw )

    def __str__(self):
        return(f"{self.Person}: {self.Funktion}")

    def cache_Bundesland(self):
        from crm.utility_routines import postcode_to_Bundesland
        if not self.Bundesland:
            if self.Person and self.Person.PLZ not in ("",None) and "-" not in self.Person.PLZ:
                self.Bundesland = postcode_to_Bundesland(self.Person.PLZ)

class Email(models.Model):
    email = models.EmailField(max_length=254)
    person = models.ForeignKey(Person,on_delete=models.CASCADE,
    verbose_name="Person",related_name="emails")
    Bemerkungen_Sachbearbeiter = models.TextField(null=True,blank=True)
    aktiv = models.BooleanField(default=True)
    blocked = models.BooleanField(default=False)
    class Meta:
        verbose_name = _("E-Mail-Adresse")
        verbose_name_plural = _("E-Mail-Adressen")

    def __str__(self):
        return(f"{self.email}: {self.person}")

class Group(models.Model):
    name = models.CharField("Bezeichnung",max_length=150,blank=True,null=True)
    priorities = models.ManyToManyField(Priorität,blank=True)
    regions = models.ManyToManyField(Bundesland,blank=True)
    functions = models.ManyToManyField(Funktion,blank=True)
    Fachgruppen = models.ManyToManyField(Fachgruppe,blank=True)
    persons = models.ManyToManyField(Person,blank=True)
    groups = models.ManyToManyField("self",symmetrical=False,blank=True)
    modules = models.ManyToManyField(Modul,blank=True,help_text="Personen, die sich für frühere Veranstaltungen dieser Art anmeldeten.")

    def __str__(self):
        return(str(self.name))

    def members(self):
        members = []
        functions = self.functions.all()
        priorities = self.priorities.all()
        regions = [r.pk for r in self.regions.all()]
        modules = self.modules.all()
        Fachgruppen = self.Fachgruppen.all()

        ## If no functions, modules or Fachgruppen, get all members of priority group
        if not functions and not modules and not Fachgruppen:
            for priority in priorities:
                members.extend(Person.objects.filter(Priorität=priority))

        for module in self.modules.all():
            members.extend(module.all_registrants)
        
        if functions:
            ## Get all people with function (region filtering takes place later)
            for function in functions:
                roles = PersonFunction.objects.filter(Funktion=function)
                persons = [role.Person for role in roles]
                members.extend(persons)

        ## Get people whose function does not contain a region, but who have a the function and are themselves in the region
            for bl in regions:
                for f in functions:
                    members.extend([pf.Person for pf in PersonFunction.objects.filter(Person__Bundesland=bl).filter(Funktion=f)])


        ## Additionally restrictive sorting by region
        if len(regions) > 0:
            members = [member for member in members if member.Bundesland and member.Bundesland.pk in regions]
        
        ## Additionally restrictive sorting by priority
        if len(priorities) > 0:
            members = [member for member in members if member.Priorität in priorities]

        ## Filter out blocked persons
        members = [member for member in members if not member.ausschließen and ( (member.Priorität and member.Priorität.pk != 1)  or not member.Priorität)] ## pk 1 is the category for excluded persons

        ## Members of other groups are not filtered by the same criteria.
        for group in self.groups.all():
            if group != self and self not in self.groups.all(): ## Prevents infinite recursion crash with groups that contain themselves
                members.extend(group.members())


        ## Remove duplicates, sort by last name
        members = list(set(members))
        members.sort(key=lambda person:str(person))
        return(members)

    class Meta:
        verbose_name = _("Gruppe")
        verbose_name_plural = _("Gruppen")

class RoomType(models.Model):
    abbreviation = models.CharField("Kürzel",help_text="EZ, DZ oder Extern",max_length=20)
    long_text = models.CharField("volle Beschreibung",help_text="i.e. Übernachtung im Einzelzimmer incl. Frühstück",max_length=250)
    occupants = models.IntegerField("Gäste",help_text="Anzahl der Gäste im Zimmer",null=False,blank=False)
        # "EZ":"Übernachtung im Einzelzimmer incl. Frühstück",
        # "DZ":"Übernachtung im Doppelzimmer incl. Frühstück",
        # "Extern":"Teilnahme ohne Übernachtung"}
    def __str__(self):
        return(f"{self.abbreviation}: {self.long_text}")

from adminsortable.models import SortableMixin,SortableForeignKey
class BookingOption(SortableMixin):

    ## Must be unique for this event
    abbreviation = models.CharField("Kürzel",
    max_length=20,
    help_text="Kennzeichnung in der Statistik auf der Anmeldungsseite (EZ, DZ-1 oder Extern)")

    ## Single room, double room, external participant
    roomtype = models.ForeignKey(RoomType,null=True,
    on_delete=models.CASCADE,
    blank=False,
    verbose_name="EZ/DZ/Extern",
    help_text="Diese Auswahl bedingt die Anzahl der Teilnehmer, die mit einer Buchung verbunden sind."
    )
    bookingoption_order = models.PositiveIntegerField("Reihenfolge",
    default=0, editable=False, db_index=True)

    # ## Always None/Null if RoomBooking is an option and not a specific booking
    # formentry = models.ForeignKey(FormEntry,
    # related_name="bookingoptions",
    # on_delete=models.CASCADE,
    # verbose_name="Formulareintrag",null=True,blank=True)

    ## Used for event options
    event = models.ForeignKey(Veranstaltung,
    null=True,blank=True,
    on_delete=models.CASCADE,
    verbose_name="Veranstaltung",
    related_name="bookingoptions"
    )

    ## Used for format options
    format = models.ForeignKey(Format,
    null=True,blank=True,
    on_delete=models.SET_NULL,
    verbose_name="Format",
    related_name="bookingoptions"
    )

    ## Price shown to participant
    price_participant = models.DecimalField("Preis für Teilnehmer", max_digits=7, decimal_places=2)

    ## In use for displayed values
    formvalue = models.CharField("angezeigter Text",
    max_length=250,null=True,blank=True,
    help_text="Dieser Wert wird dem externen Benutzer auf dem Anmeldeformular angezeigt. Bitte auf Übereinstimmung mit anderen Angaben prüfen."
    )

    ## Start and end time (time values left at 00:00 if unknown)
    start = models.DateTimeField("Zeitpunkt einchecken",
    help_text="Beginn dieser Buchungsoption, falls abweichend von den Daten der Veranstaltung",
    null=True,blank=True)
    end = models.DateTimeField("Zeitpunkt auschecken",
    help_text="Beginn dieser Buchungsoption, falls abweichend von den Daten der Veranstaltung",
    null=True,blank=True)

    ## Can be calculated or supplied without checkin/checkout
    nights = models.IntegerField("Übernachtungen",null=True,blank=True)

    public = models.BooleanField("Öffentlich einsehbar",
    default=True,null=False,
    help_text="Wenn angekreuzt, sehen externe Teilnehmer diese Buchungsoption auf der Anmeldungsseite.")

    class Meta:
        verbose_name = "Buchungsoptionen"
        verbose_name_plural = "Buchungsoptionen"
        ordering = ["bookingoption_order"]

    def __str__(self):
        if self.formvalue:
            return(self.formvalue)
        elif self.abbreviation:
            return(self.abbreviation)
        else:
            return("")

def standard_templates(obj):
    content_type = ContentType.objects.get_for_model(obj)
    
    connections = TemplateConnection.objects.filter(content_model=content_type).order_by("template__dbtemplate_order")
    templates = [tc.template for tc in connections]
    return(templates)

def fallback_templates(content_type,templates_list=[]):
    content_type_connections = TemplateConnection.objects.filter(content_model=content_type)

    if len(content_type_connections) > 0:
        templates_list.extend([tc.template for tc in content_type_connections])
    return(templates_list)

def get_object_templates(o=None, ## Django record object
initial_content_type=False, ## Argument only passed to function by itself during recursion
templates_list=[], ## List of templates passed through recursions
category=False
): 
    '''Given an object, get all associated templates (or specific templates)
    No content type as arg on first recursion,
    content type is used to pass original object content type
    for further recursions with objects of parent instances.

    Object changes in each recursion, initial_content_type stays the same.

    Parameters:

    o: Record from any model

    initial_content_type (ContentType): Content type in template (i.e. FormEntry for form confirmation),
    not used in first iteration / passed by other functions

    '''
    iteration_content_type = ContentType.objects.get_for_model(o)
    if not initial_content_type: ## First interation only
        templates_list=[] ## Reset list to empty to prevent list from repeating itself
        initial_content_type = iteration_content_type

## 1. check for object-associated templates via TemplateConnection generic relationship
    ## Templates connected to this specific object
    object_specific_connections = TemplateConnection.objects.filter(content_type=iteration_content_type).filter(object_id=o.pk)
    if category:
        object_specific_connections = object_specific_connections.filter(template__category=category)
    if object_specific_connections:
        templates_list.extend([tc.template for tc in object_specific_connections])
        # return(templates_list)

## 2. check for parent models using Inheritance and repeat step 2. on parents until template found        
        ## Assumes that there is only one Inheritance object with this object as a child
    child_in_inheritance = list(ContentType.objects.get_for_model(o).inheritance_child.all())
    assert len(child_in_inheritance) in (1,0)
    if len(child_in_inheritance) == 1:
        child_in_inheritance[0]
        parent_model = child_in_inheritance[0].parent_model
        assert type(parent_model) == ContentType
        
        for field in type(o)._meta.fields:
            if field.related_model != None:
                field_content_type = ContentType.objects.get_for_model(field.related_model)
                if field_content_type == parent_model:
                    inheritance_field = field
                    break

        ## Get value of ForeignKey field of parent
        parent_instance = getattr(o,inheritance_field.name)
        if parent_instance:
            templates_list = get_object_templates(o=parent_instance,
            initial_content_type=initial_content_type,
            templates_list=templates_list,
            category=category
            )
            return(templates_list)
                
    ## If no specific templates have been found and recursion hasn't been triggered by
    ## Inheritance, fall back on templates without a connection to a specific record.
    # return(fallback_templates(initial_content_type,templates_list=templates_list))
    return(templates_list)

class InvitationCode(models.Model):
    '''Code to be entered in registration form'''

    ## Code may be linked to a person
    person = models.ForeignKey(Person,
    verbose_name="Person",
    on_delete=models.CASCADE,
    null=True,blank=True)

    event = models.ForeignKey(Veranstaltung,
    verbose_name="Veranstaltung",
    on_delete=models.CASCADE,
    related_name="invitation_codes",
    null=True,blank=True) ## Can be null to allow codes for repeated use

    text = models.CharField("Text",max_length=50,
    blank=False,null=False)

    registrations_allowed = models.IntegerField(verbose_name="erlaubte Anmeldungen",
    blank=True,null=True,default=0,
    help_text="Anzahl der Anmeldungen, die mit diesem Code möglich sind. 0 = unbegrenzt.")

    class Meta:
        unique_together = [["event","person"]]
        verbose_name_plural = "Einladungscodes"

    def __str__(self):
        return(f"Einladungscode {self.text}: {self.event}")

class Inheritance(models.Model):
    '''Directional relationship between two ContentTypes
    for forming hierarchy according to which templates are inherited'''

    parent_model = models.ForeignKey(ContentType,
    verbose_name="Übergeordneter Inhaltstyp",
    related_name="inheritance_parent",
    on_delete=models.CASCADE)
    ## parent_model should have ForeignKey relationship to child_model,
    ## i.e. Veranstaltung / Modul / Format
    child_model = models.ForeignKey(ContentType,
    verbose_name="Untergeordneter Inhaltstyp",
    related_name="inheritance_child",
    on_delete=models.CASCADE)

    class Meta:
        unique_together = [["parent_model","child_model"]]

    def __str__(self):
        return(f"{self.child_model} inherits from {self.parent_model}")

class MessagePart(SortableMixin):
    '''Body, subject'''
    name = models.CharField("Name",help_text="Name des Nachrichtenteils, i.e. Betreffzeile, Textkörper",
    max_length=100,unique=True,null=False,blank=False)
    messagepart_order = models.PositiveIntegerField("Reihenfolge",
    default=0, editable=False, db_index=True)

    class Meta:
        verbose_name = "Nachrichtenteil"
        verbose_name_plural = "Nachrichtenteile"
        ordering = ["messagepart_order"]

    def __str__(self):
        return(self.name)

class Category(models.Model):
    '''Type of document or communication,
    e.g. invitation, confirmation, consent. Used by database templating system.'''
    name = models.CharField("Name",help_text="Name der Kategorie",max_length=100,unique=True,null=False,blank=False)
    planned = models.CharField("geplant",help_text="Bezeichnung für geplante Mitteilung, z.B. zu bestätigen",max_length=100,
    null=True,unique=False,blank=False) ## NULL AND UNIQUE SHOULD BE SWITCHED TO TRUE!!
    completed = models.CharField("erfolgt",help_text="Bezeichnung für erfolgte Mitteilung, z.B. bestätigt",max_length=100,
    null=True,unique=False,blank=False)

    def __str__(self):
        return(self.name)

class DbTemplate(SortableMixin):

    app_label = "crm"
    model_name = "dbtemplate"

    name = models.CharField("Name",help_text="Name der Vorlage",max_length=100)
    content = models.TextField("Inhalt der Vorlage")
    category = models.ForeignKey(Category,
    on_delete=models.CASCADE,
    help_text="z.B. Einladung, Eingangsvermerk, Teilnahmebestätigung",
    verbose_name="Kategorie")

    message_part = models.ForeignKey(MessagePart,
    on_delete=models.CASCADE,
    help_text="Teil der Nachricht, z.B. Betreffzeile, Textkörper",
    verbose_name="Nachrichtenteil")

    ## ContentType for inheritance purposes
    content_model = models.ForeignKey(ContentType,
    on_delete=models.CASCADE)

    dbtemplate_order = models.PositiveIntegerField(default=0, editable=False, db_index=True)

    @property
    def messagepart_order(self):
        if self.message_part:
            return(self.message_part.messagepart_order)
        else:
            return(0)

    @property
    def category_name(self):
        if self.category:
            return(self.category.name)
        else:
            return("")

    class Meta:
        ordering = ["dbtemplate_order"]
        verbose_name = "Vorlage"
        verbose_name_plural = "Vorlagen"

    def __str__ (self):
        return(f"{self.category} ({self.message_part})")

class TemplateConnection(models.Model):
    '''Connection between a template
    and a specific content object or model'''
    app_label = "crm"
    model_name = "templateconnection"
    template = models.ForeignKey(DbTemplate,
    related_name="connections",
    on_delete=models.CASCADE)

    ## ContentType for which the template is a fallback option,
    ## causing the linked template to be the most general template.
    ## Should be left blank for object-specific connections.
    content_model = models.ForeignKey(ContentType,
    related_name = "connected_templates",
    on_delete=models.CASCADE,blank=True,null=True,
    help_text="This single field is alternative to the generic relation consisting of content_type and object id, providing one fallback template for all objects of type ")
    
    ## Generic relationship to content object,
    # for use in object-specific templates, i.e. Format Seminar.
    content_type = models.ForeignKey(ContentType,
    on_delete=models.CASCADE,blank=True,null=True)
    object_id = models.PositiveIntegerField(blank=True,null=True,help_text="Foreign key of object type specified in content_type")
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        unique_together = [["template","content_type","object_id"]]

    def __str__(self):
        if self.content_model:
            return(f"{self.template} connected to {self.content_model}")
        elif self.content_type and self.object_id:
            return(f"{self.template} connected to {self.content_object}")

