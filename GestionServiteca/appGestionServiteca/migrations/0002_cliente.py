# Generated by Django 4.2.1 on 2023-05-12 17:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appGestionServiteca', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cliente',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('identificacion', models.CharField(db_comment='Identificacion del cliente', max_length=55, unique=True)),
                ('nombreC', models.CharField(db_comment='Nombre del cliente', max_length=55)),
                ('correo', models.CharField(db_comment='Correo del cliente', max_length=55, unique=True)),
                ('numeroCelular', models.CharField(db_comment='Fecha y hora última actualización', max_length=55, unique=True)),
            ],
        ),
    ]
