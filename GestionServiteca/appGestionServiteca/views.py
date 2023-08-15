from django.shortcuts import render,redirect,get_object_or_404
from appGestionServiteca.models import *
from django.contrib.auth.models import Group
from django.db import transaction
import random
import string
from django.contrib.auth import authenticate
from django.contrib import auth
from django.conf import settings
import urllib
import json
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
import threading
from django.http import JsonResponse
from smtplib import SMTPException
from rest_framework import generics
from appGestionServiteca.serializers import PersonaSerializer,ClienteSerializer
import matplotlib.pyplot as plt
import matplotlib
from fpdf import FPDF
from datetime import datetime
import os


datosSesion={"user":None,"rutaFoto":None, "rol":None}


def redireccionar(request, cualquier_cosa):
    mensaje2 = "URL NO ENCONTRADA"
    if not request.user.is_authenticated:
        return render(request,"inicio.html", {"mensaje2": mensaje2})
    if request.user.groups.filter(name='Asistente').exists():
        return render(request, "asistente/inicio.html", {"mensaje2": mensaje2})
    elif request.user.groups.filter(name='Administrador').exists():
         return render(request, "administrador/inicio.html", {"mensaje2": mensaje2})
    elif request.user.groups.filter(name='Tecnico').exists():
         return render(request, "tecnico/inicio.html", {"mensaje2": mensaje2})

        


def inicio(request):
    return render(request, 'inicio.html')


def inicioAdministrador(request):
    if not request.user.is_authenticated:
        mensaje = "Debe iniciar sesión"
        return render(request, "inicio.html", {"mensaje": mensaje})

    if request.user.groups.filter(name='Administrador').exists():
        datos_sesion = {"user": request.user}
        return render(request, "administrador/inicio.html", datos_sesion)
    
    mensaje = "Nuestro sistema detecta que su rol no cuenta con los permisos necesarios para acceder a esta url."
    
    if request.user.groups.filter(name='Asistente').exists():
        return render(request, "asistente/inicio.html", {"mensaje": mensaje})
    elif request.user.groups.filter(name='Tecnico').exists():
        return render(request, "tecnico/inicio.html", {"mensaje": mensaje})


def inicioAsistente(request):
    if not request.user.is_authenticated:
        mensaje = "Debe iniciar sesión"
        return render(request, "inicio.html", {"mensaje": mensaje})

    if request.user.groups.filter(name='Asistente').exists():
        datos_sesion = {"user": request.user}
        return render(request, "asistente/inicio.html", datos_sesion)
    
    mensaje = "Nuestro sistema detecta que su rol no cuenta con los permisos necesarios para acceder a esta url."

    if request.user.groups.filter(name='Administrador').exists():
        return render(request, "administrador/inicio.html", {"mensaje": mensaje})
    elif request.user.groups.filter(name='Tecnico').exists():
        return render(request, "tecnico/inicio.html", {"mensaje": mensaje})


def inicioTecnico(request):
    if not request.user.is_authenticated:
        mensaje = "Debe iniciar sesión"
        return render(request, "inicio.html", {"mensaje": mensaje})

    if request.user.groups.filter(name='Tecnico').exists():
        datos_sesion = {"user": request.user}
        return render(request, "tecnico/inicio.html", datos_sesion)
    
    mensaje = "Nuestro sistema detecta que su rol no cuenta con los permisos necesarios para acceder a esta url."

    if request.user.groups.filter(name='Administrador').exists():
        return render(request, "administrador/inicio.html", {"mensaje": mensaje})
    elif request.user.groups.filter(name='Asistente').exists():
        return render(request, "asistente/inicio.html", {"mensaje": mensaje})


def vistaGestionarUsuarios(request):
    user = request.user

    if user.groups.filter(name='Administrador').exists():
        usuarios = User.objects.all()
        retorno = {"usuarios": usuarios, "user": user}
        return render(request, "administrador/vistaGestionarUsuarios.html", retorno)
    
    mensaje = "Nuestro sistema detecta que su rol no cuenta con los permisos necesarios para acceder a esta url."
    
    if user.groups.filter(name='Asistente').exists():
        return render(request, "asistente/inicio.html", {"mensaje": mensaje})
    elif user.groups.filter(name='Tecnico').exists():
        return render(request, "tecnico/inicio.html", {"mensaje": mensaje})

    return render(request, "inicio.html", {"mensaje": "Debe iniciar sesión"})
    
       
def vistaRegistrarUsuario(request):
    user = request.user
    
    if user.groups.filter(name='Administrador').exists():
        roles = Group.objects.all()
        return render(request, "administrador/frmRegistrarUsuario.html", {"roles": roles, "tipoUsuario":tipoUsuario, "user": user})
    
    mensaje = "Nuestro sistema detecta que su rol no cuenta con los permisos necesarios para acceder a esta url."
    
    if request.user.groups.filter(name='Tecnico').exists():
        return render(request, "tecnico/inicio.html", {"mensaje": mensaje})
    elif request.user.groups.filter(name='Asistente').exists():
        return render(request, "asistente/inicio.html", {"mensaje": mensaje})

    return render(request, "inicio.html", {"mensaje": "Debe iniciar sesión"})


def registrarUsuario(request):
    try:
        nombres = request.POST.get("txtNombres")
        apellidos = request.POST.get("txtApellidos")
        correo = request.POST.get("txtCorreo")
        tipo = request.POST.get("cbTipo")
        foto = request.FILES.get("fileFoto",False)
        idRol = int(request.POST.get("cbRol"))

        with transaction.atomic():
            # Crear un objeto de tipo User
            user = User(username=correo, first_name=nombres, last_name=apellidos, email=correo, userTipo=tipo, userFoto=foto)
            user.save()
            
            # Obtener el Rol de acuerdo al id del rol
            rol = Group.objects.get(pk=idRol)
            # Agregar el usuario a ese Rol
            user.groups.add(rol)
            
            # Si el rol es Administrador, habilitar el acceso al sitio web del administrador
            if rol.name == "Administrador":
                user.is_staff = True
            
            # Generar y asignar contraseña al usuario
            passwordGenerado = generarPassword()
            user.set_password(passwordGenerado)
            user.save()
            
            mensaje = "Usuario Agregado Correctamente"
            retorno = {"mensaje": mensaje}
            
            # Enviar correo al usuario en un hilo separado
            asunto = 'Registro Sistema Serviteca'
            mensaje = f'Cordial saludo, <b>{user.first_name} {user.last_name}</b>, nos permitimos.\
                informarle que usted ha sido registrado en el Sistema de ServitecaOpita.\
                Nos permitimos enviarle las credenciales de Ingreso a nuestro sistema.<br>\
                <br><b>Username: </b> {user.username}\
                <br><b>Password: </b> {passwordGenerado}\
                <br><br>Lo invitamos a ingresar a nuestro sistema en la url:\
                http://serviteca.pythonanywhere.com'
            
            thread = threading.Thread(target=enviarCorreo, args=(asunto, mensaje, user.email))
            thread.start()
            
            return redirect("/vistaGestionarUsuarios/", retorno)
    
    except Exception as error:
        transaction.rollback()
        mensaje = "Error al agregar usuario,datos duplicados."
    
    retorno = {"mensaje": mensaje}
    return render(request, "administrador/frmRegistrarUsuario.html", retorno)


def vistaGestionarClientes(request):
    user = request.user

    if user.groups.filter(name='Asistente').exists():
        clientes = Cliente.objects.all()
        retorno = {"clientes": clientes, "user": user}
        return render(request, "asistente/vistaGestionarClientes.html", retorno)
    
    mensaje = "Nuestro sistema detecta que su rol no cuenta con los permisos necesarios para acceder a esta url."
    
    if request.user.groups.filter(name='Administrador').exists():
        return render(request, "administrador/inicio.html", {"mensaje": mensaje})
    elif request.user.groups.filter(name='Tecnico').exists():
        return render(request, "tecnico/inicio.html", {"mensaje": mensaje})

    return render(request, "inicio.html", {"mensaje": "Debe iniciar sesión"})


def vistaRegistrarClientes(request):
    user = request.user

    if user.groups.filter(name='Asistente').exists():
        retorno = {"user": user}
        return render(request, "asistente/frmRegistrarCliente.html", retorno)
    
    mensaje = "Nuestro sistema detecta que su rol no cuenta con los permisos necesarios para acceder a esta url."
    
    if request.user.groups.filter(name='Administrador').exists():
        return render(request, "administrador/inicio.html", {"mensaje": mensaje})
    elif request.user.groups.filter(name='Tecnico').exists():
        return render(request, "tecnico/inicio.html", {"mensaje": mensaje})

    return render(request, "inicio.html", {"mensaje": "Debe iniciar sesión"})

def registrarCliente(request):
    estado = False
    try:
        identificacion = request.POST.get("txtIdentificacion")
        nombres = request.POST.get("txtNombres")
        apellidos = request.POST.get("txtApellidos")
        correo = request.POST.get("txtCorreo")
        numeroC = request.POST.get("txtNumeroC")
        direccion = request.POST.get("txtDireccion")
        
        with transaction.atomic():
            persona = Persona(perIdentificacion=identificacion, perNombres=nombres, perApellidos=apellidos, perCorreo=correo, perNumeroCelular=numeroC)
            persona.save()
            
            cliente = Cliente(cliDireccion=direccion, cliPersona=persona)
            cliente.save()
            
            estado = True
            mensaje = "Cliente Agregado Correctamente"
    except Exception as error:
        transaction.rollback()
        mensaje = "Error al registrar cliente: Datos duplicados."
    
    retorno = {"mensaje": mensaje, "estado": estado, "user": request.user}
    return render(request, "asistente/frmRegistrarCliente.html", retorno)

def consultarCliente(request, id):
    try:
        cliente = Cliente.objects.get(pk=int(id))
        persona = cliente.cliPersona
        datos_cliente = {
            "id": cliente.id,
            "cliPersona": {
                "perIdentificacion": persona.perIdentificacion,
                "perNombres": persona.perNombres,
                "perApellidos": persona.perApellidos,
                "perCorreo": persona.perCorreo,
                "perNumeroCelular": persona.perNumeroCelular,
            },
            "cliDireccion": cliente.cliDireccion,
        }
        return JsonResponse({"cliente": datos_cliente})
    except Cliente.DoesNotExist:
        return JsonResponse({"error": "Cliente no encontrado"}, status=404)
    except Persona.DoesNotExist:
        return JsonResponse({"error": "Persona no encontrada"}, status=404)
    except ValueError:
        return JsonResponse({"error": "ID inválido"}, status=400)
    except Exception as error:
        return JsonResponse({"error": str(error)}, status=500)
    
def vistaGestionarVehiculos(request):
    user = request.user

    if user.groups.filter(name='Asistente').exists():
        vehiculos = Vehiculo.objects.all()
        retorno = {"vehiculos": vehiculos, "tipoVeh": tipoVehiculo, "tipoMar": tiposMarcas,"user": user}
        return render(request, "asistente/vistaGestionarVehiculos.html", retorno)

    mensaje = "Nuestro sistema detecta que su rol no cuenta con los permisos necesarios para acceder a esta url."

    if user.groups.filter(name='Administrador').exists():
        return render(request, "administrador/inicio.html", {"mensaje": mensaje})
    elif user.groups.filter(name='Tecnico').exists():
        return render(request, "tecnico/inicio.html", {"mensaje": mensaje})

    return render(request, "inicio.html", {"mensaje": "Debe iniciar sesión"})

def vistaRegistrarVehiculos(request):
    user = request.user

    if user.groups.filter(name='Asistente').exists():
        retorno = {"user": user, "tipoVeh": tipoVehiculo, "tipoMar": tiposMarcas}
        return render(request, "asistente/frmRegistrarVehiculo.html", retorno)

    mensaje = "Nuestro sistema detecta que su rol no cuenta con los permisos necesarios para acceder a esta url."

    if user.groups.filter(name='Administrador').exists():
        return render(request, "administrador/inicio.html", {"mensaje": mensaje})
    elif user.groups.filter(name='Tecnico').exists():
        return render(request, "tecnico/inicio.html", {"mensaje": mensaje})

    return render(request, "inicio.html", {"mensaje": "Debe iniciar sesión"})

def registrarVehiculo(request):
    estado = False
    try:
        placa = request.POST.get("txtPlaca")
        marca = request.POST.get("cbMarca")
        modelo = request.POST.get("txtModelo")
        tipoV = request.POST.get("cbTipoV")
        
        with transaction.atomic():
            vehiculo = Vehiculo(vehPlaca=placa, vehMarca=marca, vehModelo=modelo, vehTipo=tipoV)
            vehiculo.save()
            
            estado = True
            mensaje = "Vehiculo Agregado Correctamente"
    except Exception as error:
        transaction.rollback()
        mensaje = "Error al registrar vehiculo: Datos duplicados."
    
    retorno = {"mensaje": mensaje, "estado": estado, "user": request.user}
    return render(request, "asistente/frmRegistrarVehiculo.html", retorno)

def consultarVehiculo(request, id):
    try:
        vehiculo = Vehiculo.objects.get(id=id)  # Buscar vehiculo por su id
        datos_vehiculo = {
            "id": vehiculo.id,
            "vehPlaca": vehiculo.vehPlaca,
            "vehMarca": vehiculo.vehMarca,
            "vehModelo": vehiculo.vehModelo,
            "vehTipo": vehiculo.vehTipo
        }
        return JsonResponse({"vehiculo": datos_vehiculo})
    except Vehiculo.DoesNotExist:
        return JsonResponse({"error": "Vehiculo no encontrado"}, status=404)
    except ValueError:
        return JsonResponse({"error": "ID inválido"}, status=400)
    except Exception as error:
        return JsonResponse({"error": str(error)}, status=500)


def generarPassword():
    """
    Genera un password de longitud de 10 que incluye letras mayusculas
    y minusculas,digitos y cararcteres especiales
    Returns:
        _str_: retorna un password
    """
    longitud = 10
    
    caracteres = string.ascii_lowercase + string.ascii_uppercase + string.digits + string.punctuation
    password = ''
    
    for i in range(longitud):
        password +=''.join(random.choice(caracteres))
    return password


def vistaGestionarEmpleados(request):
    user = request.user

    if user.groups.filter(name='Administrador').exists():
        empleados = Empleado.objects.all()
        retorno = {"empleados": empleados,"estadoEmpl": estadoEmpleados, "user": user}
        return render(request, "administrador/vistaGestionarEmpleados.html", retorno)

    mensaje = "Nuestro sistema detecta que su rol no cuenta con los permisos necesarios para acceder a esta url."

    if user.groups.filter(name='Asistente').exists():
        return render(request, "asistente/inicio.html", {"mensaje": mensaje})
    
    if user.groups.filter(name='Tecnico').exists():
        return render(request, "tecnico/inicio.html", {"mensaje": mensaje})

    return render(request, "inicio.html", {"mensaje": "Debe iniciar sesión"})


def vistaRegistrarEmpleados(request):
    user = request.user

    if user.groups.filter(name='Administrador').exists():
        retorno = {"user": user, "estadoEmpl": estadoEmpleados}
        return render(request, "administrador/frmRegistrarEmpleado.html", retorno)

    mensaje = "Nuestro sistema detecta que su rol no cuenta con los permisos necesarios para acceder a esta url."

    if user.groups.filter(name='Asistente').exists():
        return render(request, "asistente/inicio.html", {"mensaje": mensaje})
    
    if user.groups.filter(name='Tecnico').exists():
        return render(request, "tecnico/inicio.html", {"mensaje": mensaje})

    return render(request, "inicio.html", {"mensaje": "Debe iniciar sesión"})


def registrarEmpleado(request):
    estado = False
    try:
        identificacion = request.POST.get("txtIdentificacion")
        nombres = request.POST.get("txtNombres")
        apellidos = request.POST.get("txtApellidos")
        correo = request.POST.get("txtCorreo")
        numeroC = request.POST.get("txtNumeroC")
        cargo = request.POST.get("txtCargo")
        sueldo = request.POST.get("txtSueldo")
        estadoE = request.POST.get("cbEstado")

        with transaction.atomic():
            persona = Persona(perIdentificacion=identificacion, perNombres=nombres, perApellidos=apellidos, perCorreo=correo, perNumeroCelular=numeroC)
            persona.save()
            empleado = Empleado(empCargo=cargo, empSueldo=sueldo, empEstado=estadoE, empPersona=persona)
            empleado.save()

            estado = True
            mensaje = "Empleado Agregado Correctamente"
    except Exception as error:
        transaction.rollback()
        mensaje = "Error al registrar empleado: Datos duplicados."

    retorno = {"mensaje": mensaje, "estado": estado}
    return render(request, "administrador/frmRegistrarEmpleado.html", retorno)


def consultarEmpleado(request, id):
    try:
        empleado = Empleado.objects.get(pk=int(id))  # Buscar empleado por ID de Persona
        persona = empleado.empPersona

        datos_empleado = {
            "id": empleado.id,
            "empPersona": {
                "perIdentificacion": persona.perIdentificacion,
                "perNombres": persona.perNombres,
                "perApellidos": persona.perApellidos,
                "perCorreo": persona.perCorreo,
                "perNumeroCelular": persona.perNumeroCelular,
            },
            "empCargo": empleado.empCargo,
            "empSueldo": empleado.empSueldo,
            "empEstado": empleado.empEstado,
        }
        return JsonResponse({"empleado": datos_empleado})
    except Empleado.DoesNotExist:
        return JsonResponse({"error": "Empleado no encontrado"}, status=404)
    except Persona.DoesNotExist:
        return JsonResponse({"error": "Persona no encontrada"}, status=404)
    except ValueError:
        return JsonResponse({"error": "ID inválido"}, status=400)
    except Exception as error:
        return JsonResponse({"error": str(error)}, status=500)


def vistaLogin(request):
    return render(request,"menu.html")


def login(request):
    #validar el recapthcha
    """Begin reCAPTCHA validation"""
    recaptcha_response = request.POST.get('g-recaptcha-response')
    url = 'https://www.google.com/recaptcha/api/siteverify'
    values = {
        'secret': settings.GOOGLE_RECAPTCHA_SECRET_KEY, 
        'response': recaptcha_response
    }
    data = urllib.parse.urlencode(values).encode()
    req = urllib.request.Request(url, data=data)
    response = urllib.request.urlopen(req)
    result = json.loads(response.read().decode()) 
    print (result)
    """ End reCAPTCHA validation """
    if result['success']:
        username= request.POST["txtUsername"] 
        password = request.POST["txtPassword"]
        user = authenticate(username=username, password=password)
        print (user)
        if user is not None:
            #registrar la variable de sesión
            auth.login(request, user)
            if user.groups.filter(name='Administrador').exists():
                return redirect('/inicioAdministrador')
            elif user.groups.filter(name='Asistente').exists():
                return redirect('/inicioAsistente')
            else:
                return redirect('/inicioTecnico')
        else:
            mensaje = "Usuario o Contraseña Incorrectas"
            return render(request, "inicio.html",{"mensaje":mensaje})
    else:
        mensaje="Debe validar primero el recaptcha"
        return render(request, "inicio.html",{"mensaje" :mensaje})
 
    
def salir(request):
    auth.logout(request)
    return render(request, "inicio.html",
                  {"mensaje":"Ha cerrado la sesión"})
  
    
def enviarCorreo (asunto=None, mensaje=None, destinatario=None): 
    remitente = settings.EMAIL_HOST_USER 
    template = get_template('enviarCorreo.html')
    contenido = template.render({
        'destinatario': destinatario,
        'mensaje': mensaje,
        'asunto': asunto,
        'remitente': remitente,
    })
    try:
        correo = EmailMultiAlternatives (asunto, mensaje, remitente, [destinatario]) 
        correo.attach_alternative (contenido, 'text/html') 
        correo.send(fail_silently=True)
    except SMTPException as error: 
        print(error)
 
       
def vistaRegistrarServiciosPrestados(request):
    user = request.user

    if user.groups.filter(name='Asistente').exists():
        vehiculos = Vehiculo.objects.all()
        clientes = Cliente.objects.all()
        empleados = Empleado.objects.all()
        servicios = Servicio.objects.all()
        serviciosPrestados = ServicioPrestado.objects.all()

        retorno = {
            "empleados": empleados,
            "servicios": servicios,
            "serviciosPrestados": serviciosPrestados,
            "vehiculos": vehiculos,
            "clientes": clientes,
            "estadoSP": estadoServicioPrestado
        }
        return render(request, "asistente/frmRegistrarServicioPrestado.html", retorno)

    mensaje = "Nuestro sistema detecta que su rol no cuenta con los permisos necesarios para acceder a esta url."

    if user.groups.filter(name='Administrador').exists():
        return render(request, "administrador/inicio.html", {"mensaje": mensaje})

    if user.groups.filter(name='Tecnico').exists():
        return render(request, "tecnico/inicio.html", {"mensaje": mensaje})

    return render(request, "inicio.html", {"mensaje": "Debe iniciar sesión"})

    
def registrarServicioPrestado(request):
    estado = False
    if request.method == 'POST':
        try:
            with transaction.atomic():
                idCliente = int(request.POST['cliente'])
                idVehiculo = int(request.POST['vehiculo'])
                idEmpleado = int(request.POST['empleado'])
                estadoServicio = request.POST['estado']
                fechaHora = request.POST.get('fechaHora', None)
                idServicio = int(request.POST['servicio'])
                observaciones = request.POST['observaciones']
                
                cliente = Cliente.objects.get(pk=idCliente)
                vehiculo = Vehiculo.objects.get(pk=idVehiculo)
                empleado = Empleado.objects.get(pk=idEmpleado)
                servicio = Servicio.objects.get(pk=idServicio)
                
                servicioprestado = ServicioPrestado(
                    serpCli=cliente,
                    serpVehi=vehiculo,
                    serpEmp=empleado,
                    serpServicio=servicio,
                    serpEstado=estadoServicio,
                    serpObservaciones=observaciones,
                    serpFechaServicio=fechaHora
                )
                servicioprestado.save()
                
                detalleServicios = json.loads(request.POST['detalle'])
                sumaCostos = 0
                
                for detalle in detalleServicios:
                    idDetalleServicio = int(detalle['idServicio'])
                    costoServicio = int(detalle['costo'])
                    
                    servicioDetalle = Servicio.objects.get(pk=idDetalleServicio)
                    
                    sumaCostos += costoServicio
                    
                    detalleServicioPrestado = DetalleServicioPrestado(
                        detMonto=sumaCostos,
                        detServicio=servicioDetalle,
                        detServicioPrestado=servicioprestado,
                        serpEmp=empleado
                    )
                    detalleServicioPrestado.save()
                
                estado = True
                mensaje = "Se ha registrado el servicio prestado correctamente"
        
        except Exception as error:
            transaction.rollback()
            mensaje = str(error)
        
        retorno = {"estado": estado, "mensaje": mensaje}
        return JsonResponse(retorno)
        
def vistaGestionarFacturas(request):
    user = request.user

    if user.groups.filter(name='Asistente').exists():
        return render(request, "asistente/vistaGestionarFacturas.html")

    mensaje = "Nuestro sistema detecta que su rol no cuenta con los permisos necesarios para acceder a esta url."

    if user.groups.filter(name='Administrador').exists():
        return render(request, "administrador/inicio.html", {"mensaje": mensaje})

    if user.groups.filter(name='Tecnico').exists():
        return render(request, "tecnico/inicio.html", {"mensaje": mensaje})

    return render(request, "inicio.html", {"mensaje": "Debe iniciar sesión"})
    
def vistaGestionarSolicitudesV(request):
    user = request.user

    if user.groups.filter(name='Tecnico').exists():
        return render(request, "tecnico/vistaGestionarSolicitudesVehiculos.html")

    mensaje = "Nuestro sistema detecta que su rol no cuenta con los permisos necesarios para acceder a esta url."

    if user.groups.filter(name='Administrador').exists():
        return render(request, "administrador/inicio.html", {"mensaje": mensaje})

    if user.groups.filter(name='Asistente').exists():
        return render(request, "asistente/inicio.html", {"mensaje": mensaje})

    return render(request, "inicio.html", {"mensaje": "Debe iniciar sesión"})
    
    
def existeCliente(request):
    id_identificacion = request.POST.get("txtIdentificacion", None)
    mensaje = ""
    persona = None
    estado = False

    try:
        if id_identificacion:
            persona = Persona.objects.get(perIdentificacion=id_identificacion)
            mensaje = "Cliente consultado de manera exitosa"
            estado = True
        else:
            mensaje = "Por favor, ingrese una identificación"
    except Persona.DoesNotExist:
        mensaje = "No se encontró un cliente con esa identificación"
    except Exception as error:
        mensaje = f"Problemas -> {error}"

    retorno = {
        "mensaje": mensaje,
        "persona": persona,
        "estado": estado,
    }
    return render(request, "cliente/vistaGestionarConsultasC.html", retorno)


def actualizarVehiculo(request):
    estado = False
    mensaje = ""
    
    try:
        idVehiculo = int(request.POST.get("idVehiculo"))
        placa = request.POST.get("txtPlaca")
        marca = request.POST.get("cbMarca")
        modelo = request.POST.get("txtModelo")
        tipoV = request.POST.get("cbTipoV")
        
        with transaction.atomic():
            vehiculo = Vehiculo.objects.select_for_update().get(pk=idVehiculo)
            
            if Vehiculo.objects.filter(vehPlaca=placa).exclude(pk=idVehiculo).exists():
                mensaje = "La placa ya está en uso por otro vehículo"
            else:
                vehiculo.vehPlaca = placa
                vehiculo.vehMarca = marca
                vehiculo.vehModelo = modelo
                vehiculo.vehTipo = tipoV
                vehiculo.save()
                estado = True
                mensaje = "Vehículo actualizado correctamente"
    except Vehiculo.DoesNotExist:
        mensaje = "El vehículo no existe"
    except Exception as error:
        transaction.rollback()
        mensaje = str(error)
    
    vehiculos = Vehiculo.objects.all()
    retorno = {
        "mensaje": mensaje,
        "vehiculos": vehiculos,
        "tipoVeh": tipoVehiculo,
        "tipoMar": tiposMarcas,
        "estado": estado,
    }
    
    return render(request, "asistente/vistaGestionarVehiculos.html", retorno)


def actualizarCliente(request):
    estado = False
    mensaje = ""
    
    try:
        idCliente = int(request.POST.get("idCliente"))
        identificacion = request.POST.get("txtIdentificacion")
        nombres = request.POST.get("txtNombres")
        apellidos = request.POST.get("txtApellidos")
        correo = request.POST.get("txtCorreo")
        direccion = request.POST.get("txtDireccion")
        numero = request.POST.get("txtNumeroC")
        
        with transaction.atomic():
            cliente = Cliente.objects.select_for_update().get(pk=idCliente)
            persona = cliente.cliPersona
            
            if Persona.objects.exclude(id=persona.id).filter(perIdentificacion=identificacion).exists():
                mensaje = "La identificación ya está registrada en otro cliente"
            elif Persona.objects.exclude(id=persona.id).filter(perCorreo=correo).exists():
                mensaje = "El correo electrónico ya está registrado en otro cliente"
            elif Persona.objects.exclude(id=persona.id).filter(perNumeroCelular=numero).exists():
                mensaje = "El número de celular ya está registrado en otro cliente"
            else:
                persona.perIdentificacion = identificacion
                persona.perNombres = nombres
                persona.perApellidos = apellidos
                persona.perCorreo = correo
                persona.perNumeroCelular = numero
                persona.save()
                
                cliente.cliDireccion = direccion
                cliente.save()
                estado = True
                mensaje = "Cliente actualizado correctamente"
    except Cliente.DoesNotExist:
        mensaje = "El cliente no existe"
    except Exception as error:
        transaction.rollback()
        mensaje = str(error)
    
    clientes = Cliente.objects.all()
    retorno = {
        "mensaje": mensaje,
        "estado": estado,
        "clientes": clientes,
    }
    
    return render(request, "asistente/vistaGestionarClientes.html", retorno)


def actualizarEmpleado(request):
    estado = False
    mensaje = ""
    
    try:
        idEmpleado = int(request.POST.get("idEmpleado"))
        identificacion = request.POST.get("txtIdentificacion")
        nombres = request.POST.get("txtNombres")
        apellidos = request.POST.get("txtApellidos")
        cargo = request.POST.get("txtCargo")
        sueldo = request.POST.get("txtSueldo")
        estadoE = request.POST.get("cbEstado")
        correo = request.POST.get("txtCorreo")
        numero = request.POST.get("txtNumeroC")
        
        with transaction.atomic():
            empleado = Empleado.objects.select_for_update().get(pk=idEmpleado)
            persona = empleado.empPersona
            
            if Persona.objects.exclude(id=persona.id).filter(perIdentificacion=identificacion).exists():
                mensaje = "La identificación ya está registrada en otro empleado"
            elif Persona.objects.exclude(id=persona.id).filter(perCorreo=correo).exists():
                mensaje = "El correo electrónico ya está registrado en otro empleado"
            elif Persona.objects.exclude(id=persona.id).filter(perNumeroCelular=numero).exists():
                mensaje = "El número de celular ya está registrado en otro empleado"
            else:
                persona.perIdentificacion = identificacion
                persona.perNombres = nombres
                persona.perApellidos = apellidos
                persona.perCorreo = correo
                persona.perNumeroCelular = numero
                persona.save()
                
                empleado.empCargo = cargo
                empleado.empSueldo = sueldo
                empleado.empEstado = estadoE
                empleado.save()
                estado = True
                mensaje = "Empleado actualizado correctamente"
    except Empleado.DoesNotExist:
        mensaje = "El Empleado no existe"
    except Exception as error:
        transaction.rollback()
        mensaje = str(error)
    
    empleados = Empleado.objects.all()
    retorno = {
        "mensaje": mensaje,
        "estado": estado,
        "empleados": empleados,
    }
    
    return render(request, "administrador/vistaGestionarEmpleados.html", retorno)


def vistaEdicionPerfilAsistente(request):
    user = request.user
    if user.groups.filter(name='Asistente').exists():
        roles = Group.objects.all()
        return render(request, "asistente/frmEdicionPerfil.html", {"roles": roles, "tipoUsuario":tipoUsuario, "user": user})
        

    mensaje = "Nuestro sistema detecta que su rol no cuenta con los permisos necesarios para acceder a esta url."

    if user.groups.filter(name='Administrador').exists():
        return render(request, "administrador/inicio.html", {"mensaje": mensaje})

    if user.groups.filter(name='Tecnico').exists():
        return render(request, "tecnico/inicio.html", {"mensaje": mensaje})

    return render(request, "inicio.html", {"mensaje": "Debe iniciar sesión"})
    


def vistaEdicionPerfilAdministrador(request):
    user = request.user
    if user.groups.filter(name='Administrador').exists():
        roles = Group.objects.all()
        return render(request, "administrador/frmEdicionPerfil.html", {"roles": roles, "tipoUsuario":tipoUsuario, "user": user})
        

    mensaje = "Nuestro sistema detecta que su rol no cuenta con los permisos necesarios para acceder a esta url."

    if user.groups.filter(name='Asistente').exists():
        return render(request, "asistente/inicio.html", {"mensaje": mensaje})

    if user.groups.filter(name='Tecnico').exists():
        return render(request, "tecnico/inicio.html", {"mensaje": mensaje})

    return render(request, "inicio.html", {"mensaje": "Debe iniciar sesión"})
    
    
def vistaEdicionPerfilTecnico(request):
    user = request.user
    if user.groups.filter(name='Tecnico').exists():
        roles = Group.objects.all()
        return render(request, "tecnico/frmEdicionPerfil.html", {"roles": roles, "tipoUsuario":tipoUsuario, "user": user})
        

    mensaje = "Nuestro sistema detecta que su rol no cuenta con los permisos necesarios para acceder a esta url."

    if user.groups.filter(name='Administrador').exists():
        return render(request, "administrador/inicio.html", {"mensaje": mensaje})

    if user.groups.filter(name='Asistente').exists():
        return render(request, "asistente/inicio.html", {"mensaje": mensaje})

    return render(request, "inicio.html", {"mensaje": "Debe iniciar sesión"})

    
def actualizarUsuarioAdmin(request):
    estado = False
    mensaje = ""
    try:
        nombres = request.POST.get('txtNombres')
        apellidos = request.POST.get('txtApellidos')
        correo = request.POST.get('txtCorreo')
        nueva_imagen = request.FILES.get('fileFoto')
        with transaction.atomic():
            if User.objects.exclude(id=request.user.id).filter(email=correo).exists():
                mensaje= "El correo electrónico ya está en uso por otro usuario."
            else:
                usuario = request.user
                usuario.first_name = nombres
                usuario.last_name = apellidos
                usuario.email = correo
                if nueva_imagen:
                    usuario.userFoto = nueva_imagen
                usuario.save()
                estado = True
                mensaje = "Usuario actualizado correctamente"
    except Exception as error:
            transaction.rollback()
            mensaje = str(error)
    retorno = {
        "mensaje": mensaje,
        "estado": estado,
    }
    return render(request, "administrador/frmEdicionPerfil.html", retorno)


def actualizarUsuarioAsistente(request):
    estado = False
    mensaje = ""
    try:
        nombres = request.POST.get('txtNombres')
        apellidos = request.POST.get('txtApellidos')
        correo = request.POST.get('txtCorreo')
        nueva_imagen = request.FILES.get('fileFoto')
        with transaction.atomic():
            if User.objects.exclude(id=request.user.id).filter(email=correo).exists():
                mensaje= "El correo electrónico ya está en uso por otro usuario."
            else:
                usuario = request.user
                usuario.first_name = nombres
                usuario.last_name = apellidos
                usuario.email = correo
                if nueva_imagen:
                    usuario.userFoto = nueva_imagen
                usuario.save()
                estado = True
                mensaje = "Usuario actualizado correctamente"
    except Exception as error:
            transaction.rollback()
            mensaje = str(error)
    retorno = {
        "mensaje": mensaje,
        "estado": estado,
    }
    return render(request, "asistente/frmEdicionPerfil.html", retorno)


def actualizarUsuarioTecnico(request):
    estado = False
    mensaje = ""
    try:
        nombres = request.POST.get('txtNombres')
        apellidos = request.POST.get('txtApellidos')
        correo = request.POST.get('txtCorreo')
        nueva_imagen = request.FILES.get('fileFoto')
        with transaction.atomic():
            if User.objects.exclude(id=request.user.id).filter(email=correo).exists():
                mensaje= "El correo electrónico ya está en uso por otro usuario."
            else:
                usuario = request.user
                usuario.first_name = nombres
                usuario.last_name = apellidos
                usuario.email = correo
                if nueva_imagen:
                    usuario.userFoto = nueva_imagen
                usuario.save()
                estado = True
                mensaje = "Usuario actualizado correctamente"
    except Exception as error:
            transaction.rollback()
            mensaje = str(error)
    retorno = {
        "mensaje": mensaje,
        "estado": estado,
    }
    return render(request, "tecnico/frmEdicionPerfil.html", retorno)


def deshabilitarUsuario(request, user_id):
    try:
        usuario = User.objects.get(pk=user_id)

        if usuario.is_superuser:
            raise Exception("No se puede deshabilitar a un superusuario.")

        usuario.is_active = False
        usuario.save()

        usuarios = User.objects.all()

        table_html = ""
        for usuario in usuarios:
            table_html += f"<tr>...</tr>"

        return JsonResponse({
            'success': True,
            'tableHtml': table_html,
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


def habilitarUsuario(request, user_id):
    try:
        user = get_object_or_404(User, pk=user_id)
        user.is_active = True
        user.save()
        mensaje = f"Usuario {user.username} habilitado correctamente."
        estado = True
    except User.DoesNotExist:
        mensaje = "Usuario no encontrado."
        estado = False
    except Exception as error:
        mensaje = str(error)
        estado = False
    
    return JsonResponse({
        "mensaje": mensaje,
        "estado": estado
    })
  

class PersonaList(generics.ListCreateAPIView):
    queryset=Persona.objects.all()
    serializer_class=PersonaSerializer


class PersonaDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Persona.objects.all()
    lookup_field = 'perIdentificacion'
    serializer_class = PersonaSerializer


class ClienteList(generics.ListCreateAPIView):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer


class ClienteDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer
    

def mostrarGrafica1(request):
    matplotlib.use('Agg')
    
    
    categorias = ['A', 'B', 'C', 'D', 'E']
    valores = [25, 50, 75, 100, 125]
    
    grafica = plt.bar(categorias, valores)

    plt.xlabel('Categorías')
    plt.ylabel('Valores')
    plt.title('Gráfica de Barras')

    ruta_grafica = os.path.join('./media/graficas', 'grafica_de_barras.png')
    
    plt.savefig(ruta_grafica)
    
    generar_pdf()
    retorno = {
        "ruta_grafica": ruta_grafica
    }
    return render(request, "administrador/vistaGraficas.html", retorno)

    
class PDF(FPDF):
    def header(self):
        self.image('./media/fotos/Toji.jpg', 10, 10, 25)
        
    def footer(self):
        self.set_xy(10, -15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, 'Fecha de creación: ' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 0, 0, 'L')
        
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, 'El impulso que necesita tu vehículo', 0, 0, 'R')
  
  
def generar_pdf():
    pdf = PDF()
    pdf.add_page()
    
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Serviteca Opita", 0, 1, 'C')
    
    pdf.ln(30)
    
    pdf.set_font("Arial", size=12)
    pdf.set_auto_page_break(auto=True, margin=15)
    col_width = pdf.w / 3.5
   
    pdf.cell(col_width, 10, "ID", 1)
    pdf.cell(col_width, 10, "Nombre", 1)
    pdf.cell(col_width, 10, "Apellido", 1)
    pdf.ln()
    
    for _ in range(10):
        pdf.cell(col_width, 10, str(random.randint(1, 100)), 1)
        pdf.cell(col_width, 10, "Nombre" + str(random.randint(1, 100)), 1)
        pdf.cell(col_width, 10, "Apellido" + str(random.randint(1, 100)), 1)
        pdf.ln()
    
    ruta_pdf = os.path.join('./media/pdf/', 'serviteca_opita.pdf')
    
    pdf.output(ruta_pdf)

