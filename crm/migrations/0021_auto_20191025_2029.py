# Generated by Django 2.2.4 on 2019-10-25 20:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0020_consent'),
    ]

    operations = [
        migrations.AlterField(
            model_name='formentry',
            name='GravityFormular',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='crm.GravityFormular'),
        ),
    ]
