from django.shortcuts import render, redirect, get_object_or_404
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
from appGestionServiteca.serializers import PersonaSerializer, ClienteSerializer
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


datosSesion = {"user": None, "rutaFoto": None, "rol": None}


def urlValidacion(request, texto):
    mensaje2 = "Nuestro sistema detecta que la ulr ingresada no es valida,por favor verifique."
    if not request.user.is_authenticated:
        return render(request, "inicio.html", {"mensaje2": mensaje2})
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
        return render(request, "administrador/frmRegistrarUsuario.html", {"roles": roles, "tipoUsuario": tipoUsuario, "user": user})

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
                thread = threading.Thread(
                    target=enviarCorreo, args=(asunto, mensaje, user.email))
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
        nombres_servicios_prestados = [
            detalle.detServicio.serNombre for detalle in servicio_prestado.detalleservicioprestado_set.all()]
        costos_servicios_prestados = [
            detalle.detServicio.serCosto for detalle in servicio_prestado.detalleservicioprestado_set.all()]
        datos_persona = {
            "perNombres": persona.perNombres,
            "perApellidos": persona.perApellidos,
        }

        datos_cliente = {
            "persona": datos_persona,
        }

        total_costo = sum(costos_servicios_prestados)

        datos_factura = {
            "facTotal": total_costo,
            "facEstado": factura.facEstado,
            "facCodigo": factura.facCodigo,
            "facFecha": factura.facFecha.strftime("%Y-%m-%d %H:%M:%S"),
            "nombresServiciosPrestados": nombres_servicios_prestados,
            "costosServiciosPrestados": costos_servicios_prestados,
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
    facturasNP = Factura.objects.filter(
        facEstado="No Pagada")
    facturasP = Factura.objects.filter(facEstado="Pagada")
    retorno = {
        "mensaje": mensaje,
        "estado": estado,
        "facturasP": facturasP,
        "facturasNP": facturasNP
    }
    return render(request, "asistente/vistaGestionarFacturas.html", retorno)


def vistaGestionarVehiculos(request):
    user = request.user

    if user.groups.filter(name='Asistente').exists():
        vehiculos = Vehiculo.objects.all()
        retorno = {"vehiculos": vehiculos, "tipoVeh": tipoVehiculo,
                   "tipoMar": tiposMarcas, "user": user}
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
        retorno = {"user": user, "tipoVeh": tipoVehiculo,
                   "tipoMar": tiposMarcas}
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

    caracteres = string.ascii_lowercase + \
        string.ascii_uppercase + string.digits + string.punctuation
    password = ''

    for i in range(longitud):
        password += ''.join(random.choice(caracteres))
    return password


def vistaGestionarEmpleados(request):
    user = request.user

    if user.groups.filter(name='Administrador').exists():
        empleados = Empleado.objects.all()
        retorno = {"empleados": empleados,
                   "estadoEmpl": estadoEmpleados, "user": user}
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
        # Buscar empleado por ID de Persona
        empleado = Empleado.objects.get(pk=int(id))
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
    return render(request, "menu.html")


def login(request):
    # validar el recapthcha
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
    print(result)
    """ End reCAPTCHA validation """
    if result['success']:
        username = request.POST["txtUsername"]
        password = request.POST["txtPassword"]
        user = authenticate(username=username, password=password)
        print(user)
        if user is not None:
            # registrar la variable de sesión
            auth.login(request, user)
            if user.groups.filter(name='Administrador').exists():
                return redirect('/inicioAdministrador')
            elif user.groups.filter(name='Asistente').exists():
                return redirect('/inicioAsistente')
            else:
                return redirect('/inicioTecnico')
        else:
            mensaje = "Usuario o Contraseña Incorrectas."
            return render(request, "inicio.html", {"mensaje": mensaje})
    else:
        mensaje = "Debe validar primero el recaptcha."
        return render(request, "inicio.html", {"mensaje": mensaje})


def salir(request):
    auth.logout(request)
    return render(request, "inicio.html",
                  {"mensaje": "Ha cerrado la sesión."})


def enviarCorreo(asunto=None, mensaje=None, destinatario=None):
    remitente = settings.EMAIL_HOST_USER
    template = get_template('enviarCorreo.html')
    contenido = template.render({
        'destinatario': destinatario,
        'mensaje': mensaje,
        'asunto': asunto,
        'remitente': remitente,
    })
    try:
        correo = EmailMultiAlternatives(
            asunto, '', remitente, [destinatario]
        )
        correo.attach_alternative(contenido, 'text/html')
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
        }
        return render(request, "asistente/frmRegistrarServicioPrestado.html", retorno)

    mensaje = "Nuestro sistema detecta que su rol no cuenta con los permisos necesarios para acceder a esta url."

    if user.groups.filter(name='Administrador').exists():
        return render(request, "administrador/inicio.html", {"mensaje": mensaje})

    if user.groups.filter(name='Tecnico').exists():
        return render(request, "tecnico/inicio.html", {"mensaje": mensaje})

    return render(request, "inicio.html", {"mensaje": "Debe iniciar sesión."})


def obtenerSiguienteNumeroFactura():
    ultimaFactura = Factura.objects.last()
    if ultimaFactura:
        ultimoNumero = int(ultimaFactura.facCodigo[-1])
        nuevoNumero = ultimoNumero + 1
    else:
        nuevoNumero = 1
    return nuevoNumero


def generarCodigoFactura():
    siguienteNumero = obtenerSiguienteNumeroFactura()
    return f'SVP-{siguienteNumero:06d}'


def registrarServicioPrestado(request):
    estado = False
    mensaje = ""

    if request.method == 'POST':
        try:
            with transaction.atomic():
                idCliente = int(request.POST['idCliente'])
                idVehiculo = int(request.POST['idVehiculo'])
                fechaHora = datetime.now()
                observaciones = request.POST['observaciones']

                cliente = Cliente.objects.get(pk=idCliente)
                vehiculo = Vehiculo.objects.get(pk=idVehiculo)

                servicioPrestado = ServicioPrestado(
                    serpCli=cliente,
                    serpVehi=vehiculo,
                    serpEstado="Solicitado",
                    serpObservaciones=observaciones,
                    serpFechaServicio=fechaHora
                )
                servicioPrestado.save()

                detalleServicioPrestado_lista = json.loads(
                    request.POST['detalle'])

                total_costo = 0

                empleados_notificados = {}

                for detalle in detalleServicioPrestado_lista:
                    idServicio = int(detalle['idServicio'])
                    servicio = Servicio.objects.get(id=idServicio)
                    empleado = Empleado.objects.get(
                        id=int(detalle['idEmpleado']))
                    detalleServicioPrestado = DetalleServicioPrestado(
                        detServicio=servicio,
                        detServicioPrestado=servicioPrestado,
                        serpEmp=empleado
                    )
                    detalleServicioPrestado.save()
                    total_costo += servicio.serCosto

                    if empleado not in empleados_notificados:
                        empleados_notificados[empleado] = []
                    empleados_notificados[empleado].append(servicio)

                factura = Factura(
                    facTotal=total_costo,
                    facEstado='No Pagada',
                    facServicioPrestado=servicioPrestado,
                    facCodigo=generarCodigoFactura(),
                    facFecha=fechaHora
                )
                factura.save()

                # Enviar correos a los empleados implicados en el detalle servicio
                for empleado, servicios_asignados in empleados_notificados.items():
                    vehiculo_placa = servicioPrestado.serpVehi.vehPlaca
                    cliente_nombre = servicioPrestado.serpCli.cliPersona.perNombres + \
                        " " + servicioPrestado.serpCli.cliPersona.perApellidos
                    asunto_empleado = 'Nuevo Servicio Asignado'
                    servicios_asignados_str = ", ".join(
                        [f"{servicio.serNombre}" for servicio in servicios_asignados])
                    if len(servicios_asignados) == 1:
                        servicios_asignados_str += "."
                    else:
                        servicios_asignados_str += ","
                    mensaje_empleado = f'Se le ha asignado el siguiente servicio: {servicios_asignados_str} en el vehículo: {vehiculo_placa}, para el cliente: {cliente_nombre}.'
                    thread_empleado = threading.Thread(
                        target=enviarCorreo, args=(asunto_empleado, mensaje_empleado, empleado.empPersona.perCorreo))
                    thread_empleado.start()

                # Enviar correo al cliente con los servicios y costos
                servicios_cliente_str = ", ".join(
                    [f"{Servicio.objects.get(id=int(detalle['idServicio'])).serNombre}: ${Servicio.objects.get(id=int(detalle['idServicio'])).serCosto}" for detalle in detalleServicioPrestado_lista])
                asunto_cliente = 'Registro de Servicios Solicitados'
                mensaje_cliente = f'Cordial saludo, {cliente.cliPersona.perNombres} {cliente.cliPersona.perApellidos}, su servicio ha sido registrado con los siguientes detalles: {servicios_cliente_str}.'
                thread_cliente = threading.Thread(
                    target=enviarCorreo, args=(asunto_cliente, mensaje_cliente, cliente.cliPersona.perCorreo))
                thread_cliente.start()

                estado = True
                mensaje = "Se ha registrado el servicio prestado y generado la factura correctamente."

        except Exception as error:
            transaction.rollback()
            mensaje = str(error)

    retorno = {"estado": estado, "mensaje": mensaje}
    return JsonResponse(retorno)


def consultarServicioPrestado(request, id):
    try:
        servicioPrestado = ServicioPrestado.objects.get(id=id)

        datos_serviciosP = {
            "id": servicioPrestado.id,
            "serpObservaciones": servicioPrestado.serpObservaciones,
            "serpFechaServicio": servicioPrestado.serpFechaServicio,
            "serpEstado": servicioPrestado.serpEstado,
        }

        datos_cliente = {
            "id": servicioPrestado.serpCli.id,
            "cliPersona": {
                "perNombres": servicioPrestado.serpCli.cliPersona.perNombres,
                "perApellidos": servicioPrestado.serpCli.cliPersona.perApellidos,
            }
        }

        datos_vehiculo = {
            "id": servicioPrestado.serpVehi.id,
            "vehPlaca": servicioPrestado.serpVehi.vehPlaca,
        }

        return JsonResponse({
            "servicioPrestado": datos_serviciosP,
            "cliente": datos_cliente,
            "vehiculo": datos_vehiculo
        })
    except ServicioPrestado.DoesNotExist:
        return JsonResponse({"error": "Servicio Prestado no encontrado."}, status=404)
    except Exception as error:
        return JsonResponse({"error": str(error)}, status=500)


def actualizarSericioPrestado(request):
    estado = False
    mensaje = ""

    if request.method == "POST":
        servicioP_id = request.POST.get("idServicioP")
        nuevo_estado = request.POST.get("cbEstado")

        try:
            servicioPrestado = ServicioPrestado.objects.get(pk=servicioP_id)
            servicioPrestado.serpEstado = nuevo_estado
            servicioPrestado.save()

            estado = True
            mensaje = "Servicio Prestado actualizado correctamente."

            if nuevo_estado == "Terminado":
                # Enviar correo al cliente notificando el estado terminado
                cliente = servicioPrestado.serpCli
                asunto_cliente = 'Estado del Servicio Prestado'
                mensaje_cliente = f'Cordial saludo, {cliente.cliPersona.perNombres} {cliente.cliPersona.perApellidos}, el servicio prestado solicitado ha sido marcado como terminado,\
                    ya puede pasar por nuestra serviteca por su vehiculo.'
                thread_cliente = threading.Thread(
                    target=enviarCorreo, args=(asunto_cliente, mensaje_cliente, cliente.cliPersona.perCorreo))
                thread_cliente.start()

        except ServicioPrestado.DoesNotExist:
            return JsonResponse({"error": "Servicio prestado no encontrado."}, status=404)
        except Exception as error:
            transaction.rollback()
            mensaje = f"Error al actualizar servicio prestado: {error}."

    serviciosPrestados = ServicioPrestado.objects.all()
    retorno = {
        "mensaje": mensaje,
        "estado": estado,
        "serviciosPrestados": serviciosPrestados
    }
    return render(request, "asistente/vistaGestionarServicioPrestados.html", retorno)


def vistaGestionarServiciosPrestados(request):
    user = request.user
    if user.groups.filter(name='Asistente').exists():
        serviciosPrestados = ServicioPrestado.objects.all()
        vehiculos = Vehiculo.objects.all()
        clientes = Cliente.objects.all()
        retorno = {"serviciosPrestados": serviciosPrestados,
                   "estadoServicioPrestado": estadoServicioPrestado, "vehiculos": vehiculos, "clientes": clientes}
        return render(request, "asistente/vistaGestionarServicioPrestados.html", retorno)

    mensaje = "Nuestro sistema detecta que su rol no cuenta con los permisos necesarios para acceder a esta URL."

    if user.groups.filter(name='Administrador').exists():
        return render(request, "administrador/inicio.html", {"mensaje": mensaje})

    if user.groups.filter(name='Tecnico').exists():
        return render(request, "tecnico/inicio.html", {"mensaje": mensaje})

    return render(request, "inicio.html", {"mensaje": "Debe iniciar sesión."})


def vistaGestionarFacturas(request):
    user = request.user

    if user.groups.filter(name='Asistente').exists():
        facturasNP = Factura.objects.filter(
            facEstado="No Pagada").select_related('facServicioPrestado__serpCli')
        facturasP = Factura.objects.filter(
            facEstado="Pagada").select_related('facServicioPrestado__serpCli')
        for factura in facturasNP:
            total = sum(
                detalle.detServicio.serCosto for detalle in factura.facServicioPrestado.detalleservicioprestado_set.all())
            factura.facMonto = total
        for factura in facturasP:
            total = sum(
                detalle.detServicio.serCosto for detalle in factura.facServicioPrestado.detalleservicioprestado_set.all())
            factura.facMonto = total
        retorno = {"facturasP": facturasP, "facturasNP": facturasNP,
                   "estadoFactura": estadoFactura}
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
        return render(request, "asistente/frmEdicionPerfil.html", {"roles": roles, "tipoUsuario": tipoUsuario, "user": user})

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
        return render(request, "administrador/frmEdicionPerfil.html", {"roles": roles, "tipoUsuario": tipoUsuario, "user": user})

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
        return render(request, "tecnico/frmEdicionPerfil.html", {"roles": roles, "tipoUsuario": tipoUsuario, "user": user})

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
                mensaje = "El correo electrónico ya está en uso por otro usuario."
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
                mensaje = "El correo electrónico ya está en uso por otro usuario."
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
                mensaje = "El correo electrónico ya está en uso por otro usuario."
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
    user = request.user
    if user.groups.filter(name='Administrador').exists():
        try:
            usuario = User.objects.get(pk=user_id)

            if usuario.is_superuser:
                raise Exception("No se puede deshabilitar a un superusuario.")

            usuario.is_active = False
            usuario.save()

            return JsonResponse({
                'success': True
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    mensaje = "Nuestro sistema detecta que su rol no cuenta con los permisos necesarios para acceder a esta url."

    if user.groups.filter(name='Asistente').exists():
        return render(request, "asistente/inicio.html", {"mensaje": mensaje})

    if user.groups.filter(name='Tecnico').exists():
        return render(request, "tecnico/inicio.html", {"mensaje": mensaje})

    return render(request, "inicio.html", {"mensaje": "Debe iniciar sesión."})


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
    queryset = Persona.objects.all()
    serializer_class = PersonaSerializer


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

    ruta_grafica = os.path.join(
        settings.MEDIA_ROOT, 'graficas', 'grafica_de_barras.png')

    plt.savefig(ruta_grafica)

    generarFacturapdf(request)
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
        self.cell(0, 10, 'Fecha de creación: ' +
                  datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 0, 0, 'L')

        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, 'El impulso que necesita tu vehículo', 0, 0, 'R')


def generarFacturapdf(request):
    try:
        pdf = FPDF()
        pdf.add_page()

        # Encabezado
        pdf.set_font('Arial', 'B', 18)
        pdf.set_text_color(255, 0, 0)
        pdf.cell(0, 10, 'Factura', 0, 1, 'L')

        pdf.image(settings.MEDIA_ROOT + '/fotos/Toji.jpg', x=160, y=10, w=40)

        pdf.set_text_color(0, 0, 0)
        pdf.set_font('Arial', '', 12)
        pdf.cell(0, 10, 'Serviteca Opita', 0, 1, 'L')
        pdf.cell(0, 10, 'El impulso que necesita tu vehiculo', 0, 1, 'L')
        pdf.cell(0, 10, 'Calle 4 #7', 0, 1, 'L')
        pdf.ln(10)

        # Encabezado tabla
        pdf.set_fill_color(255, 0, 0)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font('Arial', 'B', 12)
        ancho_columnas = [20, 40, 60, 30, 30, 30]
        pdf.cell(ancho_columnas[0], 10, 'Codigo',
                 border=1, ln=False, fill=True)
        pdf.cell(ancho_columnas[1], 10, 'Cliente',
                 border=1, ln=False, fill=True)
        pdf.cell(ancho_columnas[2], 10, 'Servicio Prestado',
                 border=1, ln=False, fill=True)
        pdf.cell(ancho_columnas[3], 10, 'Estado',
                 border=1, ln=False, fill=True)
        pdf.cell(ancho_columnas[4], 10, 'Fecha', border=1, ln=False, fill=True)
        pdf.cell(ancho_columnas[5], 10, 'Total', border=1, ln=True, fill=True)
        pdf.set_fill_color(255, 255, 255)
        pdf.set_text_color(0, 0, 0)

        facturas = Factura.objects.all()
        for factura in facturas:
            pdf.set_font('Arial', '', 5)
            pdf.cell(ancho_columnas[0], 5, str(factura.facCodigo), border=1)
            pdf.cell(ancho_columnas[1], 5, str(
                factura.facServicioPrestado.serpCli), border=1)

            service_names = ", ".join(
                [str(detalle.detServicio) for detalle in factura.facServicioPrestado.detalleservicioprestado_set.all()])
            pdf.cell(ancho_columnas[2], 5, service_names, border=1)
            pdf.cell(ancho_columnas[3], 5, str(factura.facEstado), border=1)
            pdf.cell(ancho_columnas[4], 5, str(factura.facFecha), border=1)
            pdf.cell(ancho_columnas[5], 5, str(factura.facTotal), border=1)
            pdf.ln()

        # Footer
        pdf.set_y(-15)
        pdf.set_font('Arial', 'I', 8)
        pdf.cell(0, 10, 'Hola', 0, 0, 'L')
        pdf.cell(0, 10, 'Pagina ' + str(pdf.page_no()), 0, 0, 'C')
        pdf.cell(0, 10, 'Gracias por su compra', 0, 0, 'R')

        rutaPdf = settings.MEDIA_ROOT + '/pdf/Facturas.pdf'
        pdf.output(rutaPdf)

        return HttpResponse("PDF generado y guardado correctamente.")
    except Exception as e:
        return HttpResponse("Error al generar el PDF: " + str(e))


def vistaCorreoForgot(request):
    return render(request, "vistaCorreoForgot.html")


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
                # Enviar correo al usuario
                asunto = 'Solicitud de Restablecimiento de Contraseña'
                mensaje = f'Cordial saludo, {usuario.first_name} {usuario.last_name}, ha solicitado el restablecimiento de contraseña. \
                Por favor, haga clic en el siguiente enlace para continuar con el proceso: http://127.0.0.1:8000/cambiarContrasena/{uidb64}/{token}/'
                thread = threading.Thread(
                    target=enviarCorreo, args=(asunto, mensaje, usuario.email))
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
    return render(request, "cambiarContraseña.html")


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
            messages.success(
                request, 'Contraseña restablecida correctamente, ahora puedes iniciar sesión con tu nueva contraseña.')

            PeticionForgot.objects.filter(
                id_user=user).update(estado='Inactiva')
            return redirect('/mostrarMensaje/')

        peticiones = PeticionForgot.objects.filter(id_user=user)
        if peticiones.exists():
            peticion = peticiones.first()
            tiempoAc = timezone.now()
            tiempoDif = tiempoAc - peticion.fechaHoraCreacion
        # Validacion para expirar el enlace de recuperacion de contraseña segun un tiempo pre-establecido
            if tiempoDif.total_seconds() > 3600:  # 1 hora en segundos
                peticiones.update(estado='Inactiva')
                return render(request, 'cambiarContrasena.html', {'validlink': False})

        return render(request, 'cambiarContrasena.html', {'validlink': True})
    else:
        return render(request, 'cambiarContrasena.html', {'validlink': False})


def mostrarMensaje(request):
    return render(request, 'mostrarMensaje.html')
