from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

# Create your models here.
tipoUsuario = [
    ('Tecnico','Tecnico'),('Asistente', 'Asistente'),('Administrativo','Administrativo'),
]
tipoVehiculo = [
    ('Electrico','Electrico'),('Gasolina', 'Gasolina'),
]
estadoEmpleados = [
    ('Activo','Activo'),('Inactivo', 'Inactivo'),
]
class User(AbstractUser):
    userFoto = models.FileField(upload_to=f"fotos/", null=True, blank=True,db_comment="Foto del Usuario")
    userTipo = models.CharField(max_length=15,choices=tipoUsuario,db_comment="Nombre Tipo de usuario")
    fechaHoraCreacion  = models.DateTimeField(auto_now_add=True,db_comment="Fecha y hora del registro")
    fechaHoraActualizacion = models.DateTimeField(auto_now=True,db_comment="Fecha y hora última actualización")
    
    def __str__(self):
        return f"{self.username}"
        
class Cliente(models.Model):
    identificacion = models.CharField(max_length=55,unique=True, null=False,db_comment="Identificacion del cliente")
    nombres = models.CharField(max_length=55,null=True,db_comment="Nombres del cliente")
    apellidos = models.CharField(max_length=55,null=True,db_comment="Apellidos del cliente")
    correo  = models.CharField(max_length=55,unique=False,db_comment="Correo del cliente")
    numeroCelular = models.CharField(max_length=55,unique=True,null=False,db_comment="Numero de celular del cliente")
    
    def __str__(self):
        return f"{self.nombres} {self.apellidos}"    

class Vehiculo(models.Model):
    placa=models.CharField(max_length=6,unique=True,null=False,db_comment="Placa del vehiculo")
    marca=models.CharField(max_length=15,null=False,db_comment="Marca del vehiculo")
    modelo=models.CharField(max_length=15,null=True,db_comment="Modelo del vehiculo")
    tipo=models.CharField(max_length=15,choices=tipoVehiculo,null=False,db_comment="Tipo de vehiculo")
    
    def __str__(self):
        return f"{self.placa}" 
    
class Empleado(models.Model):
    identificacion = models.CharField(max_length=15,unique=True, null=False,db_comment="Identificacion del empleado")
    nombres = models.CharField(max_length=55,null=True,db_comment="Nombres del empleado")
    apellidos = models.CharField(max_length=55,null=True,db_comment="Apellidos del empleado")
    correo  = models.CharField(max_length=55,unique=False,db_comment="Correo del cliente")
    numeroCelular = models.CharField(max_length=55,unique=True,null=False,db_comment="Numero de celular del empleado")
    cargo = models.CharField(max_length=30,unique=True,null=False,db_comment="Cargo del empleado")
    sueldo = models.IntegerField(null=False,db_comment="Suelo del empleado")
    estado=models.CharField(max_length=15,choices=estadoEmpleados,null=True,db_comment="Estado del empleado")