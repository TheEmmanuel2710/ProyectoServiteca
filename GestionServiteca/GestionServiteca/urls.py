"""
URL configuration for GestionServiteca project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from appGestionServiteca import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',include('appGestionServiteca.urls')),
    path('',views.inicio),
    path('inicioAdministrador/',views.inicioAdministrador),
    path('vistaRegistrarUsuario/',views.vistaRegistrarUsuario),
    path('vistaGestionarUsuarios/',views.vistaGestionarUsuarios),
    path('registrarUsuario/',views.registrarUsuario),
    path('vistaGestionarEmpleados/',views.vistaGestionarEmpleados),
    path('vistaRegistrarEmpleado/',views.vistaRegistrarEmpleados),
    path('registrarEmpleado/',views.registrarEmpleado),
    path('consultarE/<int:id>/', views.consultarEmpleado, name='consultar_empleado_por_id'),
    path('inicioAsistente/',views.inicioAsistente),
    path('vistaGestionarClientes/',views.vistaGestionarClientes),
    path('vistaRegistrarCliente/',views.vistaRegistrarClientes),
    path('registrarCliente/',views.registrarCliente),
    path('consultarC/<int:id>/', views.consultarCliente, name='consultar_cliente_por_id'),
    path('ActualizarC/', views.actualizarCliente),
    path('vistaGestionarVehiculos/',views.vistaGestionarVehiculos),
    path('vistaRegistrarVehiculo/',views.vistaRegistrarVehiculos),
    path('registrarVehiculo/',views.registrarVehiculo),
    path('consultarV/<int:id>/', views.consultarVehiculo, name='consultar_vehiculo_por_id'),
    path('ActualizarV/', views.actualizarVehiculo),
    path('registrarServicioPrestado/',views.registrarServicioPrestado),
    path('vistaRegistrarServiciosP/',views.vistaRegistrarServiciosPrestados),
    path('vistaGestionarFacturas/',views.vistaGestionarFacturas),
    path('inicioTecnico/',views.inicioTecnico),
    path('vistaGestionarSolicitudesV/',views.vistaGestionarSolicitudesV),  
    path('login/',views.login),
    path('vistaLogin/',views.vistaLogin),
    path('salir/',views.salir),
    
]
if settings.DEBUG:
    urlpatterns += static (settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)