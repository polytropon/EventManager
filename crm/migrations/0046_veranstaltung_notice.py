# Generated by Django 2.2.9 on 2020-01-25 12:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0045_auto_20200125_1143'),
    ]

    operations = [
        migrations.AddField(
            model_name='veranstaltung',
            name='notice',
            field=models.CharField(blank=True, help_text='Organisatorischer Hinweis, z.B. Anmeldung noch nicht möglich', max_length=500, null=True, verbose_name='Hinweis'),
        ),
    ]
