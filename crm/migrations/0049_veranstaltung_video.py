# Generated by Django 2.2.9 on 2020-02-09 11:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0048_auto_20200206_1124'),
    ]

    operations = [
        migrations.AddField(
            model_name='veranstaltung',
            name='video',
            field=models.CharField(blank=True, help_text='Link zum Video auf externer Seite, wird in externer Übersicht eingebunden, wenn vorhanden.', max_length=100, verbose_name='Link zum Video'),
        ),
    ]
