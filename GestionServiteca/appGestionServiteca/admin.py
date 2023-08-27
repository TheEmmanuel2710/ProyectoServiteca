from django.contrib import admin
from appGestionServiteca.models import *
# Register your models here.
admin.site.register(User)
admin.site.register(Cliente)
admin.site.register(Vehiculo)
admin.site.register(Persona)
admin.site.register(Empleado)
admin.site.register(Servicio)
admin.site.register(ServicioPrestado)
admin.site.register(DetalleServicioPrestado)
admin.site.register(Factura)
admin.site.register(PeticionForgot)
