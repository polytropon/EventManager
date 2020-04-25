# Generated by Django 2.2.9 on 2020-02-06 11:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0047_bookingoption_public'),
    ]

    operations = [
        migrations.AddField(
            model_name='bookingoption',
            name='end',
            field=models.DateTimeField(blank=True, help_text='Beginn dieser Buchungsoption, falls abweichend von den Daten der Veranstaltung', null=True, verbose_name='Zeitpunkt auschecken'),
        ),
        migrations.AddField(
            model_name='bookingoption',
            name='start',
            field=models.DateTimeField(blank=True, help_text='Beginn dieser Buchungsoption, falls abweichend von den Daten der Veranstaltung', null=True, verbose_name='Zeitpunkt einchecken'),
        ),
    ]