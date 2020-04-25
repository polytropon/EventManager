from crm import *
from django.conf import settings

from django.shortcuts import render
from django.http import HttpResponse,FileResponse
from .models import * ## All models stored in globals, specific model sent as parameter

import importlib
from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.template.context_processors import csrf
from django.forms import modelformset_factory, modelform_factory, formset_factory

from django.shortcuts import redirect
import json
from django.views.generic import ListView
from django.conf import settings
from django.template.loader import get_template

from django.utils.text import slugify


ENVIRONMENT = os.getenv('ENVIRONMENT','No ENVIRONMENT variable!')
SECRET_KEY = os.getenv('SECRET_KEY','No SECRET_KEY variable!')
GRAVITY_CLIENT_KEY = os.getenv('GRAVITY_CLIENT_KEY')
GRAVITY_CLIENT_SECRET = os.getenv('GRAVITY_CLIENT_SECRET')
logger = logging.getLogger("telegram_logger")
# logger.info(__name__)

class PersonList(ListView):
     model = Person

from custom_utils import excel_utils

from crm.gravity import gravity_request
from crm.utility_routines import merge_persons, find_duplicates

from crm.forms import PersonAutocompleteForm
from dal import autocomplete

from django.http import JsonResponse
from django.template.loader import render_to_string

from django.views.decorators.csrf import csrf_protect,ensure_csrf_cookie
import django
@login_required
def merge_duplicates(request):
    '''Combine two or more Person records and their related records
    into one, return new table row as HTML.'''
    
    merge_list = request.GET.dict()
    ## List is first key in dict (as string)
    merge_list = json.loads(list(merge_list.keys())[0])
    merged_dict = merge_persons(merge_list)
    context = {"duplicate_set":[merged_dict.pop("merged_person")]}
    new_row_html = str(render(request,'crm/duplicates/row.html',context).content,'utf-8')
    merged_dict["new_row_html"] = new_row_html
    return(JsonResponse(merged_dict))

@login_required
def duplicates(request):
    '''Show duplicate names in table
    TODO: Create option to select certain duplicates to merge while not merging others.
    '''
    
    persons = Person.objects.all().order_by("Familienname")
    duplicates = [] ## List of lists, each sublist contains duplicates with one name
    flat_list = [] ## Control list to prevent adding multiple copies of name match
    for p in persons:
        if p.Familienname and p.Vorname and p not in flat_list:
            persons_same_name = Person.objects.filter(Vorname__icontains=p.Vorname,Familienname__icontains=p.Familienname)
            if len(persons_same_name) > 1:
                for person_same_name in persons_same_name:
                    if person_same_name in flat_list:
                        flat_list.append(p)
                        break
                else:
                    flat_list.append(p)
                    duplicates.append(persons_same_name)

    context = {"duplicates":duplicates}
    return render(request, 'crm/duplicates/duplicates.html', context)


class PersonAutocomplete(autocomplete.Select2QuerySetView):
    '''Return queryset filter result for Autocomplete
    based on Person.Familienname'''
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return(Person.objects.none())
        qs = Person.objects.all()
        if self.q:
            qs = qs.filter(Familienname__icontains=self.q)
        return(qs)


@login_required
@csrf_protect
def send_message(request):
    '''Send invitation email to person
    in request query dict.
    Used by AJAX functions send() and send_all() on page Einladen via view send_invitations.'''
    querydict = request.POST.dict()
    
    person_id = int(querydict["person_id"])

    person = Person.objects.get(id=person_id)
    body = querydict["body"]
    body = simple_render(body,{"Person":person})
    subject = querydict["subject"]
    person.send_message(subject=subject,
    message=body,test=False,type=6) ## Type 6 is field in Communication meaning "sonstiges", can be changed
    return(JsonResponse(querydict))

@login_required
def email_invitation_to_person(request):
    '''Send invitation email to person
    in request query dict.
    Used by AJAX functions send() and send_all() on page Einladen via view send_invitations.'''
    querydict = request.GET.dict()
    event_id = int(querydict["event_id"])
    event = Veranstaltung.objects.get(id=event_id)
    person_id = int(querydict["person_id"])
    person = Person.objects.get(id=person_id)
    person.initialize_event(event) ## Create einladungscode (always the same for one person/veranstaltung combo)
    ## Dictionary of format {"message":"answer"} sent back in HTTP JSON response
    response_dict = person.invite(event)
    return(JsonResponse(response_dict))


@login_required
def get_people(request):
    '''Request body contains JSON dict with key group pk
    Return list of person primary keys and simple rendered persons
    Used in crm/invite/invite.html
    '''
    querydict = request.GET.dict()
    persons_selected = Group.objects.get(pk=querydict["group_id"]).members()

    response_dict = {"persons":str(len(persons_selected)),
    'html':[render_to_string("crm/invite/person.html",{"p":p}) for p in persons_selected],
    'person_ids':[p.id for p in persons_selected]
    }
    return(JsonResponse(response_dict))

@login_required
def start(request):
    logger.info(f"User {request.user} has accessed start page.")
    '''Home page'''
    context = {"future_events":Veranstaltung.objects.filter(Beginn__gte=datetime.now()).order_by("Beginn"),
    "past_events":Veranstaltung.objects.filter(Beginn__lte=datetime.now()).order_by("-Beginn"),
    "Bundesländer":Bundesland.objects.all()
    }

    return render(request, 'crm/navigation/start.html', context)

@login_required
def invited(request,event_id):
    '''Display persons invited to an event'''
    v = Veranstaltung.objects.get(pk=event_id)
    context = {"event":v,
    "answers":v.FormEntries.all().order_by("Familienname")}
    return render(request, 'crm/invite/invited.html', context)

@login_required
def invite(request):
    '''Page-level view for Einladen (dynamic invitation page)
    included PersonAutocomplete for inviting inviduals'''
    from crm.forms import PersonAutocompleteForm
    context = {'veranstaltungen':Veranstaltung.objects.filter(Beginn__gte=datetime.now()).filter(Beginn__lte=datetime.now()+timedelta(days=100)).order_by("Beginn"),
    "Gruppen":Group.objects.all(),"form":PersonAutocompleteForm()
    }
    return render(request, 'crm/invite/invite.html', context)

@login_required
def send_answers_participation(request,event_id):
    '''Send confirmation or denial email to all participants,
    logic in model function
    '''
    e = Veranstaltung.objects.get(pk=event_id)
    sent = e.send_answers_participation(test=False)
    return JsonResponse(sent,safe=False)

def public_events_past(request):
    '''Display events
    that took place in the past (for AJAX calls from external site)'''
    events = Veranstaltung.objects.filter(Format__public=True).filter(Beginn__lte=datetime.now()).order_by("-Beginn")
    modules = []
    for event in events:
        if event.Modul and event.Modul not in modules:
            modules.append(event.Modul)
    context = {"events":events,"modules":modules,"time":"past"}
    resp = render(request, 'crm/external_events/all.html', context)
    resp["Access-Control-Allow-Origin"] = '*'
    return(resp)

def public_events_future(request):
    '''Display public events
    that will take place in the future (for AJAX calls from external site)'''
    events_ = Veranstaltung.objects.filter(Format__public=True).filter(Beginn__gte=datetime.now()).order_by("Beginn")
    events = []
    modules = []
    for event in events_:
        if event.site_ready:
            events.append(event)
    for event in events:
        if event.Modul and event.Modul not in modules:
            modules.append(event.Modul)
    context = {"events":events,"modules":modules,"time":"future"}
    resp = render(request, 'crm/external_events/all.html', context)
    resp["Access-Control-Allow-Origin"] = '*'
    return(resp)

def public_events_all(request):
    '''Display all public events'''
    events_ = Veranstaltung.objects.filter(Format__public=True).order_by("Beginn")
    events = []
    modules = []

    for event in events_:
        ## Append all past events regardless of whether site ready or not
        if event.Beginn <= datetime.now():
            events.append(event)
        ## Only append future events if site is ready
        elif event.Beginn > datetime.now():
            if event.site_ready:
                events.append(event)
    for event in events:
        if event.Modul and event.Modul not in modules:
            modules.append(event.Modul)
    context = {"events":events,"modules":modules}
    resp = render(request, 'crm/external_events/all.html', context)
    resp["Access-Control-Allow-Origin"] = '*'
    return(resp)

def seminars_places_available(request):
    '''For external users: shows whether or not spaces are available'''
    s = Veranstaltung.objects.filter(Format__Bezeichnung="Seminar").filter(Beginn__gte=datetime.today()).order_by("Beginn")
    context = {"seminare":s}
    resp = render(request, 'crm/seminar/overview.html', context)
    resp["Access-Control-Allow-Origin"] = '*'
#    resp["Access-Control-Allow-Origin"] = "^(https?://(?:.+\.)?erasmus-stiftung\.de(?::\d{1,5})?)$"
    return(resp)

@login_required
def jsonGravity(request,veranstaltung_id):
    '''Export JSON file for manual import into Gravity
    TODO: Update JSON via API instead of manually importing,
    edit form as dict parsed from JSON instead of unprocessed text
    '''
    v = Veranstaltung.objects.get(id=int(veranstaltung_id))

    Inhalt = json.dumps(v.Inhalt)[1:-1]
    Datum = v.Beginn.strftime('%Y-%m-%d')
    Datum_Uhrzeit = v.Beginn.strftime('%d.%m. um %H:%M Uhr')
    context = {"v":v,"Datum":Datum,
    "Datum_Uhrzeit":json.dumps(Datum_Uhrzeit),
    "Inhalt":Inhalt}

    file_name = f"Form-{v.id}-{Datum}.json"
    full_path = f"/data/{file_name}"
    file = open(full_path, "w",encoding="utf-8")
    file.write(str(render(request, 'crm/formular_seminar.json', context).content,'utf-8'))
    file.close()
    stream = open(f'/data/{file_name}','rb')
    from io import BytesIO
    response = FileResponse(stream, content_type=f'application/json')
    response['Content-Disposition'] = f'inline; filename={file_name}'
    return(response)

from crm.forms import SeminarForm
from crm.forms import SeminarRegistrationForm
from django.forms.widgets import Select,NullBooleanSelect
from django.forms import ModelChoiceField
import collections

class PseudoField:

    def __init__(self,name,verbose_name=False):
        self.name = name
        self.verbose_name = verbose_name
    
    def label(self):
        return(self.verbose_name)

def form_factory_wrapper(instances,ordered_columns_dict,template,
    form_model=False,
    category_message_dict=False
    ):
    '''Convert iterable of instances, ordereddict and template
    into dict rendered using crm/ajax_forms templates and crm/templatetags tags

    {"formset":formset to be rendered,"columns":list of strings representing columns in table}

    '''
    if not form_model and len(instances):
        form_model = type(instances[0])

    model_fields = {field.name:field for field in form_model._meta.get_fields()}

    ModelSet = modelform_factory(form_model,fields=[key for key in ordered_columns_dict.keys() if key in model_fields],
    widgets = {field:field_dict["widget"] for field,field_dict in ordered_columns_dict.items() if "widget" in field_dict and field in model_fields}
    )

    formset = [ModelSet(instance=instance) for instance in instances]

    for key,val in ordered_columns_dict.items():
        if "queryset" in val:
            queryset = val["queryset"]
            for form in formset:
                form.fields[key].queryset = queryset
    
    column_list = OrderedDict()
    ## name:field (or PseudoField)

    for column_name,field_dict in ordered_columns_dict.items():
        if "modal" not in field_dict:
            if column_name in model_fields:
                field = model_fields[column_name]
                ## if model_fields[column_name] == django.db.models.fields.BooleanField
                column_list[column_name] = field
            elif column_name in dir(form_model):
                
                if "verbose_name" in field_dict:
                    verbose_name = field_dict["verbose_name"]
                else:
                    verbose_name = False
                column_list[column_name] = PseudoField(column_name,verbose_name=verbose_name)
 
    form_dict = {"formset":formset,"columns":column_list}

    for option in "modal","read_only":
        form_dict[option] = [column_name for column_name,val in ordered_columns_dict.items() if option in val]

    form_dict["template"] = template
    form_dict["category_message_dict"] = category_message_dict ## Used by template edit view
    return(form_dict)


@login_required
def create_specific_template(request,model_name,object_id,template_id):
    '''COPY DBTEMPLATE OBJECT AND
CREATE TEMPLATE CONNECTION TO NEW OBJECT

args: old TemplateConnection.pk

'''
    model = ContentType.objects.get(model=model_name)
    obj = model.get_object_for_this_type(pk=object_id)
    template = DbTemplate.objects.get(pk=template_id)
    
    template_properties = {field.name:getattr(template,field.name) for field in template._meta.fields if field.name != "id"}
    new_template = DbTemplate.objects.create(**template_properties)
    
    new_connection = TemplateConnection.objects.create(template=new_template,
    content_type=model,
    object_id=object_id,
    content_object=obj)

    return(linked_templates(request,model_name,object_id))


@login_required
def linked_templates(request,model_name,object_id):
    '''Return page with templates linked to an
    object of an arbitrary type'''
    model = ContentType.objects.get(model=model_name)
    obj = model.get_object_for_this_type(pk=object_id)

    if type(obj) == Veranstaltung:
        event = obj
    else:
        event = False

    template_instances = get_object_templates(obj)
    from custom_utils.sorter import multisort
    template_instances = multisort(template_instances,["messagepart_order","category_name"])
    
    categories = {t.category for t in template_instances}
    category_message_dict = OrderedDict([])

    
    for t in template_instances:
        if t.category.name in category_message_dict:
            assert type(category_message_dict[t.category.name]) == OrderedDict
            if t.message_part.name in category_message_dict[t.category.name]:
                assert(type(category_message_dict[t.category.name][t.message_part.name])) == list
                category_message_dict[t.category.name][t.message_part.name].append(t)
            else:
                category_message_dict[t.category.name][t.message_part.name] = [t]
        else:
            category_message_dict[t.category.name] = OrderedDict([(t.message_part.name , [t])])

    # template = "crm/ajax_forms/table.html"
    template = "crm/db_templates/template_tabs.html"

    ordered_columns_dict = OrderedDict([
        # ("name",{}),        
        ("content",{}),
        # ("content",{"read_only":True}),
        ] )

    form_dict = form_factory_wrapper(template_instances,ordered_columns_dict,template,
    form_model=DbTemplate,
    category_message_dict=category_message_dict
    )

    form_dict["obj"] = obj
    form_dict["object_id"] = object_id
    form_dict["model_name"] = model_name
    form_dict["category_message_dict"] = category_message_dict
    form_dict["request"] = request

    context = {"obj":obj,
        "table":form_dict,
        "event":event}

    if event:
        from crm.forms import EventForm

        context["event_form"] = {
            "form":EventForm(instance=event),
            "template":"crm/seminar/quickedit.html",
            "event":event,
            "request":request
        }

    return render(request, 'crm/db_templates/page.html',context)

@login_required
def edit_registrations(request,veranstaltung_id):
    '''Show all form entries for this Veranstaltung
    Sorting logic in Veranstaltung.FormEntriesTimeOrder
    '''

    event = Veranstaltung.objects.get(pk=int(veranstaltung_id))
    if event.Format and event.Format.Bezeichnung == "Seminar":
        
        ## Event data (hotel address, number of rooms booked)
        seminar_quickedit = SeminarForm(instance=event)

        bookingoptions = event.calculated_bookingoptions
        form_dict = form_factory_wrapper(
        event.valid_form_entries,    
        OrderedDict([
        ("Eingang",{"read_only":True}),
        ("an_name",{"read_only":True}),

        ("E_Mail",{}),
        ("Mobiltelefon",{}),
        ("bookingoption",{"widget":Select(attrs={"onchange":"roomChange(event)"}),
        "queryset":bookingoptions} ),
        ("Status",{"widget":Select(attrs={"onchange":"statusChange(event)"}) } ),
        ("Titel",{"modal":True}),
        ("Familienname",{"modal":True}),
        ("Vorname",{"modal":True}),
        ("Anmerkungen_Sachbearbeiter",{"modal":True}),
        ("Anmerkungen",{"modal":True,"read_only":True}),
        ("referent",{"widget":NullBooleanSelect(),"modal":True}),  ##attrs={"class":"form-check-input"}
        ] ) ,
        "crm/event/registrations_table.html",
        form_model=FormEntry
        )
          
        return render(request, 'crm/event/page.html',
        {"registrations_table":form_dict,
        "seminar_quickedit":
        {"template":"crm/seminar/quickedit.html",
        "form":seminar_quickedit},
        'event':event})

    else:

        form_dict = form_factory_wrapper( event.valid_form_entries,
        OrderedDict([ ("Eingang",{}),
        ("Familienname",{}),
        ("Vorname",{}),
        ("E_Mail",{}),
        ("Status",{}),
        ("Anmerkungen",{"read_only":True,"modal":True}),
        ("Anmerkungen_Sachbearbeiter",{"modal":True}),
        ("referent",{"widget":NullBooleanSelect(),"modal":True}),  ##attrs={"class":"form-check-input"}

         ]),
         "crm/event/registrations_table.html",
         form_model=FormEntry
         )

        return render(request, 'crm/event/page.html',
        {"event":event,
        "registrations_table":form_dict})


def send_event_message(formentry,message_type=False,category=False):
    templates = get_object_templates(formentry.event)
    
    if message_type:
        templates_receipt = [t for t in templates if t.category.name == message_type]
    elif category:
        templates_receipt = get_object_templates(formentry.event,category=category)
    else:
        logger.warning("In send_event_message, neither message_type string nor category given for formentry {0}".format(formentry))

    body_templates = [t for t in templates_receipt if t.message_part.name == "Textkörper"]
    if len(body_templates) == 0:
        logger.warning("views.send_event_message cannot send message to formentry with id {0}, no body template for category {1}".format(formentry.pk,category))
        return(False)
    body_template_string = body_templates[0].content

    subject_templates = [t for t in templates_receipt if t.message_part.name == "Betreffzeile"]
    if len(subject_templates) == 0:
        logger.warning("views.send_event_message cannot send message to formentry with id {0}, no subject template for category {1}".format(formentry.pk,category))
        return(False)
    subject_template_string = subject_templates[0].content

    message = simple_render(body_template_string,{"formentry":formentry})
    subject = simple_render(subject_template_string,{"formentry":formentry})
    logger.info("Subject:{0}\nMessage:\n{1}".format(subject,message))

    send_mail(subject, message,
    formentry.event.send_from_email,
    [formentry.E_Mail,formentry.event.send_from_email])

    ## This logic is in Veranstaltung.send_answers_participation
    # formentry.Status = category.completed
    # formentry.save()
    Communication.objects.create(formentry=formentry,
    person=formentry.person,
    event=formentry.event,
    medium=1,
    subject=subject,
    message=message
    )

def register(request,event_id):
    # simple_render

    event = Veranstaltung.objects.get(pk=event_id)
    templates = get_object_templates(event) + standard_templates(event)
    consents = {slugify(t.name):t for t in templates if t.category.name =='Einwilligung'}

    if request.user.is_authenticated:
        required = False
    else:
        required = True
    
    if len(event.invitation_codes.all()):
        invitation_code_required = True
    else:
        invitation_code_required = False

    if request.method == 'POST':
        ### Form submission logic
        ## Variable required is used in SeminarRegistrationForm.__init__ function
        ## to turn off required entry where not possible in template
        form = SeminarRegistrationForm(request.POST,event=event,
        required=required,
        invitation_code_required=invitation_code_required)
        form.is_valid()

        # if ENVIRONMENT == "local":
        #     isvalid = form.is_valid()
        #     return(JsonResponse( {"clean_data":str(form.cleaned_data),
        #     "isvalid":isvalid},safe=False))

        ## Validation only needed if invitation code required, unknown validation
        ## problems with Vortrag type events.
        ## TODO: FIGURE OUT WHY VALIDATION IS FAILING WITH NORMAL VORTRÄGE WITHOUT INVITE CODE!!
        # if not form.is_valid() and not request.user.is_authenticated and invitation_code_required:
        #     return(render(request,"crm/event/register.html",
        #             {"event":event,"form":form,
        #             "request":request.__dict__,
        #             "invitation_code_required":invitation_code_required
        #             }))

        querydict = dict(request.POST)
        querydict.pop("csrfmiddlewaretoken")
        
        if invitation_code_required:
            invitation_code_string = querydict.pop("invitation_code",False)
        #     if InvitationCode.objects.filter(text=invitation_code_string).exists():
        #         invitation_code = InvitationCode.objects.get(text=invitation_code)
        #         invitation_code_message = "Einladungscode verifiziert."
        #     else:
        #         invitation_code = False
        #         invitation_code_message = "Einladungscode nicht gefunden."

        ## Values are in lists containing one item, converted to simple values
        querydict = {key:val[0] for key,val in querydict.items()}

        createdict = {"Veranstaltung":event,
        "JSON":json.dumps(querydict),
        "date_created":datetime.now(),
        "invitation_code":form.cleaned_data["invitation_code"]
        }

        field_names = [field.name for field in FormEntry._meta.get_fields()]

        display_values = {}
        event_templates = standard_templates(event)
        
        ## Part of loop for created_dict could be replaced by cleaned data
        for key,value in querydict.items():                
            if key in field_names:
                field = FormEntry._meta.get_field(key)

                if type(field) == django.db.models.fields.related.ForeignKey:
                    createdict[key] = display_value = field.related_model.objects.get(pk=value)
                
                elif type(field) == django.db.models.fields.BooleanField:
                    createdict[key] = {"on":True}[value] ## Only checked boxes are sent as variables
                    display_value = {"on":"Ja"}[value]
                
                else:
                    createdict[key] = display_value = value
                
                if hasattr(field,"verbose_name"):
                    display_label = field.verbose_name
                else:
                    display_label = field.name
                
                display_values[display_label] = display_value

        for x,y in (("user_agent","HTTP_USER_AGENT"), ("source_url","HTTP_REFERER"),
        ("ip","REMOTE_ADDR")):
            createdict[x] = request.META[y]

        formentry = FormEntry.objects.create(**createdict)

        try:
            [formentry.consent_set.create(text=consent.content,
            dbtemplate=consent) for slug,consent in consents.items() if slug in querydict]
        except Exception as e:
            message = f"Error in views.register during consent record creation:\n{e}\querydict:\n{querydict}\nEvent:{event.__dict__}\nFormEntry:{formentry}\n"
            logger.info(message)
        
        try:
            if not request.user.is_authenticated or ("send_confirmation_mail" in querydict):
                send_event_message(formentry,message_type='Eingangsbestätigung Anmeldung')
        except Exception as e:
            message = f"Error in views.register when sending email:\n{e}\querydict:\n{querydict}\nEvent:{event.__dict__}\nFormEntry:{formentry}"
            logger.info(message)
        
        # if ENVIRONMENT == "local":
        #     return JsonResponse({
        #     "invitation_code_required":invitation_code_required,
        #     "form_valid":form.is_valid(),
        #     "cleaned_data":form.clean()
        #     },safe=False)
        #     # return JsonResponse(querydict,safe=False)
        # else:
        return(render(request,"crm/event/register.html",
        {"event":event,"form":form,
        "request":request.__dict__,"querydict":querydict,
        "display_values":display_values,
        "formentry":formentry,
        "invitation_code_required":invitation_code_required,
        }))

    elif request.method == "GET":
        form = SeminarRegistrationForm(event=event,
        required=required)

        if request.user.is_authenticated:
            required_class = ""
        else:
            required_class = "required"

        return(render(request,"crm/event/register.html",
        {"event":event,"form":form,"request":request.__dict__,
        "required_class":required_class,
        "consents":consents,
        "invitation_code_required":invitation_code_required,
        }))

@login_required
def all_participants_export_excel(request,event_id):
    '''Export the registrations for a event with contact and address data as Excel file
    and return file in HTTP response'''
    from custom_utils.excel_utils import seminarExcel
    event = Veranstaltung.objects.get(pk=event_id)
    registrants = event.valid_form_entries
#    registrants = multisort(event.valid_form_entries,"Familienname")

    export_statuses = list(FormEntry.Statusoptionen) + [None]
    export_statuses.remove("Papierkorb")

#    file_name = f"{event.Beginn.strftime('%Y-%m-%d')}  – {event.Raum_Einladung} {event.Bezeichnung}"
    file_name = slugify(f"{event.Beginn.strftime('%Y-%m-%d')} {event.Raum_Einladung} {event.Bezeichnung}")

    seminarExcel(registrants,file_name,["Anrede","Titel","Familienname",
"Vorname","roomtype_abbreviation","Zweitperson_Zimmer","Zimmerpartner","Rolle","Status",
"Anzahl_ÜN","von_bis",#"von","bis",
"E_Mail","Mobiltelefon",
"Zusatz_Adresse","Straße","PLZ","Ort"],export_statuses=export_statuses)

    stream = open(f'/data/{file_name}.xlsx','rb')
    # from io import BytesIO
    # root,ext = os.path.splitext(file_name)
    response = FileResponse(stream, content_type='application/xlsx')
    response['Content-Disposition'] = f'inline; filename={file_name}.xlsx'
    return(response)


@login_required
def participants_export_excel(request,event_id):
    '''Export only the confirmed registrations (without contact data) for a event as Excel file
    and return file in HTTP response'''
    from custom_utils.excel_utils import seminarExcel,eventExcel
    event = Veranstaltung.objects.get(pk=event_id)

    registrants = event.valid_form_entries
    
#    registrants = multisort(event.valid_form_entries,"Familienname")

    file_name = event.Beginn.strftime('%Y-%m-%d') + " " + slugify(event.Raum_Einladung) + " Hotelgäste"

    if event.Format.Bezeichnung == "Seminar":
        seminarExcel(registrants,file_name)
    else:
        eventExcel(registrants,file_name)

    stream = open(f'/data/{file_name}.xlsx','rb')
    # from io import BytesIO
    # root,ext = os.path.splitext(file_name)
    response = FileResponse(stream, content_type='application/xlsx')
    response['Content-Disposition'] = f'inline; filename={file_name}.xlsx'
    return(response)

@login_required
def event_statistics(request,event_id):
    '''Return content of statistics widget
    with number of participants with DZ/EZ/Extern on AJAX call from registration page.'''
    event = Veranstaltung.objects.get(pk=event_id)
    # invited = event.invited
    if event.Format and event.Format.Bezeichnung == "Seminar":
        template = 'crm/seminar/statistics.html'
    else:
        template = 'crm/event/statistics.html'
 
    return(render(request,template,
    {"statistics":event.statistics(),"event":event
    # "invited":invited
    }))

# @login_required
# def update_future_registrations(self):
#     '''Triggered by AJAX call from event overview page,
#     should later be converted to cron job or eliminated with new forms.
#     Call Gravity Forms API once for each event in the future,
#     return list of lists containing new registrations per event.'''
#     future_events = Veranstaltung.objects.filter(Beginn__gte=datetime.today())

#     ## parseAnmeldungen updates cached statistics via event.statistics
#     new_registrations = [event.parseAnmeldungen() for event in future_events]
#     new_registrations = [r for r in new_registrations if r not in (None,[])]
#     if new_registrations:
#         update = True
#     else:
#         update = False
#     return JsonResponse(update,safe=False)

@login_required
def ajax_save(request):
    '''Save new field value changed by user, triggered
    by focusout on page'''
    
    save_dict = request.POST.dict()
    model = globals()[save_dict["model"]]
    record = model.objects.get(pk=save_dict["pk"])

    new_value = save_dict["newvalue"]
    column = save_dict["column"]

    field_type = type(model._meta.get_field(column)) ## == models.DateField.formfield

    ## If field is a ForeignKey, get object and set it
    if field_type == django.db.models.fields.related.ForeignKey:
        if not new_value: ## If new value is empty string...
            new_value = None
        else:
            foreign_key_model = model._meta.get_field(column).related_model
            foreign_key_object = foreign_key_model.objects.get(pk=new_value)
            new_value = foreign_key_object
    elif field_type == django.db.models.fields.BooleanField:
        bool_convert = {"true":True,"false":False,"undefined":None}
        new_value = bool_convert[new_value]

    ## All other field types: simply set text
    
    setattr(record,column,new_value)

    ## TODO: CREATE MODEL TO SAVE PAST VALUES    
    record.save()
    request.META["REMOTE_ADDR"] ## IP address
    request.META["HTTP_USER_AGENT"] ## User agent
    request.user ## https://docs.djangoproject.com/en/2.2/ref/request-response/
    ## An instance of AUTH_USER_MODEL representing the currently logged-in user. (<class 'django.contrib.auth.models.User'>)
    
    # if field_type = models.DateField.formfield:

    save_dict["field_type"] = str(field_type)
    save_dict["request"] = str(request.__dict__)
    return JsonResponse(save_dict,safe=False)


# @login_required
# def save_registrations_ajax(request,veranstaltung_id):
#     '''Save new field values changed by user, triggered
#     by focusout on page'''

#     update_list = request.GET.dict()["save_list"]
#     assert type(update_list) == str
#     update_list = json.loads(update_list)
#     assert type(update_list) == list
#     update_rows = {} ## "1":{"Übernachtung":"EZ","Mobilnummer":"123456"}
#     for field in update_list:
# #        field = json.loads(field)
#         entry_id = field["entry_id"]
#         if entry_id not in update_rows:
#             update_rows[entry_id] = {field["field"]:field["value"]}
#         elif entry_id in update_rows:
#             update_rows[entry_id][field["field"]] = field["value"]

#     for entry_id,values in update_rows.items():
#         entry = FormEntry.objects.get(entry_id=entry_id)
#         if entry.Titel == "None": ## Unknown bug causes "None" text value
#             entry.Titel = None
#         [setattr(entry,key,val) for key,val in values.items()]
#         entry.save()
#     return JsonResponse(update_list,safe=False)

# @login_required
# def update_registrations(request,event_id):
#     '''
#     Arg: veranstaltung_id (pk)
#     Load new registrations from Gravity API that are not yet in DB
#     '''
#     v = Veranstaltung.objects.get(pk=int(event_id))

#     new_entries = v.parseAnmeldungen()

#     if new_entries:
#         new_entries = True
#     else:
#         new_entries = False
#     return JsonResponse(new_entries,safe=False)

# @login_required
# def events_overview_request_to_context(request):
#     '''Accept request with optional querystring "future", "past"
#     Used by syncGravityForms and registrations_overview
#     to produce context for registration overview pages (or just table) from request'''
#     querydict = request.GET.dict() ##
#     if "time" in querydict:
#         if querydict["time"] == "future":
#             context = {'events':Veranstaltung.objects.filter(Beginn__gte=datetime.today()).order_by('Beginn'),
#             "Zeit":"Künftige Veranstaltungen"
#             } ## later to be filtered by date
#         elif querydict["time"] == "past":
#             context = {'events':Veranstaltung.objects.filter(Beginn__lte=datetime.today()).order_by('-Beginn'),
#             "Zeit":"Vergangene Veranstaltungen"
#             }
#         else:
#             context = {'events':Veranstaltung.objects.order_by('-Beginn'),
#             "Zeit":"Alle Veranstaltungen"
#             }
#     else:
#         context = {'events':Veranstaltung.objects.order_by('Beginn'),
#         "Zeit":"Alle Veranstaltungen"
#         }
#     return(context)

# from crm.gravity import syncGravityFormsApiSave

# @login_required
# def syncGravityForms(request):
#     '''Activated on registration overview page load
#     Return HTML table with current list of Gravity forms and registration numbers
#     '''
#     ## Sync DB with gravity forms, ensuring that existing forms are registered in DB
#     syncGravityFormsApiSave()
#     ## Render request with updated data
#     context = events_overview_request_to_context(request)
#     return render(request, 'crm/registrations_overview/table.html', context)

@login_required
def registrations_overview(request):
    '''Return all events that lie in the future,
    the number of registrations for each event and the
    maximal number of registrations'''
    context = events_overview_request_to_context(request)
    return render(request, 'crm/registrations_overview/page.html', context)

from crm.forms import DateTimeInput, DateInput


@login_required
def formeEntrySetRegistrations(request,arg):
    '''Working demonstration code, displays registrations including further modal fields
    using FormEntrySet. Not operational bc it does not allow
    simple python lists for sorting.
    '''
    event = Veranstaltung.objects.get(pk=30)

    FormEntrySet = modelformset_factory(FormEntry,fields=("date_created","E_Mail","Mobiltelefon",
    "Übernachtung","Zweitperson_Zimmer","Status","Anmerkungen_Sachbearbeiter","Anmerkungen"),
    widgets={"date_created":DateTimeInput()
    })

    return render(request, 'crm/ajax_forms/page.html',
    {'formset': FormEntrySet(queryset=FormEntry.objects.filter(Veranstaltung=event)),'readonly':("date_created","Mobiltelefon","E_Mail","Anmerkungen"),
    'modal':("Anmerkungen_Sachbearbeiter","Anmerkungen"),
    'columns':("date_created","E_Mail","Mobiltelefon",
    "Übernachtung","Zweitperson_Zimmer","Status"),
    'event':event})

@login_required
def select_room_partner(request):
    save_dict = request.GET.dict()
    fe = FormEntry.objects.get(pk=save_dict["formentry_id"])
    from crm.forms import RoomPartnerForm
    form = RoomPartnerForm(instance=fe)
    options = list(FormEntry.objects.filter(Veranstaltung=fe.Veranstaltung).filter(bookingoption__roomtype__occupants=2).exclude(pk=fe.pk).exclude(Status="Papierkorb"))

    # options = [option for option in options if not FormEntry.objects.filter(Veranstaltung=fe.Veranstaltung).filter(room_partner=option).exists()]

    options = [option for option in options if option.Status not in ("Papierkorb","abgesagt","Teilnehmer storniert") and not FormEntry.objects.filter(Veranstaltung=fe.Veranstaltung).filter(room_partner=option).exists()]
        
    return(render(request,"crm/seminar/room_partner.html",{"form":form,"options":options,
    "selected":fe.room_partner}))

@login_required
@ensure_csrf_cookie
def send_message_page(request):
    '''Function for testing arbitrary code'''
    '''Page-level view for Einladen (dynamic invitation page)
    included PersonAutocomplete for inviting inviduals'''
    
    context = {'veranstaltungen':Veranstaltung.objects.filter(Beginn__gte=datetime.now()).filter(Beginn__lte=datetime.now()+timedelta(days=100)).order_by("Beginn"),
    "Gruppen":Group.objects.all(),"form":PersonAutocompleteForm()
    }
    return render(request, 'crm/send_message/page.html', context)

@login_required
@ensure_csrf_cookie
def sandbox(request,arg):
    '''Function for testing arbitrary code'''
    '''Page-level view for Einladen (dynamic invitation page)
    included PersonAutocomplete for inviting inviduals'''
    from crm.forms import PersonAutocompleteForm
    context = {'veranstaltungen':Veranstaltung.objects.filter(Beginn__gte=datetime.now()).filter(Beginn__lte=datetime.now()+timedelta(days=100)).order_by("Beginn"),
    "Gruppen":Group.objects.all(),"form":PersonAutocompleteForm()
    }
    return render(request, 'crm/send_message/page.html', context)

def upload(request,arg):
    '''All-purpose import API without corresponding view
    Parse arguments into dict
    create record of model dict['model']
    use other dict arguments as record values
    '''
    if ENVIRONMENT != 'local':
         return(HttpResponse(f"Not in local environment, function deactivated."))

    querydict = request.GET.dict() ## QueryDict.dict()

    if 'model' not in querydict: ## Keyword model is used to get the model to be created, all are imported
        return(HttpResponse(f"'Model' not in querydict\n:{querydict}"))
    else:
        model_name = querydict.pop('model') ## Remove model name
        if model_name not in globals():
            return(HttpResponse(f"Model not in globals\n:{model_name}"))
        else:
            model = globals()[model_name]
            try:
                ## Remove empty values
                querydict = {key:value for key,value in querydict.items() if value != '' and key != "id"}

                ## Block for converting strings to normed data / foreign keys
                ## Assume that all data comes as a string
                if "Partei" in querydict:
                    if querydict["Partei"] == '':
                        querydict.pop("Partei")
                    else:
                        try:
                            querydict["Partei"] = Partei.objects.get(Kürzel=querydict["Partei"])
                        except: ## If party object doesn't exist, create it
                            querydict["Partei"] = Partei.objects.create(Kürzel=querydict["Partei"],Langbezeichung="")

                if "Anrede" in querydict:
                    if querydict["Anrede"] == '':
                        querydict.pop("Anrede")
                    else:
                        querydict["Anrede"] = Geschlecht.objects.get(Herr_Frau=querydict["Anrede"])

                if "Priorität" in querydict:
                    if querydict["Priorität"] == '':
                        querydict.pop("Priorität")
                    else:
                        try: ## IF Priorität doesn't exist, create it
                            querydict["Priorität"] = Priorität.objects.get(Bezeichnung=querydict["Priorität"])
                        except:
                            querydict["Priorität"] = Priorität.objects.create(Bezeichnung=querydict["Priorität"])

                if "Kreis" in querydict:
                    querydict["Kreis"] = Kreis.objects.get(Nr_Kreis=querydict["Kreis"])

                if "LV" in querydict or "Landesverband" in querydict:
                    if "LV" in querydict:
                        querydict["Bundesland"] = Bundesland.objects.get(LV=querydict.pop("LV"))
                        if "Landesverband" in querydict: querydict.pop("Landesverband") ## Landesverband not needed
                    if "Landesverband" in querydict:
                        querydict["Bundesland"] = Bundesland.objects.get(Landesverband=querydict.pop("Landesverband"))

                if "Funktionen" in querydict: ## Value must be parsed before dict cleaned of values that do not match fields
                    list_functions = querydict.pop("Funktionen").split(",") ## Processed later
                else:
                    list_functions = False

                ## Only set attributes that are fields / columns in DB
                field_names = [field.name for field in model._meta.get_fields()]

                querydict = {key:value for key,value in querydict.items() if key in field_names}

                ## Once fields have been filtered for matching names, check for dates to convert
                if type(model) == Person:
                    assert type(model._meta.get_field("Familienname")).formfield == models.CharField.formfield
                    assert type(Person._meta.get_field("ausschließen")).formfield == models.DateField.formfield
                    #assert type(Person._meta.get_field("ausschließen")).formfield == models.DateField.formfield

                for key,value in querydict.items():
                    if type(model._meta.get_field(key)).formfield == models.DateField.formfield:
                        value = datetime.strptime(value,"%d.%m.%Y").strftime("%Y-%m-%d")
                        querydict[key] = value

                new_obj = model.objects.create(**querydict)

                if "E_Mail2" in querydict:
                    if querydict["E_Mail2"] != None:
                        new_obj.emails.create(email=querydict["E_Mail2"])

                functions_created = ""
                if list_functions:
                # if "Funktionen" in querydict: ## Comes from SEWOBE, comma-separated string of Funktion numbers (Hausberger)
                    for Nr_Fkt in list_functions:
                        f = Funktion.objects.get(Nr_Fkt=int(Nr_Fkt))

                        new_fkt = PersonFunction.objects.create(Person=new_obj,Funktion=f)
                        functions_created += str(new_fkt)

                response_dict = {key:value for key,value in new_obj.__dict__.items() if key != "_state" and "_cache" not in key}

                convert_serializable = {"Anrede":"Herr_Frau","Partei":"Kürzel",
                "Kreis":"Name_Kreis",
                "Priorität":"Bezeichnung"}
                for key,value in response_dict.items():
                    if key in convert_serializable and value != None:
                        response_dict[key] = getattr(value,convert_serializable[key])

                if functions_created:
                    response_dict["functions_created"] = functions_created.__dict__
                return(JsonResponse(response_dict))
            except Exception as e:
                return(JsonResponse({"Error":f"{e}"}))

@login_required
def dataView(request,file_name):
    '''Return file when given file name
    file_name includes file name and extension, but not
    /data/ directory (which is assumed)'''
    # module_dir = os.path.dirname(__file__)
    stream = open(f'/data/{file_name}','rb')
    from io import BytesIO
    root,ext = os.path.splitext(file_name)
    response = FileResponse(stream, content_type=f'application/{ext}')
    # response = FileResponse(stream, content_type='application/xlsx')
    response['Content-Disposition'] = f'inline; filename={file_name}'
    return(response)

# @login_required
# def upload_funktionen(request,arg):
#     '''Single-purpose function for uploading
#     Function entries from SharePoint
#     '''
#     querydict = request.GET.dict()
#     fg_text = querydict.pop("Fachgruppe")

#     fg_min = int(fg_text.split(' - ')[0])
#     try:
#         fg = Fachgruppe.objects.get(Min=fg_min)
#     except Exception as e:
#         return(HttpResponse(f"Get for {fg_text} failed with exception {e}"))
#     if type(fg) != Fachgruppe:
#         return(HttpResponse(f"Type of search is not fachgruppe for: {fg_text}"))
#     else:
#         querydict["Fachgruppe"] = fg
#         try:
#             new_obj = Funktion.objects.create(**querydict)
#             return(HttpResponse(f"Created: {new_obj}"))
#         except Exception as e:
#             return(HttpResponse(f"Get for dict:\n{querydict}\nfailed with exception {e}"))
