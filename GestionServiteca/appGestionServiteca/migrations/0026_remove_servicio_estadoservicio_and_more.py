# Generated by Django 4.2.3 on 2023-10-03 12:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appGestionServiteca', '0025_alter_servicio_estadoservicio'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='servicio',
            name='estadoServicio',
        ),
        migrations.AddField(
            model_name='servicio',
            name='serEstadoServicio',
            field=models.CharField(choices=[('En Proceso', 'En Proceso'), ('Pendiente', 'Pendiente'), ('Finalizado', 'Finalizado')], db_comment='Estado del servicio', default='Pendiente', max_length=15),
        ),
    ]
