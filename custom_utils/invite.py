from crm.models import *
# v = Veranstaltung.objects.get(pk=event_id)
# registered = [fe.person for fe in v.FormEntries.all()]
# persons = Person.objects.all()
# [p._einladungscode(v) for p in persons if p not in registered]
# [p._params_link(v) for p in persons if p not in registered]
# [p.send_message("Einladung: Kongress Meinungsfreiheit / 15.06.2019 10-16 Uhr / Berlin",v.Einladungstext,test=True) for p in persons if p not in registered]

def emailablePersons(person_queryset):
    return([p for p in person_queryset if p.E_Mail and not p.ausschließen])
# invitees = [p for p in Person.objects.all() if p.E_Mail and not p.ausschließen]
