# Generated by Django 2.2.10 on 2020-02-28 18:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0053_veranstaltung_html_invitation'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='veranstaltung',
            name='html_invitation',
        ),
    ]
