# Generated by Django 2.2.4 on 2019-10-08 14:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0009_bookingoption_nights'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bookingoption',
            name='formentry',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='bookingoptions', to='crm.FormEntry', verbose_name='Formulareintrag'),
        ),
    ]
