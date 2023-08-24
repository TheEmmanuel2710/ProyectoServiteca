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
from django.http import HttpResponse
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib import messages
from django.utils import timezone


datosSesion={"user":None,"rutaFoto":None, "rol":None}


def urlValidacion(request, texto):
    mensaje2 = "Nuestro sistema detecta que la ulr ingresada no es valida,por favor verifique."
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
        mensaje = "Debe iniciar sesión."
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
        mensaje = "Debe iniciar sesión."
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
        mensaje = "Debe iniciar sesión."
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

    return render(request, "inicio.html", {"mensaje": "Debe iniciar sesión."})
    
       
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

    return render(request, "inicio.html", {"mensaje": "Debe iniciar sesión."})


def registrarUsuario(request):
    estado = False
    mensaje1 = ""

    try:
        correo = request.POST.get("txtCorreo")

        if User.objects.filter(email=correo).exists():
            mensaje1 = "Error: Correo electrónico ya está registrado en otro usuario."
        else:
            nombres = request.POST.get("txtNombres")
            apellidos = request.POST.get("txtApellidos")
            tipo = request.POST.get("cbTipo")
            foto = request.FILES.get("fileFoto", False)
            idRol = int(request.POST.get("cbRol"))

            with transaction.atomic():
                user = User(
                    username=correo,
                    first_name=nombres,
                    last_name=apellidos,
                    email=correo,
                    userTipo=tipo,
                    userFoto=foto,
                )
                user.save()

                rol = Group.objects.get(pk=idRol)
                user.groups.add(rol)

                if rol.name == "Administrador":
                    user.is_staff = True

                passwordGenerado = generarPassword()
                user.set_password(passwordGenerado)
                user.save()

                mensaje1 = "Usuario Agregado Correctamente."
                estado = True

                asunto = "Registro Sistema Serviteca"
                mensaje = f"Cordial saludo, <b>{user.first_name} {user.last_name}</b>, nos permitimos\
                    informarle que usted ha sido registrado en el Sistema de ServitecaOpita.\
                    Nos permitimos enviarle las credenciales de Ingreso a nuestro sistema.<br>\
                    <br><b>Username: </b> {user.username}\
                    <br><b>Password: </b> {passwordGenerado}\
                    <br><br>Lo invitamos a ingresar a nuestro sistema en la url:\
                    http://127.0.0.1:8000/"
                thread = threading.Thread(target=enviarCorreo, args=(asunto, mensaje, user.email))
                thread.start()

    except Exception as error:
        mensaje1 = f"Error al registrar usuario: {error}."

    retorno = {"mensaje1": mensaje1, "estado": estado}
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

    return render(request, "inicio.html", {"mensaje": "Debe iniciar sesión."})


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

    return render(request, "inicio.html", {"mensaje": "Debe iniciar sesión."})

def registrarCliente(request):
    estado = False
    mensaje = ""

    try:
        identificacion = request.POST.get("txtIdentificacion")
        numeroC = request.POST.get("txtNumeroC")
        correo = request.POST.get("txtCorreo")


        if Persona.objects.filter(perIdentificacion=identificacion).exists():
            mensaje = "Error : Identificación ya registrada en otro cliente."
        elif Persona.objects.filter(perNumeroCelular=numeroC).exists():
            mensaje = "Error : Número de celular ya registrado en otro cliente."
        elif Persona.objects.filter(perCorreo=correo).exists():
            mensaje = "Error : Correo electrónico ya registrado en otro cliente."
        else:
            nombres = request.POST.get("txtNombres")
            apellidos = request.POST.get("txtApellidos")
            direccion = request.POST.get("txtDireccion")

            with transaction.atomic():
                persona = Persona(
                    perIdentificacion=identificacion,
                    perNombres=nombres,
                    perApellidos=apellidos,
                    perCorreo=correo,
                    perNumeroCelular=numeroC
                )
                persona.save()

                cliente = Cliente(cliDireccion=direccion, cliPersona=persona)
                cliente.save()

            estado = True
            mensaje = "Cliente Agregado Correctamente."

    except Exception as error:
        mensaje = f"Error al registrar cliente: {error}."

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
        return JsonResponse({"error": "Cliente no encontrado."}, status=404)
    except Persona.DoesNotExist:
        return JsonResponse({"error": "Persona no encontrada."}, status=404)
    except ValueError:
        return JsonResponse({"error": "ID inválido."}, status=400)
    except Exception as error:
        return JsonResponse({"error": str(error)}, status=500)

def consultarFactura(request, id):
    try:
        factura = Factura.objects.get(pk=int(id))
        servicio_prestado = factura.facServicioPrestado
        cliente = servicio_prestado.serpCli
        persona = cliente.cliPersona
        nombres_servicios_prestados = [detalle.detServicio.serNombre for detalle in servicio_prestado.detalleservicioprestado_set.all()]
        datos_persona = {
            "perNombres": persona.perNombres,
            "perApellidos": persona.perApellidos,
        }
        
        datos_cliente = {
            "persona": datos_persona,
        }
        
        datos_factura = {
            "facTotal": factura.facTotal,
            "facEstado": factura.facEstado,
            "facCodigo": factura.facCodigo,
            "facFecha": factura.facFecha.strftime("%Y-%m-%d %H :%M :%S"), 
            "serviciosPrestados": nombres_servicios_prestados,
        }
        
        return JsonResponse({"cliente": datos_cliente, "factura": datos_factura})
    except Factura.DoesNotExist:
        return JsonResponse({"error": "Factura no encontrada."}, status=404)
    except Cliente.DoesNotExist:
        return JsonResponse({"error": "Cliente no encontrado."}, status=404)
    except Persona.DoesNotExist:
        return JsonResponse({"error": "Persona no encontrada."}, status=404)
    except ValueError:
        return JsonResponse({"error": "ID inválido."}, status=400)
    except Exception as error:
        return JsonResponse({"error": str(error)}, status=500)
    

def ActualizarFac(request):
    estado = False
    mensaje = ""
    if request.method == "POST":
        factura_id = request.POST.get("idFactura")
        nuevo_estado = request.POST.get("cbEstado")
        try:
            factura = Factura.objects.get(pk=factura_id)
            factura.facEstado = nuevo_estado
            factura.save()
            estado = True
            mensaje = "Factura actualizado correctamente."
        except Factura.DoesNotExist:
            return JsonResponse({"error": "Factura no encontrada."}, status=404)
        except Exception as error:
          transaction.rollback()
          mensaje = f"Error al actualizar factura,{error}."
    retorno = {
        "mensaje": mensaje,
        "estado": estado
    }
    return render(request, "asistente/vistaGestionarFacturas.html", retorno)
        
    

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

    return render(request, "inicio.html", {"mensaje": "Debe iniciar sesión."})


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

    return render(request, "inicio.html", {"mensaje": "Debe iniciar sesión."})


def registrarVehiculo(request):
    estado = False
    mensaje = ""

    try:
        placa = request.POST.get("txtPlaca")

        if Vehiculo.objects.filter(vehPlaca=placa).exists():
            mensaje = "Error : Placa ya registrada en otro vehiculo."
        else:
            marca = request.POST.get("cbMarca")
            modelo = request.POST.get("txtModelo")
            tipoV = request.POST.get("cbTipoV")

            with transaction.atomic():
                vehiculo = Vehiculo(
                    vehPlaca=placa,
                    vehMarca=marca,
                    vehModelo=modelo,
                    vehTipo=tipoV
                )
                vehiculo.save()

            estado = True
            mensaje = "Vehículo Agregado Correctamente."
    except Exception as error:
        mensaje = f"Error al registrar vehículo : {error}."

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
        return JsonResponse({"error": "Vehiculo no encontrado."}, status=404)
    except ValueError:
        return JsonResponse({"error": "ID inválido."}, status=400)
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

    return render(request, "inicio.html", {"mensaje": "Debe iniciar sesión."})


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

    return render(request, "inicio.html", {"mensaje": "Debe iniciar sesión."})


def registrarEmpleado(request):
    estado = False
    mensaje = ""

    try:
        identificacion = request.POST.get("txtIdentificacion")
        numeroC = request.POST.get("txtNumeroC")
        correo = request.POST.get("txtCorreo")

        if Persona.objects.filter(perIdentificacion=identificacion).exists():
            mensaje = "Error : Identificación ya registrada en un empleado."
        elif Persona.objects.filter(perNumeroCelular=numeroC).exists():
            mensaje = "Error : Número de celular ya registrado en un empleado."
        elif Persona.objects.filter(perCorreo=correo).exists():
            mensaje = "Error : Correo electrónico ya registrado en un empleado."
        else:
            nombres = request.POST.get("txtNombres")
            apellidos = request.POST.get("txtApellidos")
            cargo = request.POST.get("txtCargo")
            sueldo = request.POST.get("txtSueldo")
            estadoE = request.POST.get("cbEstado")

            with transaction.atomic():
                persona = Persona(
                    perIdentificacion=identificacion,
                    perNombres=nombres,
                    perApellidos=apellidos,
                    perCorreo=correo,
                    perNumeroCelular=numeroC
                )
                persona.save()
                empleado = Empleado(
                    empCargo=cargo,
                    empSueldo=sueldo,
                    empEstado=estadoE,
                    empPersona=persona
                )
                empleado.save()

            estado = True
            mensaje = "Empleado Agregado Correctamente."

    except Exception as error:
        mensaje = f"Error al registrar empleado : {error}."

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
        return JsonResponse({"error": "Empleado no encontrado."}, status=404)
    except Persona.DoesNotExist:
        return JsonResponse({"error": "Persona no encontrada."}, status=404)
    except ValueError:
        return JsonResponse({"error": "ID inválido."}, status=400)
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
            mensaje = "Usuario o Contraseña Incorrectas."
            return render(request, "inicio.html",{"mensaje":mensaje})
    else:
        mensaje="Debe validar primero el recaptcha."
        return render(request, "inicio.html",{"mensaje" :mensaje})
 
    
def salir(request):
    auth.logout(request)
    return render(request, "inicio.html",
                  {"mensaje":"Ha cerrado la sesión."})
  
    
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

    return render(request, "inicio.html", {"mensaje": "Debe iniciar sesión."})

    
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
                mensaje = "Se ha registrado el servicio prestado correctamente."
        
        except Exception as error:
            transaction.rollback()
            mensaje = str(error)
        
        retorno = {"estado": estado, "mensaje": mensaje}
        return JsonResponse(retorno)
        
        
def vistaGestionarFacturas(request):
    user = request.user

    if user.groups.filter(name='Asistente').exists():
        facturasNP = Factura.objects.filter(facEstado="No Pagada").select_related('facServicioPrestado__serpCli') 
        facturasP = Factura.objects.filter(facEstado="Pagada").select_related('facServicioPrestado__serpCli')
        retorno = {"facturasP": facturasP,"facturasNP":facturasNP,"estadoFactura": estadoFactura}
        return render(request, "asistente/vistaGestionarFacturas.html", retorno)

    mensaje = "Nuestro sistema detecta que su rol no cuenta con los permisos necesarios para acceder a esta URL."

    if user.groups.filter(name='Administrador').exists():
        return render(request, "administrador/inicio.html", {"mensaje": mensaje})

    if user.groups.filter(name='Tecnico').exists():
        return render(request, "tecnico/inicio.html", {"mensaje": mensaje})

    return render(request, "inicio.html", {"mensaje": "Debe iniciar sesión."})

    
def vistaGestionarSolicitudesV(request):
    user = request.user

    if user.groups.filter(name='Tecnico').exists():
        return render(request, "tecnico/vistaGestionarSolicitudesVehiculos.html")

    mensaje = "Nuestro sistema detecta que su rol no cuenta con los permisos necesarios para acceder a esta url."

    if user.groups.filter(name='Administrador').exists():
        return render(request, "administrador/inicio.html", {"mensaje": mensaje})

    if user.groups.filter(name='Asistente').exists():
        return render(request, "asistente/inicio.html", {"mensaje": mensaje})

    return render(request, "inicio.html", {"mensaje": "Debe iniciar sesión."})
    
    
def existeCliente(request):
    id_identificacion = request.POST.get("txtIdentificacion", None)
    mensaje = ""
    persona = None
    estado = False

    try:
        if id_identificacion:
            persona = Persona.objects.get(perIdentificacion=id_identificacion)
            mensaje = "Cliente consultado de manera exitosa."
            estado = True
        else:
            mensaje = "Por favor, ingrese una identificación."
    except Persona.DoesNotExist:
        mensaje = "No se encontró un cliente con esa identificación."
    except Exception as error:
        mensaje = f"Problemas -> {error}."

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
                mensaje = "La placa ya está en uso por otro vehículo."
            else:
                vehiculo.vehPlaca = placa
                vehiculo.vehMarca = marca
                vehiculo.vehModelo = modelo
                vehiculo.vehTipo = tipoV
                vehiculo.save()
                estado = True
                mensaje = "Vehículo actualizado correctamente."
    except Vehiculo.DoesNotExist:
        mensaje = "El vehículo no existe."
    except Exception as error:
        transaction.rollback()
        mensaje = f"Error al actualizar vehiculo,{error}."
    
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
                mensaje = "La identificación ya está en uso por otro cliente."
            elif Persona.objects.exclude(id=persona.id).filter(perCorreo=correo).exists():
                mensaje = "El correo electrónico ya está en uso por otro cliente."
            elif Persona.objects.exclude(id=persona.id).filter(perNumeroCelular=numero).exists():
                mensaje = "El número de celular ya está en uso por otro cliente."
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
                mensaje = "Cliente actualizado correctamente."
    except Cliente.DoesNotExist:
        mensaje = "El cliente no existe."
    except Exception as error:
        transaction.rollback()
        mensaje = f"Error,{error}"
    
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
                mensaje = "La identificación ya está en uso por otro empleado."
            elif Persona.objects.exclude(id=persona.id).filter(perCorreo=correo).exists():
                mensaje = "El correo electrónico ya está en uso por otro empleado."
            elif Persona.objects.exclude(id=persona.id).filter(perNumeroCelular=numero).exists():
                mensaje = "El número de celular ya está en uso por otro empleado."
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
                mensaje = "Empleado actualizado correctamente."
    except Empleado.DoesNotExist:
        mensaje = "El Empleado no existe."
    except Exception as error:
        transaction.rollback()
        mensaje = f"Error,{error}"
    
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

    return render(request, "inicio.html", {"mensaje": "Debe iniciar sesión."})
    


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

    return render(request, "inicio.html", {"mensaje": "Debe iniciar sesión."})
    
    
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

    return render(request, "inicio.html", {"mensaje": "Debe iniciar sesión."})

    
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
                mensaje = "Usuario actualizado correctamente."
    except Exception as error:
            transaction.rollback()
            mensaje = f"Error,{error}"
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
                mensaje = "Usuario actualizado correctamente."
    except Exception as error:
            transaction.rollback()
            mensaje = f"Error,{error}"
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
                mensaje = "Usuario actualizado correctamente."
    except Exception as error:
            transaction.rollback()
            mensaje = f"Error,{error}"
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

        return JsonResponse({
            'success': True
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

    ruta_grafica = os.path.join(settings.MEDIA_ROOT, 'graficas', 'grafica_de_barras.png')
    
    plt.savefig(ruta_grafica)
    
    generar_pdf(request)
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
  
  
def generar_pdf(request):
    try:

        pdf = PDF()
        pdf.add_page()

       
        image_path = settings.MEDIA_ROOT + '/fotos/Toji.jpg'

       
        pdf.image(image_path, x=10, y=10, w=25)

       
        pdf.ln(20)  
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, 'Tabla de Valores Aleatorios', 0, 1, 'C')

        pdf.set_font('Arial', '', 12)
        column_widths = [40, 40, 40]  
        row_height = 10 
        num_rows = 5  
        num_columns = 3  

        pdf.cell(column_widths[0], row_height, 'Columna 1', border=1)
        pdf.cell(column_widths[1], row_height, 'Columna 2', border=1)
        pdf.cell(column_widths[2], row_height, 'Columna 3', border=1)
        pdf.ln()

        for _ in range(num_rows):
            for _ in range(num_columns):
                random_value = random.randint(1, 100)
                pdf.cell(column_widths[_], row_height, str(random_value), border=1)
            pdf.ln()

        pdf_path = settings.MEDIA_ROOT + '/pdf/SERVITECA_OPITA.pdf'

        pdf.output(pdf_path)

        # PDF como respuesta HTTP 
        # with open(pdf_path, 'rb') as pdf_file:
        #     response = HttpResponse(pdf_file.read(), content_type='application/pdf')
        #     response['Content-Disposition'] = 'attachment; filename="SERVITECA OPITA.pdf"'
        #     return response

        return HttpResponse("PDF generado y guardado correctamente.")
    except Exception as e:
        return HttpResponse("Error al generar el PDF: " + str(e))
   

def vistaCorreoForgot(request):
    return render(request,"vistaCorreoForgot.html")


def registrarPeticionForgot(request):
    if request.method == 'POST':
        correo = request.POST.get('txtCorreo')
        try:
            usuario = User.objects.get(email=correo)
            with transaction.atomic():
                peticion = PeticionForgot(id_user=usuario)
                peticion.save()
                # Generar uidb64
                uidb64 = urlsafe_base64_encode(force_bytes(usuario.pk))
                # Generar el token
                token = default_token_generator.make_token(usuario)
                # Enviar correo al usuario en un hilo separado
                asunto = 'Solicitud de Restablecimiento de Contraseña'
                mensaje = f'Cordial saludo, {usuario.first_name} {usuario.last_name}, ha solicitado el restablecimiento de contraseña. Por favor, haga clic en el siguiente enlace para continuar con el proceso: http://127.0.0.1:8000/cambiarContrasena/{uidb64}/{token}/'
                thread = threading.Thread(target=enviarCorreo, args=(asunto, mensaje, usuario.email))
                thread.start()

                mensaje = "Correo enviado exitosamente,por favor verifique su bandeja de entrada."
                estado = True
        except User.DoesNotExist:
            mensaje = "El correo electrónico no está registrado en ningun usuario."
            estado = False

        return render(request, "vistaCorreoForgot.html", {"mensaje": mensaje, "estado": estado})
    else:
        return render(request, "vistaCorreoForgot.html")
    
    
def vistaCambiarContraseña(request):
    return render(request,"cambiarContraseña.html")


def cambiarContraseña(request, uidb64, token): 
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            password = request.POST.get('nuevaContraseña')
            user.set_password(password)
            user.save()
            messages.success(request, 'Contraseña restablecida correctamente, ahora puedes iniciar sesión con tu nueva contraseña.')

            PeticionForgot.objects.filter(id_user=user).update(estado='Inactiva')
            return redirect('/mostrarMensaje/')

        # Validacion para expirar el enlace de recuperacion de contraseña segun un tiempo pre-establecido
        peticion = PeticionForgot.objects.get(id_user=user)
        tiempoAc = timezone.now()
        tiempoDif = tiempoAc - peticion.fechaHoraCreacion
        if tiempoDif.total_seconds() > 300:  # 5 minutos en segundos
            PeticionForgot.objects.filter(id_user=user).update(estado='Inactiva')
            return render(request, 'cambiarContrasena.html', {'validlink': False})

        return render(request, 'cambiarContrasena.html', {'validlink': True})
    else:
        return render(request, 'cambiarContrasena.html', {'validlink': False})
    
    
def mostrarMensaje(request):
    return render(request, 'mostrarMensaje.html')

