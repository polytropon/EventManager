# Generated by Django 2.2.4 on 2019-09-19 12:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0005_veranstaltung_participant_list'),
    ]

    operations = [
        migrations.AlterField(
            model_name='formentry',
            name='Einladungscode',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
