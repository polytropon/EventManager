# Generated by Django 2.2.4 on 2019-10-08 15:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0011_bookingoption_abbreviation'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bookingoption',
            name='formentry',
        ),
    ]