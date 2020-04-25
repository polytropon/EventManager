# Generated by Django 2.2.9 on 2020-02-10 08:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0050_auto_20200210_0826'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='invitationcode',
            options={'verbose_name_plural': 'Einladungscodes'},
        ),
        migrations.AlterField(
            model_name='invitationcode',
            name='registrations_allowed',
            field=models.IntegerField(blank=True, default=0, help_text='Anzahl der Anmeldungen, die mit diesem Code möglich sind. 0 = unbegrenzt.', null=True, verbose_name='erlaubte Anmeldungen'),
        ),
    ]
