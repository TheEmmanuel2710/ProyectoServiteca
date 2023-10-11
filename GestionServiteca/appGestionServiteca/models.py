from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings


tipoUsuario = [
    ('Tecnico', 'Tecnico'), ('Asistente',
                             'Asistente'), ('Administrativo', 'Administrativo')
]
estadoPeticionForgot = [
    ('Activa', 'Activa'), ('Inactiva', 'Inactiva')
]

tipoVehiculo = [
    ('Electrico', 'Electrico'), ('Gasolina', 'Gasolina')
]
tipoCodigo = [
    ('SVP', 'SVP')
]
estadoEmpleados = [
    ('Activo', 'Activo'), ('Inactivo', 'Inactivo')
]
estadoFactura = [
    ('Pagada', 'Pagada'), ('No Pagada', 'No Pagada')
]

estadoServicioPrestado = [
    ('Cancelado', 'Cancelado'), ('Solicitado',
                                 'Solicitado'), ('Terminado', 'Terminado'),
    ('Entregado', 'Entregado')
]

estadoServicio = [
    ('En Proceso',
     'En Proceso'), ('Asignado', 'Asignado'), ('Finalizado', 'Finalizado')
]

tiposMarcas = [
    ('Toyota', 'Toyota'), ('Nissan', 'Nissan'), ('Mazda',
                                                 'Mazda'), ('Hyundai', 'Hyundai'),
    ('Chevrolet', 'Chevrolet'), ('BMW',
                                 'BMW'), ('Suzuki', 'Suzuki'), ('Ford', 'Ford'),
    ('Mercedes-Benz', 'Mercedes-Benz'), ('Audi', 'Audi'), ('Renault', 'Renault'),
    ('Kia', 'Kia'), ('Honda', 'Honda'), ('Jeep',
                                         'Jeep'), ('Volkswagen', 'Volkswagen'),
    ('Ssangyong', 'Ssangyong'), ('Fiat',
                                 'Fiat'), ('Lexus', 'Lexus'), ('Citroën', 'Citroën'),
    ('Jac', 'Jac'), ('Mitsubishi', 'Mitsubishi'), ('Cadillac',
                                                   'Cadillac'), ('Dodge', 'Dodge')
]


class Persona(models.Model):
    perIdentificacion = models.CharField(
        max_length=10, unique=True, db_comment="Identificacion de la persona")
    perNombres = models.CharField(
        max_length=70, null=True, db_comment="Nombres de la persona")
    perApellidos = models.CharField(
        max_length=70, null=True, db_comment="Apellidos de la persona")
    perCorreo = models.CharField(
        max_length=70, unique=True, db_comment="Correo de la persona")
    perNumeroCelular = models.CharField(
        max_length=10, unique=True, db_comment="Numero de celular de la persona")

    def __str__(self):
        return f"Identificacion:{self.perIdentificacion} -Nombres: {self.perNombres} -Apellidos:{self.perApellidos} -Correo:{self.perCorreo} -Celular:{self.perNumeroCelular}"


class Empleado(models.Model):
    empCargo = models.CharField(
        max_length=30, unique=True, db_comment="Cargo del empleado")
    empSueldo = models.IntegerField(db_comment="Suelo del empleado")
    empEstado = models.CharField(
        max_length=8, null=True, choices=estadoEmpleados, db_comment="Estado del empleado")
    empPersona = models.ForeignKey(
        Persona, on_delete=models.PROTECT, db_comment="Hace relación a la persona FK")

    def __str__(self):
        return f"Empleado: {self.empPersona.perNombres} {self.empPersona.perApellidos}"


class User(AbstractUser):
    userFoto = models.FileField(
        upload_to=f"fotos/", null=True, blank=True, db_comment="Foto del Usuario")
    userTipo = models.CharField(
        max_length=15, choices=tipoUsuario, db_comment="Nombre Tipo de usuario")
    userEmpleado = models.OneToOneField(
        Empleado, on_delete=models.PROTECT, null=True, blank=True, db_comment="Hace referencia al empleado PK")
    fechaHoraCreacion = models.DateTimeField(
        auto_now_add=True, db_comment="Fecha y hora del registro")
    fechaHoraActualizacion = models.DateTimeField(
        auto_now=True, db_comment="Fecha y hora última actualización")

    def __str__(self):
        return f"{self.username}"


class PeticionForgot(models.Model):
    id_user = models.ForeignKey(
        User, on_delete=models.PROTECT, db_comment="Hace relación al usuario FK")
    fechaHoraCreacion = models.DateTimeField(
        auto_now_add=True, db_comment="Fecha y hora del registro de la peticion forgot")
    estado = models.CharField(max_length=27, choices=estadoPeticionForgot,
                              default='Activa', db_comment="Estado de la peticion forgot")

    def __str__(self):
        return f"Usuario: {self.id_user}"


class Cliente(models.Model):
    cliDireccion = models.CharField(
        max_length=72, null=True, db_comment="Direccion del cliente")
    cliPersona = models.ForeignKey(
        Persona, on_delete=models.PROTECT, db_comment="Hace relación a la persona FK")

    def __str__(self):
        return f"Cliente: {self.cliPersona.perNombres} {self.cliPersona.perApellidos}"


class Vehiculo(models.Model):
    vehPlaca = models.CharField(
        max_length=6, unique=True, db_comment="Placa del vehiculo")
    vehMarca = models.CharField(
        max_length=27, choices=tiposMarcas, db_comment="Marca del vehiculo")
    vehModelo = models.IntegerField(
        null=True, db_comment="Modelo del vehiculo")
    vehTipo = models.CharField(
        max_length=9, choices=tipoVehiculo, db_comment="Tipo de vehiculo")

    def __str__(self):
        return f"Vehiculo: {self.vehPlaca}"


class Servicio(models.Model):
    serNombre = models.CharField(
        max_length=50, unique=True, db_comment="Nombre del servicio")
    serCosto = models.IntegerField(db_comment="Costo del servicio")
    serFechaInicial = models.DateTimeField(
        auto_now_add=True, db_comment="Fecha y Hora del servicio")
    serFechaFinal = models.DateTimeField(
        auto_now_add=True, db_comment="Fecha y Hora ultima actualizacion del servicio")

    def __str__(self):
        return f"{self.serNombre}"


class ServicioPrestado(models.Model):
    serpCli = models.ForeignKey(
        Cliente, on_delete=models.PROTECT, db_comment="Hace relación al cliente FK")
    serpVehi = models.ForeignKey(
        Vehiculo, on_delete=models.PROTECT, db_comment="Hace relación al vehiculo FK")
    serpEstado = models.CharField(
        max_length=15, choices=estadoServicioPrestado, null=True, db_comment="Estado del servicio prestado")
    serpObservaciones = models.TextField(
        null=True, db_comment="Novedad acerca del servicio prestado realizado")
    serpFechaServicio = models.DateTimeField(
        auto_now_add=True, db_comment="Fecha y Hora ultima actualizacion del servicio prestado")

    def __str__(self):
        return f"{self.serpCli} {self.serpVehi}"


class DetalleServicioPrestado(models.Model):
    detServicio = models.ForeignKey(
        Servicio, on_delete=models.PROTECT, db_comment="Hace relación al servicio FK")
    detServicioPrestado = models.ForeignKey(
        ServicioPrestado, on_delete=models.PROTECT, db_comment="Hace relación al servicio FK")
    detEmpleado = models.ForeignKey(
        Empleado, on_delete=models.PROTECT, db_comment="Hace relación al empleado FK")
    detEstadoServicio = models.CharField(
        max_length=10, null=True, default='Asignado', choices=estadoServicio, db_comment="Estado del servicio")
    detObservaciones = models.TextField(
        null=True, db_comment="Observaciones acerca del servicio prestado realizado")

    def __str__(self):
        return f"{self.detServicio} {self.detServicioPrestado}"


class Factura(models.Model):
    facTotal = models.IntegerField(
        db_comment="Total del costo de todos los servicios prestados.")
    facEstado = models.CharField(
        max_length=13, choices=estadoFactura, db_comment="Estado de la factura")
    facServicioPrestado = models.ForeignKey(
        ServicioPrestado, on_delete=models.PROTECT, db_comment="Hace relación al servicio prestado FK")
    facCodigo = models.CharField(
        max_length=10, choices=tipoCodigo, db_comment="Codigo factura")
    facFecha = models.DateTimeField(
        auto_now_add=True, db_comment="Fecha y Hora de la factura")

    def __str__(self):
        return f"{self.facServicioPrestado}"
