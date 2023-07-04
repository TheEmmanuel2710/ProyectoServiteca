from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.utils import timezone



tipoUsuario = [
    ('Tecnico','Tecnico'),('Asistente', 'Asistente'),('Administrativo','Administrativo'),
]

tipoVehiculo = [
    ('Electrico','Electrico'),('Gasolina', 'Gasolina'),
]
tipoCodigo=[
    ('SVP','Servicio Prestado')
]
estadoEmpleados = [
    ('Activo','Activo'),('Inactivo', 'Inactivo'),
]
estadoFactura = [
    ('Pagada','Pagada'),('No Pagada', 'No Pagada'),
]

estadoServicioPrestado=[
    ('Cancelado','Cancelado'),('Solicitado','Solicitado'),('Terminado','Terminado'),
    ('Entregado','Entregado')
]

tiposMarcas=[
    ('Toyota','Toyota'),('Nissan','Nissan'),('Mazda','Mazda'),('Hyundai','Hyundai'),
    ('Chevrolet','Chevrolet'),('BMW','BMW'),('Suzuki','Suzuki'),('Ford','Ford'),
    ('Mercedes-Benz','Mercedes-Benz'),('Audi','Audi'),('Renault','Renault'),
    ('Kia','Kia'),('Honda','Honda'),('Jeep','Jeep'),('Volkswagen','Volkswagen')
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
        return f"{self.cliPersona}"    

class Vehiculo(models.Model):
    vehPlaca=models.CharField(max_length=6,unique=True,db_comment="Placa del vehiculo")
    vehMarca=models.CharField(max_length=13,choices=tiposMarcas,db_comment="Marca del vehiculo")
    vehModelo=models.CharField(max_length=15,null=True,db_comment="Modelo del vehiculo")
    vehTipo=models.CharField(max_length=9,choices=tipoVehiculo,db_comment="Tipo de vehiculo")
    
    def __str__(self):
        return f"{self.vehPlaca}" 
    
class Empleado(models.Model):
    empCargo = models.CharField(max_length=30,unique=True,db_comment="Cargo del empleado")
    empSueldo = models.IntegerField(db_comment="Suelo del empleado")
    empEstado=models.CharField(max_length=8,choices=estadoEmpleados,db_comment="Estado del empleado")
    empPersona=models.ForeignKey(Persona,on_delete=models.PROTECT,db_comment="Hace relación a la persona FK")
    
    def __str__(self):
        return f"{self.empPersona}" 

class Servicio(models.Model):
    serNombre=models.CharField(max_length=45,unique=True,db_comment="Nombre del servicio")
    serCosto=models.IntegerField(db_comment="Costo del servicio")
    serFechaInicial=models.DateTimeField(auto_now_add=True,db_comment="Fecha y Hora del servicio")
    serFechaFinal=models.DateTimeField(default=timezone.now(),db_comment="Fecha y Hora ultima actualizacion del servicio")
    
    def __str__(self):
        return f"{self.serNombre}" 

class ServicioPrestado(models.Model):
    serpCli=models.ForeignKey(Cliente,on_delete=models.PROTECT,db_comment="Hace relación al cliente FK")  
    serpVehi=models.ForeignKey(Vehiculo,on_delete=models.PROTECT,db_comment="Hace relación al vehiculo FK")  
    serpEmp=models.ForeignKey(Empleado,on_delete=models.PROTECT,db_comment="Hace relación al empleado FK")  
    serpServicio=models.ForeignKey(Servicio,on_delete=models.PROTECT,db_comment="Hace relación al servicio FK")
    serpEstado=models.CharField(max_length=10,choices=estadoServicioPrestado,db_comment="Estado del Servicio Prestado")
    serpNovedad=models.TextField(null=True,db_comment="Novedad acerca del servicio prestado realizado")
    serpFechaServicio=models.DateTimeField(default=timezone.now(),db_comment="Fecha y Hora ultima actualizacion del servicio prestado")
    
    def __str__(self):
        return f"{self.serpCli} {self.serpVehi} {self.serpEmp} {self.serpServicio}"

class DetalleServicio(models.Model):
    detNovedad=models.TextField(null=True,db_comment="Novedad acerca del detalle del servicio prestado")
    detMonto=models.IntegerField(db_comment="Monto del los servicios prestados solicitados")
    detServicio=models.ForeignKey(Servicio,on_delete=models.PROTECT,db_comment="Hace relación al servicio FK")
    detServicioPrestado=models.ForeignKey(ServicioPrestado,on_delete=models.PROTECT,db_comment="Hace relación al servicio FK")
    
    def __str__(self):
        return f"{self.detServicio} {self.detServicioPrestado}" 
    
class Factura(models.Model):
    facTotal=models.IntegerField(db_comment="Total del costo de todos los servicios prestados.")    
    facEstado=models.CharField(max_length=13,choices=estadoFactura,db_comment="Estado de la factura")
    facServicioPrestado=models.ForeignKey(ServicioPrestado,on_delete=models.PROTECT,db_comment="Hace relación al servicio prestado FK")
    facCodigo=models.CharField(max_length=3, choices=tipoCodigo,db_comment="Codigo factura")
    facFecha=models.DateTimeField(auto_now_add=True,db_comment="Fecha y Hora de la factura")
    
    def __str__(self):
        return f"{self.facServicioPrestado}"