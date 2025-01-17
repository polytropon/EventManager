# Generated by Django 2.2.4 on 2019-10-08 13:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0007_auto_20190930_1501'),
    ]

    operations = [
        migrations.CreateModel(
            name='RoomType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('abbreviation', models.CharField(help_text='EZ, DZ oder Extern', max_length=20, verbose_name='Kürzel')),
                ('long_text', models.CharField(help_text='i.e. Übernachtung im Einzelzimmer incl. Frühstück', max_length=250, verbose_name='volle Beschreibung')),
            ],
        ),
        migrations.CreateModel(
            name='BookingOption',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price_participant', models.DecimalField(decimal_places=2, max_digits=7, verbose_name='Preis für Teilnehmer')),
                ('formlabel', models.CharField(blank=True, max_length=250, null=True)),
                ('formvalue', models.CharField(blank=True, max_length=250, null=True)),
                ('checkin', models.DateTimeField(blank=True, null=True, verbose_name='Zeitpunkt einchecken')),
                ('checkout', models.DateTimeField(blank=True, null=True, verbose_name='Zeitpunkt auschecken')),
                ('event', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='bookingoptions', to='crm.Veranstaltung', verbose_name='Veranstaltung')),
                ('format', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='bookingoptions', to='crm.Format', verbose_name='Format')),
                ('formentry', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='roombookings', to='crm.FormEntry', verbose_name='Formulareintrag')),
                ('roomtype', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='crm.RoomType', verbose_name='EZ/DZ/Extern')),
            ],
        ),
    ]
