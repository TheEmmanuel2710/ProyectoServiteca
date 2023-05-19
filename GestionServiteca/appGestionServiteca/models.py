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
        
class Persona(models.Model):
    perIdentificacion = models.CharField(max_length=15,unique=True,db_comment="Identificacion de la persona")
    perNombres = models.CharField(max_length=55,db_comment="Nombres de la persona")
    perApellidos = models.CharField(max_length=55,db_comment="Apellidos de la persona")
    perCorreo  = models.CharField(max_length=55,unique=True,db_comment="Correo de la persona")
    perNumeroCelular = models.CharField(max_length=55,unique=True,db_comment="Numero de celular de la persona")   

class Cliente(models.Model):
    cliDireccion  = models.CharField(max_length=55,unique=False,null=True,db_comment="Direccion del cliente")
    cliPersona=models.ForeignKey(Persona,on_delete=models.PROTECT,db_comment="Hace relación a la persona FK")
    def __str__(self):
        return f"{self.cliDireccion}"    

class Vehiculo(models.Model):
    vehPlaca=models.CharField(max_length=6,unique=True,db_comment="Placa del vehiculo")
    vehMarca=models.CharField(max_length=15,db_comment="Marca del vehiculo")
    vehModelo=models.CharField(max_length=15,null=True,db_comment="Modelo del vehiculo")
    vehTipo=models.CharField(max_length=15,choices=tipoVehiculo,db_comment="Tipo de vehiculo")
    
    def __str__(self):
        return f"{self.vehPlaca}" 
    
class Empleado(models.Model):
    empCargo = models.CharField(max_length=30,unique=True,db_comment="Cargo del empleado")
    empSueldo = models.IntegerField(null=False,db_comment="Suelo del empleado")
    empEstado=models.CharField(max_length=15,choices=estadoEmpleados,db_comment="Estado del empleado")
    empPersona=models.ForeignKey(Persona,on_delete=models.PROTECT,db_comment="Hace relación a la persona FK")
 
