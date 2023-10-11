# Generated by Django 4.2.3 on 2023-10-05 11:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appGestionServiteca', '0030_remove_empleado_empterminoservicio'),
    ]

    operations = [
        migrations.AddField(
            model_name='detalleservicioprestado',
            name='detEstadoServicio',
            field=models.CharField(choices=[('En Proceso', 'En Proceso'), ('Asignado', 'Asignado'), ('Finalizado', 'Finalizado')], db_comment='Estado del servicio', default='Asignado', max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='servicioprestado',
            name='serpEstado',
            field=models.CharField(choices=[('Cancelado', 'Cancelado'), ('Solicitado', 'Solicitado'), ('Terminado', 'Terminado'), ('Entregado', 'Entregado')], db_comment='Estado del servicio prestado', max_length=15, null=True),
        ),
    ]
