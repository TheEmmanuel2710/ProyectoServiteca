# Generated by Django 4.2.3 on 2023-09-05 20:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('appGestionServiteca', '0020_rename_serpemp_detalleservicioprestado_detempleado'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='userEmpleado',
            field=models.OneToOneField(blank=True, db_comment='Hace referencia al empleado PK', null=True, on_delete=django.db.models.deletion.PROTECT, to='appGestionServiteca.empleado'),
        ),
    ]
