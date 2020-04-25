# Generated by Django 2.2.4 on 2019-10-18 16:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0015_auto_20191009_2106'),
    ]

    operations = [
        migrations.AlterField(
            model_name='communication',
            name='medium',
            field=models.IntegerField(blank=True, choices=[(1, 'E-Mail'), (2, 'Telefon'), (3, 'Brief'), (4, 'persönlich'), (5, 'sonstiges')], verbose_name='Kommunikationsmittel'),
        ),
    ]
