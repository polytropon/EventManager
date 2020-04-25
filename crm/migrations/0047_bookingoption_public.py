# Generated by Django 2.2.9 on 2020-02-06 11:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0046_veranstaltung_notice'),
    ]

    operations = [
        migrations.AddField(
            model_name='bookingoption',
            name='public',
            field=models.BooleanField(default=True, help_text='Wenn angekreuzt, sehen externe Teilnehmer diese Buchungsoption auf der Anmeldungsseite.', verbose_name='Öffentlich einsehbar'),
        ),
    ]