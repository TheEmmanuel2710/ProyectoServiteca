# Generated by Django 4.2.3 on 2023-08-18 14:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('appGestionServiteca', '0013_alter_vehiculo_vehmarca_peticionforgot'),
    ]

    operations = [
        migrations.DeleteModel(
            name='PeticionForgot',
        ),
    ]