# Generated by Django 4.2.1 on 2023-05-24 18:11

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('appGestionServiteca', '0010_persona_rename_cargo_empleado_empcargo_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Servicio',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('serNombre', models.CharField(db_comment='Nombre del servicio', max_length=45, unique=True)),
                ('serCosto', models.IntegerField(db_comment='Costo del servicio')),
                ('serFechaInicial', models.DateTimeField(auto_now_add=True, db_comment='Fecha y Hora del servicio')),
                ('serFechaFinal', models.DateTimeField(db_comment='Fecha y Hora ultima actualizacion del servicio', default=datetime.datetime(2023, 5, 24, 18, 11, 52, 927808, tzinfo=datetime.timezone.utc))),
            ],
        ),
        migrations.AlterField(
            model_name='cliente',
            name='cliPersona',
            field=models.ForeignKey(db_comment='Hace relación a la persona FK', default=None, on_delete=django.db.models.deletion.PROTECT, to='appGestionServiteca.persona'),
        ),
        migrations.AlterField(
            model_name='empleado',
            name='empEstado',
            field=models.CharField(choices=[('Activo', 'Activo'), ('Inactivo', 'Inactivo')], db_comment='Estado del empleado', max_length=8, null=True),
        ),
        migrations.AlterField(
            model_name='empleado',
            name='empPersona',
            field=models.ForeignKey(db_comment='Hace relación a la persona FK', on_delete=django.db.models.deletion.PROTECT, to='appGestionServiteca.persona'),
        ),
        migrations.AlterField(
            model_name='persona',
            name='perCorreo',
            field=models.CharField(db_comment='Correo de la persona', max_length=55, unique=True),
        ),
        migrations.AlterField(
            model_name='vehiculo',
            name='vehMarca',
            field=models.CharField(choices=[('Toyota', 'Toyota'), ('Nissan', 'Nissan'), ('Mazda', 'Mazda'), ('Hyundai', 'Hyundai'), ('Chevrolet', 'Chevrolet'), ('BMW', 'BMW'), ('Suzuki', 'Suzuki'), ('Ford', 'Ford'), ('Mercedes-Benz', 'Mercedes-Benz'), ('Audi', 'Audi'), ('Renault', 'Renault')], db_comment='Marca del vehiculo', max_length=13),
        ),
        migrations.AlterField(
            model_name='vehiculo',
            name='vehTipo',
            field=models.CharField(choices=[('Electrico', 'Electrico'), ('Gasolina', 'Gasolina')], db_comment='Tipo de vehiculo', max_length=9),
        ),
    ]
