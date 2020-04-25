# Generated by Django 2.2.10 on 2020-03-03 11:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0055_auto_20200301_0122'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='completed',
            field=models.CharField(default='', help_text='Bezeichnung für erfolgte Mitteilung, z.B. bestätigt', max_length=100, unique=False, verbose_name='erfolgt'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='category',
            name='name',
            field=models.CharField(help_text='Name der Kategorie', max_length=100, unique=True, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='category',
            name='planned',
            field=models.CharField(default='', help_text='Bezeichnung für geplante Mitteilung, z.B. zu bestätigen', max_length=100, unique=False, verbose_name='geplant'),
            preserve_default=False,
        ),
    ]
