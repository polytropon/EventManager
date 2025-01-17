# Generated by Django 2.2.10 on 2020-03-19 13:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0059_auto_20200308_0814'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bookingoption',
            name='roomtype',
            field=models.ForeignKey(help_text='Diese Auswahl bedingt die Anzahl der Teilnehmer, die mit einer Buchung verbunden sind.', null=True, on_delete=django.db.models.deletion.CASCADE, to='crm.RoomType', verbose_name='EZ/DZ/Extern'),
        ),
        migrations.AlterField(
            model_name='category',
            name='completed',
            field=models.CharField(help_text='Bezeichnung für erfolgte Mitteilung, z.B. bestätigt', max_length=100, null=True, verbose_name='erfolgt'),
        ),
        migrations.AlterField(
            model_name='category',
            name='planned',
            field=models.CharField(help_text='Bezeichnung für geplante Mitteilung, z.B. zu bestätigen', max_length=100, null=True, verbose_name='geplant'),
        ),
    ]
