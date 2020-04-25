# Generated by Django 2.2.10 on 2020-03-01 01:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0054_remove_veranstaltung_html_invitation'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='completed',
            field=models.CharField(help_text='Bezeichnung für erfolgte Mitteilung, z.B. bestätigt', max_length=100, null=True, verbose_name='erfolgt'),
        ),
        migrations.AddField(
            model_name='category',
            name='planned',
            field=models.CharField(help_text='Bezeichnung für geplante Mitteilung, z.B. zu bestätigen', max_length=100, null=True, verbose_name='geplant'),
        ),
    ]
