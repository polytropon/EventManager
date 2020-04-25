from celery.task import task
from aldryn_celery.celery import app
import logging
logger = logging.getLogger("telegram_logger")
import os
import telegram
# import time
from crm import *

from django.core import mail


@app.task
def celerymail(*args,**kwargs):
        mail.send_mail(*args,**kwargs)

def send_mail(*args,**kwargs):
        celerymail.delay(*args,**kwargs)        

@app.task()
def sendTelegram(message):
        ## chat_id is integer in url of telegram group
        TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
        bot = telegram.Bot(token=TELEGRAM_TOKEN)
        bot.send_message(chat_id=-464963305, text=message)

@app.task()
def migrate_templates():
        from crm.models import Category,Format,Veranstaltung,DbTemplate,ContentType,TemplateConnection,FormEntry,MessagePart
        if not Category.objects.filter(name="Beschreibung").exists():
                beschreibung_category = Category.objects.create(name="Beschreibung")
        else:
                beschreibung_category = Category.objects.get(name="Beschreibung")

        for o in Format.objects.all():

                content_model = ContentType.objects.get_for_model(FormEntry)

                if o.confirmation:    
                
                        t = DbTemplate.objects.create(
                                content=o.confirmation,
                                category=Category.objects.get(name="Teilnahmebestätigung"),
                                message_part=MessagePart.objects.get(name="Textkörper"),
                                content_model=content_model
                        )

                        TemplateConnection.objects.create(template=t,
                        object_id=o.pk,
                        content_type=ContentType.objects.get_for_model(o))

                
                if o.denial:

                        t = DbTemplate.objects.create(
                                content=o.denial,
                                category=Category.objects.get(name="Absage an TN"),
                                message_part=MessagePart.objects.get(name="Textkörper"),
                                content_model=content_model
                        )

                        TemplateConnection.objects.create(template=t,
                        object_id=o.pk,
                        content_type=ContentType.objects.get_for_model(o))

        for o in Veranstaltung.objects.all():
                content_model = ContentType.objects.get_for_model(FormEntry)

                # if o.confirmation_text:
                #         t = DbTemplate.objects.create(
                #                 content=o.confirmation_text,
                #                 category=Category.objects.get(name="Teilnahmebestätigung"),
                #                 message_part=MessagePart.objects.get(name="Textkörper"),
                #                 content_model=content_model
                #         )

                #         TemplateConnection.objects.create(template=t,
                #         object_id=o.pk,
                #         content_type=ContentType.objects.get_for_model(o))

                if o.Einladungstext:
                        t = DbTemplate.objects.create(
                                content=o.Einladungstext,
                                category=Category.objects.get(name="Einladung"),
                                message_part=MessagePart.objects.get(name="Textkörper"),
                                content_model=content_model
                        )

                        TemplateConnection.objects.create(template=t,
                        object_id=o.pk,
                        content_type=ContentType.objects.get_for_model(o))

                if o.description:
                        t = DbTemplate.objects.create(
                                content=o.description,
                                category=Category.objects.get(name="Beschreibung"),
                                message_part=MessagePart.objects.get(name="Textkörper"),
                                content_model=ContentType.objects.get_for_model(Veranstaltung)
                        )

                        TemplateConnection.objects.create(template=t,
                        object_id=o.pk,
                        content_type=ContentType.objects.get_for_model(o))