#from crm.models import PostcodeRange
from crm.models import *

def postcode_to_Bundesland(postcode):
    '''Take postcode string or int,
    return Bundesland object or None'''
    if type(postcode) == str and postcode.isdigit():
        if len(postcode) < 4:
            return(None)
        else:
            postcode = int(postcode)
    from crm.models import PostcodeRange
    postcode_ranges = PostcodeRange.objects.filter(Min__lte=postcode).filter(Max__gte=postcode)
    if len(postcode_ranges) == 1:
        return(postcode_ranges[0].Bundesland)

def get_Bundesland_from_postcode():
    '''Save Person.Bundesland (foreign key) for all persons with a
    postcode, but without a Bundesland
    '''
    persons_bundesländer = [(p,postcode_to_Bundesland(p.PLZ)) for p in Person.objects.all() if p.PLZ not in ("",None) and p.PLZ.isdigit()]

    for p, b in persons_bundesländer:
        p.Bundesland = b
        p.save()

def cache_Bundesland():
    for pf in PersonFunction.objects.all():
        pf.Bundesland = pf.Person.Bundesland
        pf.save()

def cache_Fachgruppe():
    for pf in PersonFunction.objects.all():
        pf.Fachgruppe = pf.Funktion.Fachgruppe
        pf.save()

def find_duplicates():
    _match_list = []
    from crm.models import Person, Communication,PersonFunction,Email
    for p in Person.objects.all():
        matches = list(Person.objects.filter(Familienname__icontains=p.Familienname,Vorname__icontains=p.Vorname))
        matches.extend(list(Person.objects.filter(Vorname__icontains=p.Vorname,E_Mail__icontains=p.E_Mail)))

        if len(matches) > 1:
            _match_list.append(list(matches))

    match_list = []
    for match_set in _match_list:
        in_list = False
        for match in match_set:
            for match_set2 in match_list:
                if match in match_set2:
                    in_list = True
        if not in_list:
            match_list.append(match_set)
    return(match_list)

def merge_persons(matches):
    '''Triggered by AJAX call on duplicates page
    Save attributes of all persons to be merged in 0-index person, combine foreign key attributes
    Delete other persons'''
    assert all([type(match) == int or match.isdigit() for match in matches])
    from crm.models import Person, Communication,PersonFunction,Email,FormEntry
    import json

    matches = [Person.objects.filter(pk=int(match)) for match in matches]
    matches = [m[0] for m in matches if m]

    model_fields = {field.name:None for field in Person._meta.get_fields() if hasattr(field,"name") and field.name not in ("id",)}
    model_fields["emails"] = [] ## Email objects
    email_strings = [] ## Email strings (lower case)
    emails = []
    communications = []
    functions = []
    formentries = []

    merged_person = matches[0] ## All changes saved in 0-index merged person

    for match in matches:
        communications.extend(Communication.objects.filter(person=match))
        functions.extend(PersonFunction.objects.filter(Person=match))
        formentries.extend(FormEntry.objects.filter(_person=match))
        for field in model_fields:
            if hasattr(match,field):
                field_value = getattr(match,field)
                if field_value:

                    if field == "Notizen" and model_fields["Notizen"]:
                        model_fields[field] = model_fields[field] + "\n" + field_value
                    elif field == "Quelle" and model_fields["Quelle"]:
                        model_fields[field] = model_fields[field] + "\n" + field_value
                    elif field == "emails":
                        if len(field_value.all()) > 0:
                            emails.extend(list(field_value.all()))
                    elif field == "E_Mail":
                        if "E_Mail": ## Prevents adding empty emails
                            email_strings.append(field_value.lower())
                    else:
                        model_fields[field] = field_value

    email_strings = [email_string for email_string in email_strings if email_string not in [e.email.lower() for e in emails] ]
    ## Creates model objects to be saved to 0-index match
    model_fields["emails"] = [Email.objects.create(person=merged_person,email=e) for e in set(email_strings)] ## Remove duplicate emails


    for c in communications:
        c.person = merged_person
        c.save()
    for f in functions:
        f.Person = merged_person
        f.save()
    for fe in formentries:
        fe._person = merged_person
        fe.save()
    for e in emails:
        e.person = merged_person
        e.save()

    [setattr(merged_person,key,value) for key, value in model_fields.items() if hasattr(merged_person,key) and type(getattr(merged_person,key)).__name__ != "RelatedManager"]

    ## If email in person model is none, but other emails are available, arbitrarily choose one of the other emails as value for Person.E_Mail
    if not merged_person.E_Mail:
        if email_strings:
            merged_person.E_Mail = email_strings[0]
        elif emails:
            merged_person.E_Mail = emails[0].email

    merged_person.save()
    deleted_pks = [m.pk for m in matches[1:]]
    [m.delete() for m in matches[1:]]
    return({"merged_pk":matches[0].pk,"deleted_pks":deleted_pks,
    "merged_person":matches[0]})

import random
import string
from random import seed
from random import randint

def randomString(stringLength=8):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))

def anonymizeTemplates():
    from crm.models import DbTemplate
    ts = DbTemplate.objects.all()
    for t in ts:
        if "=================" in t.content:
            t.content = t.content.split("=================")[0]
            t.save()

def cleanTable(table):
    fields = {field.name:field for field in table._meta.get_fields() if hasattr(field,"name") and field.name not in ("id",) and "_id" not in field.name}
    for obj in table.objects.all():
        for field_name,field in fields.items():
            if type(field).__name__ in ("CharField","TextField","EmailField"):
                if getattr(obj,field_name):
                    setattr(obj,field_name,
                    randomString(stringLength=len(getattr(obj,field_name))) )
            elif type(field).__name__ in ("IntegerField",):
                setattr(obj,field_name,randint(0,20))

        obj.save()
    
def randomize_data():    

    for table in (Person,FormEntry,Veranstaltung):
        cleanTable(table)