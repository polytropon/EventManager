# Generated by Django 2.2.4 on 2019-09-18 09:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0004_auto_20190916_1803'),
    ]

    operations = [
        migrations.AddField(
            model_name='veranstaltung',
            name='participant_list',
            field=models.FileField(blank=True, help_text='Hier die Teilnehmerliste nach einer Veranstaltung für Dokumentationszwecke hochladen.', upload_to='', verbose_name='Teilnehmerliste'),
        ),
    ]
