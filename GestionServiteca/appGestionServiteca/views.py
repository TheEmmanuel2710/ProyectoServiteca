from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from appGestionServiteca.models import *
from django.contrib.auth.models import Group
from django.db import transaction
import random
import string
from django.contrib.auth import authenticate
from django.contrib import auth
from rest_framework.response import Response
from django.conf import settings
import urllib
import json
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.db.models import Sum
import threading
from django.http import Http404
from django.http import JsonResponse
from smtplib import SMTPException
from rest_framework import generics
from appGestionServiteca.serializers import PersonaSerializer, ClienteSerializer, ServicioPrestadoSerializer, DetalleServicioPrestadoSerializer
import matplotlib.pyplot as plt
import matplotlib
from fpdf import FPDF
from datetime import datetime
import os
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count
from io import BytesIO
from django.core.mail import EmailMessage
from email.mime.base import MIMEBase
from email import encoders


datosSesion = {"user": None, "rutaFoto": None, "rol": None}


def error_404(request, exception):
    return render(request, '404.html', {}, status=404)


def urlValidacion(request, texto):
    """
    Esta es una funcion cuyo fin es la autenticación del usuario y su grupo, y redirige a diferentes
    plantillas HTML con un mensaje de error si la URL ingresada no es válida.

    Args:
        request (HttpRequest): El objeto de solicitud HTTP de Django.
        texto (str): El texto que se va a validar en la URL.

    Returns:
        HttpResponse: Una respuesta HTTP que renderiza una plantilla HTML apropiada.
    """

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
    """
    Esta vista renderiza la página de inicio.

    Args:
        request (HttpRequest): El objeto de solicitud HTTP de Django.

    Returns:
        HttpResponse: Una respuesta HTTP que renderiza la página de inicio (inicio.html).
    """
    return render(request, 'inicio.html')


def inicioAdministrador(request):
    """
    Esta vista verifica si el usuario está autenticado y tiene el rol de "Administrador".
    Si es así, muestra la página de inicio del administrador. Si no, muestra un mensaje de error.

    Args:
        request (HttpRequest): El objeto de solicitud HTTP de Django.

    Returns:
        HttpResponse: Una respuesta HTTP que renderiza la página de inicio adecuada o muestra un mensaje de error.
    """

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
    """
    Esta vista verifica si el usuario está autenticado y tiene el rol de "Asistente".
    Si es así, muestra la página de inicio del asistente. Si no, muestra un mensaje de error.

    Args:
        request (HttpRequest): El objeto de solicitud HTTP de Django.

    Returns:
        HttpResponse: Una respuesta HTTP que renderiza la página de inicio adecuada o muestra un mensaje de error.
    """

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
    """
    Esta vista verifica si el usuario está autenticado y tiene el rol de "Técnico".
    Si es así, muestra la página de inicio del técnico. Si no, muestra un mensaje de error.

    Args:
        request (HttpRequest): El objeto de solicitud HTTP de Django.

    Returns:
        HttpResponse: Una respuesta HTTP que renderiza la página de inicio adecuada o muestra un mensaje de error.
    """

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
    """
    Esta función muestra una vista que permite la gestión de usuarios según el rol del usuario que realiza la solicitud.
    Los administradores pueden ver y gestionar todos los usuarios, mientras que otros roles
    obtienen un mensaje de error o son redirigidos a sus respectivas páginas de inicio.

    Args:
        request (HttpRequest): El objeto de solicitud HTTP de Django.

    Returns:
        HttpResponse: Una respuesta HTTP que renderiza la página adecuada o muestra un mensaje de error.
    """

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


def vistaRegistrarEmpleado(request):
    """
    Esta vista permite el registro de empleados en el sistema según el rol del usuario que realiza la solicitud.
    Los administradores pueden acceder a la página de registro de empleados, mientras que otros roles
    obtienen un mensaje de error o son redirigidos a sus respectivas páginas de inicio.

    Args:
        request (HttpRequest): El objeto de solicitud HTTP de Django.

    Returns:
        HttpResponse: Una respuesta HTTP que renderiza la página adecuada o muestra un mensaje de error.
    """

    user = request.user

    if user.groups.filter(name='Administrador').exists():
        roles = Group.objects.all()
        return render(request, "administrador/frmRegistrarEmpleado.html", {"roles": roles, "tipoUsuario": tipoUsuario, "estadoEmpl": estadoEmpleados, "user": user})

    mensaje = "Nuestro sistema detecta que su rol no cuenta con los permisos necesarios para acceder a esta url."

    if request.user.groups.filter(name='Tecnico').exists():
        return render(request, "tecnico/inicio.html", {"mensaje": mensaje})
    elif request.user.groups.filter(name='Asistente').exists():
        return render(request, "asistente/inicio.html", {"mensaje": mensaje})

    return render(request, "inicio.html", {"mensaje": "Debe iniciar sesión."})


def registrarEmpleado(request):
    """
    Esta vista permite registrar nuevos empleados en el sistema. El registro de empleados está condicionado
    por la validación de datos, como identificación, correo electrónico y número de celular, para evitar
    duplicados. Luego, se crea una instancia de usuario y se envía un correo electrónico con las credenciales
    de ingreso al empleado registrado.

    Args:
        request (HttpRequest): El objeto de solicitud HTTP de Django.

    Returns:
        HttpResponse: Una respuesta HTTP que renderiza la página de registro de empleado con un mensaje
        de éxito o error.
    """
    estado = False
    mensaje1 = ""

    try:
        identificacion = request.POST.get("txtIdentificacion")
        correo = request.POST.get("txtCorreo")
        numeroC = request.POST.get("txtNumeroC")
        if User.objects.filter(email=correo).exists() or Persona.objects.filter(perCorreo=correo):
            mensaje1 = "Error: El Correo electrónico ya está registrado en otro empleado."
        elif Persona.objects.filter(perIdentificacion=identificacion).exists():
            mensaje1 = "Error: La Identificación ya está registrada en otro empleado."
        elif Persona.objects.filter(perNumeroCelular=numeroC).exists():
            mensaje1 = "Error: El Número de celular ya está registrado en otro empleado."
        else:
            nombres = request.POST.get("txtNombres")
            apellidos = request.POST.get("txtApellidos")
            cargo = request.POST.get("txtCargo")
            sueldo = request.POST.get("txtSueldo")
            estadoE = request.POST.get("cbEstado")
            tipo = request.POST.get("cbTipo")
            foto = request.FILES.get("fileFoto", False)
            idRol = int(request.POST.get("cbRol"))

            with transaction.atomic():
                persona = Persona(
                    perIdentificacion=identificacion,
                    perNombres=nombres,
                    perApellidos=apellidos,
                    perNumeroCelular=numeroC,
                    perCorreo=correo
                )
                persona.save()
                empleado = Empleado(
                    empCargo=cargo,
                    empSueldo=sueldo,
                    empEstado=estadoE,
                    empPersona=persona
                )
                empleado.save()
                user = User(
                    username=correo,
                    first_name=nombres,
                    last_name=apellidos,
                    email=correo,
                    userTipo=tipo,
                    userFoto=foto,
                    userEmpleado=empleado
                )
                user.save()

                rol = Group.objects.get(pk=idRol)
                user.groups.add(rol)

                if rol.name == "Administrador":
                    user.is_staff = True

                passwordGenerado = generarPassword()
                user.set_password(passwordGenerado)
                user.save()

                mensaje1 = "Empleado Agregado Correctamente."
                estado = True

                asunto = "Registro Sistema Serviteca"
                mensaje = f"Cordial saludo, <b>{user.first_name} {user.last_name}</b>, nos permitimos\
                    informarle que usted ha sido registrado en el Sistema de ServitecaOpita.\
                    Nos permitimos enviarle las credenciales de ingreso a nuestro sistema.<br>\
                    <br><b>Username: </b> {user.username}\
                    <br><b>Password: </b> {passwordGenerado}\
                    <br><br>Lo invitamos a ingresar a nuestro sistema en la url:\
                    http://127.0.0.1:8000/"
                thread = threading.Thread(
                    target=enviarCorreo, args=(asunto, mensaje, user.email))
                thread.start()

    except Exception as error:
        transaction.rollback()
        mensaje1 = f"Error al registrar empleado: {error}."

    retorno = {"mensaje1": mensaje1, "estado": estado}
    return render(request, "administrador/frmRegistrarEmpleado.html", retorno)


def vistaGestionarClientes(request):
    """
    Esta vista permite la gestión de clientes en el sistema según el rol del usuario que realiza la solicitud.
    Los asistentes pueden acceder a la página de gestión de clientes, mientras que otros roles obtienen un
    mensaje de error o son redirigidos a sus respectivas páginas de inicio.

    Args:
        request (HttpRequest): El objeto de solicitud HTTP de Django.

    Returns:
        HttpResponse: Una respuesta HTTP que renderiza la página adecuada o muestra un mensaje de error.
    """

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
    """
    Esta vista permite el registro de nuevos clientes en el sistema. El acceso a la página de registro de clientes
    está condicionado por el rol del usuario que realiza la solicitud, en este caso, los asistentes pueden acceder
    a la página de registro de clientes, mientras que otros roles obtienen un mensaje de error o son redirigidos
    a sus respectivas páginas de inicio.

    Args:
        request (HttpRequest): El objeto de solicitud HTTP de Django.

    Returns:
        HttpResponse: Una respuesta HTTP que renderiza la página adecuada o muestra un mensaje de error.
    """

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
    """
    Esta vista permite el registro de nuevos clientes en el sistema. Se verifica la existencia de duplicados
    en la identificación, número de celular y correo electrónico para evitar registros duplicados. Luego,
    se crea una instancia de persona y cliente asociada al nuevo cliente registrado.

    Args:
        request (HttpRequest): El objeto de solicitud HTTP de Django.

    Returns:
        HttpResponse: Una respuesta HTTP que renderiza la página de registro de cliente con un mensaje
        de éxito o error.
    """

    estado = False
    mensaje = ""

    try:
        identificacion = request.POST.get("txtIdentificacion")
        numeroC = request.POST.get("txtNumeroC")
        correo = request.POST.get("txtCorreo")

        if Persona.objects.filter(perIdentificacion=identificacion).exists():
            mensaje = "Error : La Identificación ya está registrada en otro cliente."
        elif Persona.objects.filter(perNumeroCelular=numeroC).exists():
            mensaje = "Error : El Número de celular ya está registrado en otro cliente."
        elif Persona.objects.filter(perCorreo=correo).exists():
            mensaje = "Error : El Correo electrónico ya está registrado en otro cliente."
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
        transaction.rollback()
        mensaje = f"Error al registrar cliente: {error}."

    retorno = {"mensaje": mensaje, "estado": estado,
               "user": request.user if not request.user.is_anonymous else None}
    if "application/json" in request.META.get("HTTP_ACCEPT", ""):
        return JsonResponse(retorno)
    else:
        return render(request, "asistente/frmRegistrarCliente.html", retorno)


def consultarCliente(request, id):
    """
    Esta vista permite consultar los detalles de un cliente en el sistema por su ID y devuelve la información
    en formato JSON.

    Args:
        request (HttpRequest): El objeto de solicitud HTTP de Django.
        id (int): El ID del cliente que se desea consultar.

    Returns:
        JsonResponse: Una respuesta JSON que contiene los detalles del cliente o un mensaje de error si el cliente
        no se encuentra, el ID es inválido o se produce algún otro error.
    """

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
    """
    Esta vista permite consultar los detalles de una factura en el sistema por su ID y devuelve la información
    en formato JSON, incluyendo los detalles del cliente asociado, los servicios prestados en la factura y el
    total de la factura.

    Args:
        request (HttpRequest): El objeto de solicitud HTTP de Django.
        id (int): El ID de la factura que se desea consultar.

    Returns:
        JsonResponse: Una respuesta JSON que contiene los detalles de la factura y del cliente asociado, o un
        mensaje de error si la factura no se encuentra, el cliente o la persona asociada al cliente no se
        encuentran, el ID es inválido o se produce algún otro error.
    """

    try:
        factura = Factura.objects.get(pk=int(id))
        servicio_prestado = factura.facServicioPrestado
        cliente = servicio_prestado.serpCli
        persona = cliente.cliPersona
        detalles_servicios_prestados = DetalleServicioPrestado.objects.filter(
            detServicioPrestado=servicio_prestado)

        datos_persona = {
            "perNombres": persona.perNombres,
            "perApellidos": persona.perApellidos,
        }

        datos_cliente = {
            "persona": datos_persona,
        }

        servicios_con_empleados = []
        total_costo = 0

        for detalle in detalles_servicios_prestados:
            servicio = detalle.detServicio
            empleado = detalle.detEmpleado
            servicio_con_empleado = {
                "serNombre": servicio.serNombre,
                "serCosto": servicio.serCosto,
                "nombreEmpleado": empleado.empPersona.perNombres,
                "apellidoEmpleado": empleado.empPersona.perApellidos,
            }
            servicios_con_empleados.append(servicio_con_empleado)
            total_costo += servicio.serCosto

        datos_factura = {
            "facTotal": total_costo,
            "facEstado": factura.facEstado,
            "facCodigo": factura.facCodigo,
            "facFecha": factura.facFecha.strftime("%Y-%m-%d %H:%M:%S"),
            "nombresServiciosPrestados": servicios_con_empleados,
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
    """
    Esta vista permite actualizar el estado de una factura en el sistema. Se espera una solicitud HTTP POST con el ID de
    la factura y el nuevo estado. La factura se busca en la base de datos y se actualiza su estado. Luego, se muestra un
    mensaje de éxito o error y se renderiza la página de gestión de facturas.

    Args:
        request (HttpRequest): El objeto de solicitud HTTP de Django.

    Returns:
        HttpResponse: Una respuesta HTTP que renderiza la página de gestión de facturas con un mensaje de éxito o error.
    """

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
    """
    Esta vista permite gestionar vehículos en el sistema. El acceso a la página de gestión de vehículos está condicionado
    por el rol del usuario que realiza la solicitud, en este caso, los asistentes pueden acceder a la página de gestión
    de vehículos. Otros roles obtienen un mensaje de error o son redirigidos a sus respectivas páginas de inicio.

    Args:
        request (HttpRequest): El objeto de solicitud HTTP de Django.

    Returns:
        HttpResponse: Una respuesta HTTP que renderiza la página adecuada o muestra un mensaje de error.
    """

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
    """
    Esta vista permite registrar vehículos en el sistema. El acceso a la página de registro de vehículos está condicionado
    por el rol del usuario que realiza la solicitud, en este caso, los asistentes pueden acceder a la página de registro
    de vehículos. Otros roles obtienen un mensaje de error o son redirigidos a sus respectivas páginas de inicio.

    Args:
        request (HttpRequest): El objeto de solicitud HTTP de Django.

    Returns:
        HttpResponse: Una respuesta HTTP que renderiza el formulario de registro de vehículos o muestra un mensaje de error.
    """

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
    """
    Esta vista permite registrar un vehículo en el sistema. Se espera una solicitud HTTP POST con los datos del vehículo
    a registrar, incluyendo la placa, la marca, el modelo y el tipo de vehículo. Se verifica si la placa ya está
    registrada en otro vehículo y se realiza el registro si la placa no está duplicada.

    Args:
        request (HttpRequest): El objeto de solicitud HTTP de Django.

    Returns:
        HttpResponse: Una respuesta HTTP que renderiza el formulario de registro de vehículos con un mensaje de éxito o error.
    """

    estado = False
    mensaje = ""

    try:
        placa = request.POST.get("txtPlaca")

        if Vehiculo.objects.filter(vehPlaca=placa).exists():
            mensaje = "Error : La Placa ya está registrada en otro vehiculo."
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
        transaction.rollback()
        mensaje = f"Error al registrar vehículo : {error}."

    retorno = {"mensaje": mensaje, "estado": estado,
               "user": request.user if not request.user.is_anonymous else None}
    if "application/json" in request.META.get("HTTP_ACCEPT", ""):
        return JsonResponse(retorno)
    else:
        return render(request, "asistente/frmRegistrarVehiculo.html", retorno)


def consultarVehiculo(request, id):
    """
    Esta vista permite consultar la información de un vehículo en el sistema utilizando su ID. Se espera una solicitud HTTP
    GET con el ID del vehículo a consultar. La vista busca el vehículo en la base de datos y devuelve los datos del
    vehículo en formato JSON.

    Args:
        request (HttpRequest): El objeto de solicitud HTTP de Django.
        id (int): El ID del vehículo a consultar.

    Returns:
        JsonResponse: Una respuesta JSON que contiene los datos del vehículo o un mensaje de error si el vehículo no se encuentra.
    """

    try:
        vehiculo = Vehiculo.objects.get(id=id)
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
    """
    Esta vista permite gestionar empleados en el sistema. El acceso a la página de gestión de empleados está condicionado
    por el rol del usuario que realiza la solicitud. Los administradores pueden acceder a la página de gestión de empleados
    y ver una lista de usuarios registrados en el sistema. Otros roles obtienen un mensaje de error o son redirigidos a sus
    respectivas páginas de inicio.

    Args:
        request (HttpRequest): El objeto de solicitud HTTP de Django.

    Returns:
        HttpResponse: Una respuesta HTTP que renderiza la página adecuada o muestra un mensaje de error.
    """

    user = request.user

    if user.groups.filter(name='Administrador').exists():
        usuarios = User.objects.all()
        retorno = {"usuarios": usuarios,
                   "estadoEmpl": estadoEmpleados, "user": user}
        return render(request, "administrador/vistaGestionarEmpleados.html", retorno)

    mensaje = "Nuestro sistema detecta que su rol no cuenta con los permisos necesarios para acceder a esta url."

    if user.groups.filter(name='Asistente').exists():
        return render(request, "asistente/inicio.html", {"mensaje": mensaje})

    if user.groups.filter(name='Tecnico').exists():
        return render(request, "tecnico/inicio.html", {"mensaje": mensaje})

    return render(request, "inicio.html", {"mensaje": "Debe iniciar sesión."})


def consultarUsuario(request, id):
    """
    Esta vista permite consultar la información de un usuario en el sistema utilizando su ID. Se espera una solicitud HTTP
    GET con el ID del usuario a consultar. La vista busca el usuario en la base de datos y devuelve los datos del usuario
    en formato JSON, incluyendo información del empleado y la persona asociados si existen.

    Args:
        request (HttpRequest): El objeto de solicitud HTTP de Django.
        id (int): El ID del usuario a consultar.

    Returns:
        JsonResponse: Una respuesta JSON que contiene los datos del usuario o un mensaje de error si el usuario no se encuentra.
    """

    try:
        usuario = User.objects.get(pk=id)

        empleado = usuario.userEmpleado
        if empleado:
            persona = empleado.empPersona

            datos_usuario = {
                "usuario": {
                    "id": usuario.id,
                    "first_name": usuario.first_name,
                    "last_name": usuario.last_name,
                    "email": usuario.email,
                },
                "empleado": {
                    "empCargo": empleado.empCargo,
                    "empSueldo": empleado.empSueldo,
                    "empEstado": empleado.empEstado,
                },
                "persona": {
                    "perIdentificacion": persona.perIdentificacion,
                    "perNumeroCelular": persona.perNumeroCelular,
                }
            }
        else:
            datos_usuario = {
                "usuario": {
                    "id": usuario.id,
                    "username": usuario.username,
                    "email": usuario.email,
                },
                "empleado": None,
                "persona": None
            }

        return JsonResponse({"usuario": datos_usuario})

    except User.DoesNotExist:
        return JsonResponse({"error": "Usuario no encontrado."}, status=404)
    except Exception as error:
        return JsonResponse({"error": str(error)}, status=500)


def vistaLogin(request):
    """
    Esta vista renderiza la página de inicio de sesión, donde los usuarios pueden ingresar sus credenciales.

    Args:
        request (HttpRequest): El objeto de solicitud HTTP de Django.

    Returns:
        HttpResponse: Una respuesta HTTP que renderiza la página de inicio de sesión.
    """
    return render(request, "menu.html")


def login(request):
    """
    Esta vista maneja el proceso de inicio de sesión de los usuarios. Verifica las credenciales del usuario y también
    valida el reCAPTCHA. Si las credenciales son válidas y el reCAPTCHA se valida correctamente, el usuario se autentica y
    se redirige a su página de inicio correspondiente. Si no, se muestra un mensaje de error.

    Args:
        request (HttpRequest): El objeto de solicitud HTTP de Django.

    Returns:
        HttpResponse: Una respuesta HTTP que redirige al usuario a su página de inicio o muestra un mensaje de error.
    """

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
    """
    Esta vista maneja el proceso de cierre de sesión de los usuarios. Cuando un usuario cierra la sesión, se lo redirige
    a la página de inicio y se muestra un mensaje indicando que ha cerrado la sesión.

    Args:
        request (HttpRequest): El objeto de solicitud HTTP de Django.

    Returns:
        HttpResponse: Una respuesta HTTP que redirige al usuario a la página de inicio y muestra un mensaje de cierre de sesión.
    """

    auth.logout(request)
    return render(request, "inicio.html",
                  {"mensaje": "Ha cerrado la sesión."})


def enviarCorreo(asunto=None, mensaje=None, destinatario=None):
    """
    Esta función se encarga de enviar un correo electrónico a un destinatario dado con un asunto y mensaje específicos.

    Args:
        asunto (str): El asunto del correo electrónico.
        mensaje (str): El contenido del correo electrónico.
        destinatario (str): La dirección de correo electrónico del destinatario.

    Returns:
        None
    """

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
    """
    Esta vista renderiza la página para registrar servicios prestados. Dependiendo del rol del usuario autenticado, muestra
    diferentes opciones y formularios para registrar servicios prestados, empleados, vehículos y clientes.

    Args:
        request (HttpRequest): El objeto de solicitud HTTP de Django.

    Returns:
        HttpResponse: Una respuesta HTTP que renderiza la página para registrar servicios prestados.
    """

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
    """
    Esta función se encarga de obtener el siguiente número de factura disponible. Busca la última factura registrada en la base de datos
    y aumenta el número en 1. Si no hay facturas registradas, devuelve 1 como el primer número de factura.

    Returns:
        int: El siguiente número de factura disponible.
    """

    ultimaFactura = Factura.objects.last()
    if ultimaFactura:
        ultimoNumero = int(ultimaFactura.facCodigo[-1])
        nuevoNumero = ultimoNumero + 1
    else:
        nuevoNumero = 1
    return nuevoNumero


def generarCodigoFactura():
    """
    Genera un código de factura único con el formato 'SVP-XXXXXX'.

    Esta función se utiliza para generar un código de factura único para su posterior uso
    en la creación de facturas relacionadas con servicios prestados. El código de factura
    está compuesto por 'SVP-' seguido de un número entero único.

    :return: Una cadena de texto que representa el código de factura generado.
    :rtype: str
    """

    siguienteNumero = obtenerSiguienteNumeroFactura()
    return f'SVP-{siguienteNumero:06d}'


def registrarServicioPrestado(request):
    """
    Esta funcion permite registrar un serivicioPrestado a la base de datos,
    tambien manda un correo electronico al cliente asociado al servicio prestado y tambien envia en
    un correo electronico a los empleados que esten asociados al detalle servicio prestado,por otra
    parte tambien genera un factura en pdf con los datos del servicio prestado y el detalle servicio
    prestado. 

    Args:
        request (_type_): _description_

    Returns:
        _type_: _description_
    """

    estado = False
    mensaje = ""

    if request.method == 'POST':
        rollback_requerido = False
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
                        detEmpleado=empleado
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

                # Llama a generarFacturaPdf con el objeto de factura
                factura_pdf = generarFacturaPdf(servicioPrestado, factura)

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
                    mensaje_empleado = f"Le informamos que se le ha asignado el siguiente servicio: {servicios_asignados_str} el cual deberá ser atendido en el vehículo con placa: {vehiculo_placa}, en nombre del cliente: {cliente_nombre}. Agradecemos su atención y diligencia en la prestación de este servicio."
                    thread_empleado = threading.Thread(
                        target=enviarCorreo, args=(asunto_empleado, mensaje_empleado, empleado.empPersona.perCorreo))
                    thread_empleado.start()

                # Enviar correo al cliente con los servicios, costos y el PDF adjunto
                servicios_cliente_str = ", ".join(
                    [f"{Servicio.objects.get(id=int(detalle['idServicio'])).serNombre}: ${Servicio.objects.get(id=int(detalle['idServicio'])).serCosto}" for detalle in detalleServicioPrestado_lista])
                asunto_cliente = 'Registro de Servicios Solicitados'
                mensaje_cliente = f"Estimado(a) {cliente.cliPersona.perNombres} {cliente.cliPersona.perApellidos}, reciba un cordial saludo,nos complace informarle que su servicio ha sido registrado con los siguientes detalles: {servicios_cliente_str}. Agradecemos su confianza en nuestros servicios y quedamos a su disposición para cualquier consulta adicional."

                # Crear el objeto de correo electrónico
                correo_cliente = EmailMessage(
                    asunto_cliente, mensaje_cliente, settings.EMAIL_HOST_USER, [cliente.cliPersona.perCorreo])

                # Adjuntar el PDF a través de un MIMEBase
                if factura_pdf:
                    pdf_attachment = MIMEBase('application', 'octet-stream')
                    pdf_attachment.set_payload(factura_pdf.getvalue())
                    encoders.encode_base64(pdf_attachment)
                    pdf_attachment.add_header('Content-Disposition',
                                              'attachment; filename=Factura.pdf')
                    correo_cliente.attach(pdf_attachment)

                # Enviar el correo al cliente
                correo_cliente.send()

                estado = True
                mensaje = "Se ha registrado el servicio prestado y generado la factura correctamente."

        except Cliente.DoesNotExist:
            mensaje = "El cliente no existe."
            rollback_requerido = False
        except Exception as error:
            rollback_requerido = True
            mensaje = f"Error,{error}"
        if rollback_requerido:
            transaction.rollback()
    retorno = {"estado": estado, "mensaje": mensaje}
    return JsonResponse(retorno)


def consultarServicioPrestado(request, id):
    """
    Consulta los detalles de un servicio prestado y devuelve la información en formato JSON.

    Esta función busca un servicio prestado por su ID en la base de datos y recopila información relacionada,
    incluyendo detalles del cliente, detalles del vehículo y detalles de los servicios asignados y empleados asignados.

    :param request: La solicitud HTTP que contiene el ID del servicio prestado a consultar.
    :type request: HttpRequest

    :param id: El ID del servicio prestado a consultar.
    :type id: int

    :return: Un objeto JsonResponse con los detalles del servicio prestado.
    :rtype: JsonResponse
    """

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
        detalles_servicio = DetalleServicioPrestado.objects.filter(
            detServicioPrestado=servicioPrestado)

        datos_detalles = []

        for detalle in detalles_servicio:
            servicio_detalle = detalle.detServicio
            empleado_detalle = detalle.detEmpleado

            datos_detalles.append({
                "servicio": {
                    "serNombre": servicio_detalle.serNombre,
                    "serCosto": servicio_detalle.serCosto,
                },
                "empleado": {
                    "perNombres": empleado_detalle.empPersona.perNombres,
                    "perApellidos": empleado_detalle.empPersona.perApellidos,
                }
            })

        datos_vehiculo = {
            "id": servicioPrestado.serpVehi.id,
            "vehPlaca": servicioPrestado.serpVehi.vehPlaca,
        }

        return JsonResponse({
            "servicioPrestado": datos_serviciosP,
            "cliente": datos_cliente,
            "vehiculo": datos_vehiculo,
            "detalles": datos_detalles
        })

    except ServicioPrestado.DoesNotExist:
        return JsonResponse({"error": "Servicio Prestado no encontrado."}, status=404)
    except Exception as error:
        return JsonResponse({"error": str(error)}, status=500)


def actualizarServicioPrestado(request):
    """
    Actualiza el estado de un servicio prestado y, si corresponde, notifica a los clientes mediante correos electrónicos.

    Esta función permite cambiar el estado de un servicio prestado, como "Solicitado," "En Progreso," "Terminado" o "Cancelado".
    En caso de que el estado se actualice a "Terminado" o "Cancelado," se envían correos electrónicos a los clientes para notificarlos.

    :param request: La solicitud HTTP que contiene el ID del servicio prestado y el nuevo estado.
    :type request: HttpRequest

    :return: Una respuesta HTTP con la vista de gestión de servicios prestados actualizada.
    :rtype: HttpResponse
    """

    estado = False
    mensaje = ""

    if request.method == "POST":
        servicioP_id = request.POST.get("idServicioP")
        nuevo_estado = request.POST.get("cbEstado")

        try:
            servicioPrestado = ServicioPrestado.objects.get(pk=servicioP_id)

            if nuevo_estado == "Cancelado":
                # Enviar correo al cliente notificando la cancelación
                cliente = servicioPrestado.serpCli
                asunto_cliente = 'Cancelación del Servicio Prestado'
                mensaje_cliente = f"Estimado(a) {cliente.cliPersona.perNombres} {cliente.cliPersona.perApellidos}, lamentamos informarle que el servicio prestado que había solicitado ha sido cancelado. Le ofrecemos nuestras disculpas por cualquier inconveniente que esto pueda causarle. Si tiene alguna pregunta o requiere más información, no dude en contactarnos."
                thread_cliente = threading.Thread(
                    target=enviarCorreo, args=(asunto_cliente, mensaje_cliente, cliente.cliPersona.perCorreo))
                thread_cliente.start()

            servicioPrestado.serpEstado = nuevo_estado
            servicioPrestado.save()

            estado = True
            mensaje = "Servicio Prestado actualizado correctamente."

            if nuevo_estado == "Terminado":
                # Enviar correo al cliente notificando el estado terminado
                cliente = servicioPrestado.serpCli
                asunto_cliente = 'Estado del Servicio Prestado'
                mensaje_cliente = f"Estimado(a) {cliente.cliPersona.perNombres} {cliente.cliPersona.perApellidos}, Nos complace informarle que el servicio prestado que solicitó ha sido marcado como concluido, le invitamos a que pase por nuestra serviteca para recoger su vehículo. Quedamos a su disposición para cualquier consulta adicional."
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
    """
    Muestra una vista de gestión de servicios prestados según el rol del usuario.

    Esta función verifica el rol del usuario y muestra una vista de gestión de servicios prestados apropiada.
    Los asistentes pueden ver y gestionar servicios prestados, mientras que otros roles no tienen acceso.

    :param request: La solicitud HTTP del usuario.
    :type request: HttpRequest

    :return: Una vista HTML con la gestión de servicios prestados correspondiente al rol del usuario.
    :rtype: HttpResponse
    """

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
    """
    Muestra una vista de gestión de facturas según el rol del usuario asistente.

    Esta función verifica el rol del usuario y muestra una vista de gestión de facturas adaptada a los asistentes.
    Los asistentes pueden ver y gestionar facturas de servicios prestados.

    :param request: La solicitud HTTP del usuario.
    :type request: HttpRequest

    :return: Una vista HTML con la gestión de facturas correspondiente al rol del usuario asistente.
    :rtype: HttpResponse
    """

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
    """
    Renderiza la página de gestión de solicitudes de vehículos según el rol del usuario.

    Args:
        request: El objeto de solicitud de Django.

    Returns:
        HttpResponse: Una respuesta HTTP que representa la página de gestión de solicitudes de vehículos.
    """

    user = request.user

    if user.groups.filter(name='Tecnico').exists():
        serviciosPrestados = ServicioPrestado.objects.all()
        vehiculos = Vehiculo.objects.all()
        clientes = Cliente.objects.all()
        retorno = {"serviciosPrestados": serviciosPrestados,
                   "estadoServicioPrestado": estadoServicioPrestado, "vehiculos": vehiculos, "clientes": clientes}

        return render(request, "tecnico/vistaGestionarSolicitudesVehiculos.html", retorno)

    mensaje = "Nuestro sistema detecta que su rol no cuenta con los permisos necesarios para acceder a esta url."

    if user.groups.filter(name='Administrador').exists():
        return render(request, "administrador/inicio.html", {"mensaje": mensaje})

    if user.groups.filter(name='Asistente').exists():
        return render(request, "asistente/inicio.html", {"mensaje": mensaje})

    return render(request, "inicio.html", {"mensaje": "Debe iniciar sesión."})


def actualizarVehiculo(request):
    """
    Actualiza la información de un vehículo en la base de datos.

    Args:
        request: El objeto de solicitud de Django que contiene los datos de actualización.

    Returns:
        HttpResponse: Una respuesta HTTP que representa la página de gestión de vehículos actualizada.
    """

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
                mensaje = "La nueva placa ya está en uso por otro vehículo."
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
    """
    Actualiza la información de un cliente en la base de datos.

    Args:
        request: El objeto de solicitud de Django que contiene los datos de actualización.

    Returns:
        HttpResponse: Una respuesta HTTP que representa la página de gestión de clientes actualizada.
    """

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
                mensaje = "La nueva identificación ya está en uso por otro cliente."
            elif Persona.objects.exclude(id=persona.id).filter(perCorreo=correo).exists():
                mensaje = "El nuevo correo electrónico ya está en uso por otro cliente."
            elif Persona.objects.exclude(id=persona.id).filter(perNumeroCelular=numero).exists():
                mensaje = "El nuevo número de celular ya está en uso por otro cliente."
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
    """
    Actualiza la información de un empleado en la base de datos.

    Args:
        request: El objeto de solicitud de Django que contiene los datos de actualización.

    Returns:
        HttpResponse: Una respuesta HTTP que representa la página de gestión de empleados actualizada.
    """

    estado = False
    mensaje = ""

    try:
        idUsuario = int(request.POST.get("idUsuario"))
        identificacion = request.POST.get("txtIdentificacion")
        nombres = request.POST.get("txtNombres")
        apellidos = request.POST.get("txtApellidos")
        cargo = request.POST.get("txtCargo")
        sueldo = request.POST.get("txtSueldo")
        estadoE = request.POST.get("cbEstado")
        correo = request.POST.get("txtCorreo")
        numero = request.POST.get("txtNumeroC")

        with transaction.atomic():
            usuario = User.objects.select_for_update().get(pk=idUsuario)
            empleado = usuario.userEmpleado
            persona = empleado.empPersona

            if Persona.objects.exclude(id=persona.id).filter(perIdentificacion=identificacion).exists():
                mensaje = "La  nueva identificación ya está en uso por otro empleado."
            elif Persona.objects.exclude(id=persona.id).filter(perCorreo=correo).exists() or User.objects.filter(email=correo).exists():
                mensaje = "El nuevo correo electrónico ya está en uso por otro empleado."
            elif Persona.objects.exclude(id=persona.id).filter(perNumeroCelular=numero).exists():
                mensaje = "El nuevo número de celular ya está en uso por otro empleado."
            else:
                persona.perIdentificacion = identificacion
                persona.perNombres = nombres
                persona.perApellidos = apellidos
                persona.perCorreo = correo
                persona.perNumeroCelular = numero
                persona.save()

                usuario.first_name = nombres
                usuario.last_name = apellidos
                usuario.email = correo
                usuario.save()

                empleado.empCargo = cargo
                empleado.empSueldo = sueldo
                empleado.empEstado = estadoE
                empleado.save()
                estado = True
                mensaje = "Empleado actualizado correctamente."
    except User.DoesNotExist:
        mensaje = "El Usuario no existe."
    except Empleado.DoesNotExist:
        mensaje = "El Empleado no existe."
    except Exception as error:
        transaction.rollback()
        mensaje = f"Error: {error}"

    usuarios = User.objects.all()
    retorno = {
        "mensaje": mensaje,
        "estado": estado,
        "usuarios": usuarios,
    }

    return render(request, "administrador/vistaGestionarEmpleados.html", retorno)


def vistaEdicionPerfilAsistente(request):
    """
    Muestra una página de edición de perfil para un usuario con el rol de "Asistente".

    Args:
        request: El objeto de solicitud de Django.

    Returns:
        HttpResponse: Una respuesta HTTP que representa la página de edición de perfil.
    """

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
    """
    Muestra una página de edición de perfil para un usuario con el rol de "Administrador".

    Args:
        request: El objeto de solicitud de Django.

    Returns:
        HttpResponse: Una respuesta HTTP que representa la página de edición de perfil.
    """

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
    """
    Muestra una página de edición de perfil para un usuario con el rol de "Tecnico".

    Args:
        request: El objeto de solicitud de Django.

    Returns:
        HttpResponse: Una respuesta HTTP que representa la página de edición de perfil.
    """

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
    """
    Actualiza la información del usuario administrador, incluyendo nombre, apellidos, correo electrónico y foto de perfil.

    Args:
        request: El objeto de solicitud de Django.

    Returns:
        HttpResponse: Una respuesta HTTP que representa la página de edición de perfil del usuario.
    """

    estado = False
    mensaje = ""
    try:
        nombres = request.POST.get('txtNombres')
        apellidos = request.POST.get('txtApellidos')
        correo = request.POST.get('txtCorreo')
        nueva_imagen = request.FILES.get('fileFoto')

        with transaction.atomic():
            if User.objects.exclude(id=request.user.id).filter(email=correo).exists():
                mensaje = "El nuevo correo electrónico ya está en uso por otro empleado."
            else:
                usuario = request.user
                empleado = usuario.userEmpleado
                persona = empleado.empPersona

                persona.perNombres = nombres
                persona.perApellidos = apellidos
                persona.perCorreo = correo
                persona.save()

                usuario.email = correo
                usuario.first_name = nombres
                usuario.last_name = apellidos
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
    """
    Actualiza la información del usuario asistente, incluyendo nombre, apellidos, correo electrónico y foto de perfil.

    Args:
        request: El objeto de solicitud de Django.

    Returns:
        HttpResponse: Una respuesta HTTP que representa la página de edición de perfil del usuario.
    """

    estado = False
    mensaje = ""
    try:
        nombres = request.POST.get('txtNombres')
        apellidos = request.POST.get('txtApellidos')
        correo = request.POST.get('txtCorreo')
        nueva_imagen = request.FILES.get('fileFoto')

        with transaction.atomic():
            if User.objects.exclude(id=request.user.id).filter(email=correo).exists():
                mensaje = "El nuevo correo electrónico ya está en uso por otro empleado."
            else:
                usuario = request.user
                empleado = usuario.userEmpleado
                persona = empleado.empPersona

                persona.perNombres = nombres
                persona.perApellidos = apellidos
                persona.perCorreo = correo
                persona.save()

                usuario.email = correo
                usuario.first_name = nombres
                usuario.last_name = apellidos
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
    """
    Actualiza la información del usuario tecnico, incluyendo nombre, apellidos, correo electrónico y foto de perfil.

    Args:
        request: El objeto de solicitud de Django.

    Returns:
        HttpResponse: Una respuesta HTTP que representa la página de edición de perfil del usuario.
    """

    estado = False
    mensaje = ""
    try:
        nombres = request.POST.get('txtNombres')
        apellidos = request.POST.get('txtApellidos')
        correo = request.POST.get('txtCorreo')
        nueva_imagen = request.FILES.get('fileFoto')

        with transaction.atomic():
            if User.objects.exclude(id=request.user.id).filter(email=correo).exists():
                mensaje = "El nuevo correo electrónico ya está en uso por otro usuario."
            else:
                usuario = request.user
                empleado = usuario.userEmpleado
                persona = empleado.empPersona

                persona.perNombres = nombres
                persona.perApellidos = apellidos
                persona.perCorreo = correo
                persona.save()

                usuario.email = correo
                usuario.first_name = nombres
                usuario.last_name = apellidos
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
    """
    Deshabilita un usuario en función de los permisos y el rol del usuario que realiza la solicitud.

    Args:
        request: El objeto de solicitud de Django.
        user_id: El ID del usuario que se desea deshabilitar.

    Returns:
        JsonResponse: Una respuesta JSON que indica si se ha deshabilitado con éxito el usuario.
    """

    user = request.user
    if user.groups.filter(name='Administrador').exists():
        try:
            usuario = User.objects.get(pk=user_id)

            if user.groups.filter(name='Administrador').exists() and user.is_superuser:
                if usuario.groups.filter(name='Administrador').exists() and usuario.is_superuser:
                    return JsonResponse({'success': False, 'error': 'No puedes deshabilitar a otro administrador y superusuario.'})

                usuario.is_active = False
                usuario.save()

                return JsonResponse({'success': True})

            if user.groups.filter(name='Administrador').exists():
                if usuario.groups.filter(name='Administrador').exists() or usuario.is_superuser:
                    return JsonResponse({'success': False, 'error': 'No tienes permisos para deshabilitar este usuario.'})

                usuario.is_active = False
                usuario.save()

                return JsonResponse({'success': True})

            return JsonResponse({'success': False, 'error': 'No tienes permisos para deshabilitar usuarios.'})

        except User.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'El usuario no existe.'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    mensaje = "Nuestro sistema detecta que su rol no cuenta con los permisos necesarios para acceder a esta URL."

    if user.groups.filter(name='Asistente').exists():
        return render(request, "asistente/inicio.html", {"mensaje": mensaje})

    if user.groups.filter(name='Tecnico').exists():
        return render(request, "tecnico/inicio.html", {"mensaje": mensaje})

    return render(request, "inicio.html", {"mensaje": "Debe iniciar sesión."})


def habilitarUsuario(request, user_id):
    """
    Habilita un usuario previamente deshabilitado.

    Args:
        request: El objeto de solicitud de Django.
        user_id: El ID del usuario que se desea habilitar.

    Returns:
        JsonResponse: Una respuesta JSON que indica si se ha habilitado con éxito el usuario.
    """

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


# -----INICIO API-----
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

    def get_object(self):
        perIdentificacion = self.kwargs.get('perIdentificacion')
        try:
            return Cliente.objects.get(cliPersona__perIdentificacion=perIdentificacion)
        except Cliente.DoesNotExist:
            raise Http404


class ServicioPrestadoList(generics.ListCreateAPIView):
    queryset = ServicioPrestado.objects.all()
    serializer_class = ServicioPrestadoSerializer


class ServicioPrestadoDetalladoList(generics.ListCreateAPIView):
    serializer_class = ServicioPrestadoSerializer

    def get_queryset(self):
        perIdentificacion = self.kwargs['perIdentificacion']

        cliente = Cliente.objects.filter(
            cliPersona__perIdentificacion=perIdentificacion).first()

        if cliente:
            queryset = ServicioPrestado.objects.filter(serpCli=cliente)
        else:
            queryset = ServicioPrestado.objects.none()

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        if queryset.exists():
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        else:
            return Response({"detail": "No se encontraron servicios prestados."})


# class ServicioPrestadoDetail(generics.RetrieveUpdateDestroyAPIView):
#     queryset = ServicioPrestado.objects.all()
#     serializer_class = ServicioPrestadoSerializer


class DetalleServicioPrestadoList(generics.ListCreateAPIView):
    serializer_class = DetalleServicioPrestadoSerializer

    def get_queryset(self):
        id_servicio_prestado = self.kwargs.get('id')
        return DetalleServicioPrestado.objects.filter(detServicioPrestado=id_servicio_prestado)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = DetalleServicioPrestadoSerializer(queryset, many=True)
        data = serializer.data
        return Response(data)


# -----FIN API -----


def mostrarGrafica1(request):
    """
    Genera y muestra una gráfica de barras que representa la cantidad de solicitudes por servicio.

    Args:
        request: El objeto de solicitud de Django.

    Returns:
        render: Una respuesta de renderización de Django que muestra la gráfica en una vista.
    """

    matplotlib.use('Agg')
    todos_servicios = Servicio.objects.all()
    if DetalleServicioPrestado.objects.exists():
        servicios_con_registros = Servicio.objects.filter(
            detalleservicioprestado__isnull=False).distinct()

        servicios_con_cantidad = servicios_con_registros.annotate(
            cantidad_solicitudes=Count('detalleservicioprestado'))

        cantidad_solicitudes_dict = {
            servicio.id: 0 for servicio in servicios_con_registros}

        for servicio in servicios_con_cantidad:
            cantidad_solicitudes_dict[servicio.id] = int(
                servicio.cantidad_solicitudes)

        nombresS = [servicio.serNombre for servicio in servicios_con_registros]

        valores = [cantidad_solicitudes_dict[servicio.id]
                   for servicio in servicios_con_registros]
    else:
        nombresS = [servicio.serNombre for servicio in todos_servicios]
        valores = [0] * len(todos_servicios)

    plt.figure(figsize=(10, 6))
    plt.bar(nombresS, valores)
    plt.xlabel('Servicios')
    plt.ylabel('Cantidad de Solicitudes')
    plt.title('Cantidad de Solicitudes por Servicio')

    ruta_grafica = os.path.join(
        settings.MEDIA_ROOT, 'graficas', 'grafica_de_servicios.png')

    plt.xticks(rotation=45)

    if valores:
        plt.yticks(range(min(valores), max(valores) + 1))

    plt.tight_layout()

    plt.savefig(ruta_grafica)

    retorno = {
        "ruta_grafica": ruta_grafica
    }
    return render(request, "administrador/vistaGraficas.html", retorno)


def mostrarGrafica2(request):
    """
    Genera y muestra una gráfica de barras que representa la cantidad de servicios prestados por cada empleado.

    Args:
        request: El objeto de solicitud de Django.

    Returns:
        render: Una respuesta de renderización de Django que muestra la gráfica en una vista.
    """

    matplotlib.use('Agg')

    if DetalleServicioPrestado.objects.exists():
        empleados_con_registros = Empleado.objects.filter(
            detalleservicioprestado__isnull=False).distinct()

        empleados_con_cantidad = empleados_con_registros.annotate(
            cantidad_servicios_prestados=Count('detalleservicioprestado'))

        cantidad_servicios_dict = {
            empleado.id: 0 for empleado in empleados_con_registros}

        for empleado in empleados_con_cantidad:
            cantidad_servicios_dict[empleado.id] = int(
                empleado.cantidad_servicios_prestados)

        nombres_empleados = [
            empleado.empPersona.perNombres for empleado in empleados_con_registros]

        cantidad_servicios = [cantidad_servicios_dict[empleado.id]
                              for empleado in empleados_con_registros]
    else:
        todos_empleados = Empleado.objects.all()
        nombres_empleados = [
            empleado.empPersona.perNombres for empleado in todos_empleados]
        cantidad_servicios = [0] * len(todos_empleados)

    plt.figure(figsize=(10, 6))
    plt.bar(nombres_empleados, cantidad_servicios)
    plt.xlabel('Empleados')
    plt.ylabel('Cantidad de Servicios Prestados')
    plt.title('Cantidad de Servicios Prestados por Empleado')

    ruta_grafica = os.path.join(
        settings.MEDIA_ROOT, 'graficas', 'grafica_de_barras_empleados.png')

    plt.xticks(rotation=45)

    if cantidad_servicios:
        plt.yticks(range(min(cantidad_servicios), max(cantidad_servicios) + 1))

    plt.tight_layout()

    plt.savefig(ruta_grafica)

    retorno = {
        "ruta_grafica": ruta_grafica
    }
    return render(request, "administrador/vistaGraficas.html", retorno)


def mostrarGrafica3(request):
    """
    Genera y muestra una gráfica de barras que representa la cantidad de solicitudes de servicios prestados por cada cliente.

    Args:
        request: El objeto de solicitud de Django.

    Returns:
        render: Una respuesta de renderización de Django que muestra la gráfica en una vista.
    """

    matplotlib.use('Agg')

    todos_clientes = Cliente.objects.all()

    if ServicioPrestado.objects.exists():
        clientes_con_cantidad = Cliente.objects.filter(servicioprestado__isnull=False).annotate(
            cantidad_servicios_prestados=Count('servicioprestado'))

        nombres_clientes = [
            cliente.cliPersona.perNombres for cliente in clientes_con_cantidad]

        cantidad_servicios = [int(cliente.cantidad_servicios_prestados)
                              for cliente in clientes_con_cantidad]
    else:
        nombres_clientes = [
            cliente.cliPersona.perNombres for cliente in todos_clientes]
        cantidad_servicios = [0] * len(todos_clientes)

    plt.figure(figsize=(10, 6))
    plt.bar(nombres_clientes, cantidad_servicios)
    plt.xlabel('Clientes')
    plt.ylabel('Cantidad de Solicitudes de Servicios Prestados')
    plt.title('Cantidad de Servicios Prestados a Clientes')

    ruta_grafica = os.path.join(
        settings.MEDIA_ROOT, 'graficas', 'grafica_de_barras_clientes.png')

    plt.xticks(rotation=45)

    if cantidad_servicios:
        plt.yticks(range(min(cantidad_servicios), max(cantidad_servicios) + 1))

    plt.tight_layout()

    plt.savefig(ruta_grafica)

    retorno = {
        "ruta_grafica": ruta_grafica
    }
    return render(request, "administrador/vistaGraficas.html", retorno)


def mostrarGraficas(request):
    mostrarGrafica1(request)
    mostrarGrafica2(request)
    mostrarGrafica3(request)
    return render(request, "administrador/vistaGraficas.html")


def generarFacturaPdf(servicioPrestado, factura):
    try:
        pdf = FPDF()
        pdf.add_page()
        total_paginas = pdf.page_no()
        # Encabezado
        pdf.set_font('Arial', '', 12)
        pdf.cell(0, 10, 'Factura', 0, 1, 'L')
        pdf.image(settings.MEDIA_ROOT +
                  '/fotos/LogoNegroSF.png', x=160, y=10, w=40)
        pdf.set_text_color(0, 0, 0)

        # Código de la factura
        pdf.cell(0, 10, 'Código de la Factura: ' +
                 str(factura.facCodigo), 0, 1, 'L')

        # Cliente y Fecha
        cliente = servicioPrestado.serpCli
        fecha_formateada = factura.facFecha.strftime('%d/%m/%Y')
        cliente_fecha = f'{str(cliente)}            Fecha: {fecha_formateada}'
        pdf.cell(0, 10, cliente_fecha, 0, 1, 'L')

        pdf.ln(10)

        imagen_y = pdf.get_y()
        nueva_posicion_imagen = imagen_y + 70
        pdf.image(settings.MEDIA_ROOT + '/fotos/Firma.png',
                  x=10, y=nueva_posicion_imagen, w=200, h=150)

        # Encabezado de la tabla
        pdf.set_fill_color(255, 255, 255)
        pdf.set_text_color(0, 0, 0)
        pdf.set_font('Arial', '', 12)
        ancho_columnas = [80, 40, 40]
        pdf.cell(
            ancho_columnas[0], 10, 'Servicio', border=1, ln=False, fill=True)
        pdf.cell(ancho_columnas[1], 10, 'Costo Unitario',
                 border=1, ln=False, fill=True)
        pdf.cell(ancho_columnas[2], 10, 'Cantidad',
                 border=1, ln=True, fill=True)
        pdf.set_font('Arial', '', 12)

        servicios_prestados = servicioPrestado.detalleservicioprestado_set.all()
        total_costo = servicios_prestados.aggregate(
            total_costo=Sum('detServicio__serCosto'))['total_costo']

        for servicio_prestado in servicios_prestados:
            try:
                pdf.cell(ancho_columnas[0], 10,
                         str(servicio_prestado.detServicio), border=1)
                pdf.cell(ancho_columnas[1], 10,
                         '$'+str(servicio_prestado.detServicio.serCosto), border=1)
                pdf.cell(ancho_columnas[2], 10, str(1), border=1)
                pdf.ln()
            except Exception as e:
                print("Error al procesar detalles de servicios:", str(e))

        pdf.cell(ancho_columnas[0], 10, 'Total', border=1)
        pdf.cell(ancho_columnas[1], 10, '$'+str(total_costo), border=1)
        pdf.ln()

        pdf.set_line_width(0.5)
        y_linea = nueva_posicion_imagen + 78
        pdf.line(10, y_linea, 200, y_linea)

        pdf.set_font('Arial', '', 12)
        nueva_posicion_texto = y_linea + 8
        pdf.set_y(nueva_posicion_texto)
        pdf.cell(0, 10, 'Emmanuel Gonzalez - Gerencia', 0, 1, 'C')

        # Pie de página
        pdf.set_y(1)
        pdf.set_font('Arial', 'I', 8)
        pdf.cell(
            0, 10, f'Página {pdf.page_no()} de {total_paginas}', 0, 0, 'C')

        pdf_output = BytesIO()
        pdf_output.write(pdf.output(dest='S').encode('latin1'))

        return pdf_output
    except Exception as e:
        print("Error al generar el PDF:", str(e))
        return False


def vistaCorreoForgot(request):
    """
    Vista para mostrar un formulario de solicitud de recuperación de contraseña por correo electrónico.

    Parameters:
    - request: El objeto de solicitud HTTP que se recibe al acceder a esta vista.

    Returns:
    - HttpResponse: Una respuesta HTTP que representa la página HTML con el formulario de recuperación de contraseña.
    """

    return render(request, "vistaCorreoForgot.html")


def registrarPeticionForgot(request):
    """
    Vista para registrar una solicitud de restablecimiento de contraseña por correo electrónico.

    Parameters:
    - request: El objeto de solicitud HTTP que se recibe al enviar el formulario de solicitud de restablecimiento de contraseña.

    Returns:
    - HttpResponse: Una respuesta HTTP que representa la página de respuesta después de registrar la solicitud.
    """

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
                mensaje = f'Cordial saludo, {usuario.first_name} {usuario.last_name}, ha solicitado el restablecimiento de contraseña.<br> \
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
    """
    Vista para mostrar el formulario de cambio de contraseña.

    Parameters:
    - request: El objeto de solicitud HTTP.

    Returns:
    - HttpResponse: Una respuesta HTTP que representa la página de cambio de contraseña.
    """

    return render(request, "cambiarContraseña.html")


def cambiarContraseña(request, uidb64, token):
    """
    Vista para cambiar la contraseña de un usuario que ha solicitado restablecerla.

    Parameters:
    - request: El objeto de solicitud HTTP.
    - uidb64 (str): El ID de usuario codificado en base64.
    - token (str): El token de seguridad generado para el usuario.

    Returns:
    - HttpResponse: Una respuesta HTTP que representa la página de cambio de contraseña.
    """

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
    """
    Vista para mostrar un mensaje de éxito después de que el usuario ha cambiado su contraseña con éxito.

    Parameters:
    - request: El objeto de solicitud HTTP.

    Returns:
    - HttpResponse: Una respuesta HTTP que representa la página de mensaje de éxito.
    """

    return render(request, 'mostrarMensaje.html')
