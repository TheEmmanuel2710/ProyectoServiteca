# Generated by Django 4.2.3 on 2023-10-03 12:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appGestionServiteca', '0023_alter_servicioprestado_serpestado'),
    ]

    operations = [
        migrations.AddField(
            model_name='servicio',
            name='estadoServicio',
            field=models.CharField(choices=[('En Proceso', 'En Proceso'), ('Pendiente', 'Pendiente'), ('Finalizado', 'Finalizado')], db_comment='Estado del servicio', default='Pendiente', max_length=15),
        ),
        migrations.AlterField(
            model_name='servicioprestado',
            name='serpEstado',
            field=models.CharField(choices=[('Cancelado', 'Cancelado'), ('Solicitado', 'Solicitado'), ('Terminado', 'Terminado'), ('Entregado', 'Entregado')], db_comment='Estado del servicio prestado', max_length=15, null=True),
        ),
    ]
