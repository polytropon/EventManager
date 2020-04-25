# Generated by Django 2.2.4 on 2019-09-30 15:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0006_auto_20190919_1249'),
    ]

    operations = [
        migrations.AlterField(
            model_name='formentry',
            name='GravityFormular',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='crm.GravityFormular'),
        ),
        migrations.AlterField(
            model_name='formentry',
            name='Veranstaltung',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='FormEntries', to='crm.Veranstaltung'),
        ),
        migrations.AlterField(
            model_name='formentry',
            name='Zweitperson_Zimmer',
            field=models.CharField(blank=True, help_text="Die Angabe des Teilnehmers aus dem Formular in Textform – soll nicht durch Sachbearbeiter geändert werden. Stattdessen das Auswahlfeld in der Spalte 'Übernachtung' benutzen, um Zimmerpartner für interne Zwecke festzulegen.", max_length=150, null=True),
        ),
        migrations.AlterField(
            model_name='formentry',
            name='room_partner',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='crm.FormEntry', verbose_name='Zweitperson im Zimmer'),
        ),
    ]