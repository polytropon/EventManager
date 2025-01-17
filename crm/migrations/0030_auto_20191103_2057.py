# Generated by Django 2.2.4 on 2019-11-03 20:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0029_modul_format'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dbtemplate',
            name='category',
            field=models.ForeignKey(help_text='z.B. Einladung, Eingangsvermerk, Teilnahmebestätigung', on_delete=django.db.models.deletion.CASCADE, to='crm.Category', verbose_name='Kategorie'),
        ),
        migrations.AlterField(
            model_name='dbtemplate',
            name='message_part',
            field=models.ForeignKey(help_text='Teil der Nachricht, z.B. Betreffzeile, Textkörper', on_delete=django.db.models.deletion.CASCADE, to='crm.MessagePart', verbose_name='Nachrichtenteil'),
        ),
    ]
