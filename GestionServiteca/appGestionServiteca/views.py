from django.shortcuts import render,redirect
from appGestionServiteca.models import *
from django.contrib.auth.models import Group
from django.db import Error,transaction
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


# Create your views here.
datosSesion={"user":None,"rutaFoto":None, "rol":None}

def inicio(request):
    return render(request,"inicio.html")

def inicioAdministrador(request):
    if request.user.is_authenticated:
        datosSesion={"user": request.user}
        return render(request,"administrador/inicio.html", datosSesion)
    else:
        mensaje="Debe iniciar sesión"
        return render(request, "inicio.html",{"mensaje":mensaje})

def inicioAsistente(request):
    if request.user.is_authenticated:
        datosSesion={"user": request.user}
        return render(request,"asistente/inicio.html", datosSesion)
    else:
        mensaje="Debe iniciar sesión"
        return render(request, "inicio.html",{"mensaje":mensaje})

def inicioTecnico(request):
    if request.user.is_authenticated:
        datosSesion={"user": request.user}
        return render(request,"tecnico/inicio.html", datosSesion)
    else:
        mensaje="Debe iniciar sesión"
        return render(request, "inicio.html",{"mensaje":mensaje})

def inicioCliente(request):
    return render(request,"cliente/inicio.html")
        
    
def vistaRegistrarUsuario(request):
    if request.user.is_authenticated:
        roles = Group.objects.all()
        retorno = {"roles":roles,"tipoUsuario":tipoUsuario,"user":request.user}
        return render(request, "administrador/frmRegistrarUsuario.html",retorno)
    else:
        mensaje="Debe iniciar sesión"
        return render(request, "inicio.html",{"mensaje":mensaje})

def vistaGestionarUsuarios(request):
    if request.user.is_authenticated:
        usuarios=User.objects.all()
        retorno = {"usuarios":usuarios,"user":request.user}
        return render(request,"administrador/vistaGestionarUsuarios.html",retorno)
    else:
        mensaje="Debe iniciar sesión"
        return render(request, "inicio.html",{"mensaje":mensaje})

def registrarUsuario(request):
    try:
        nombres = request.POST["txtNombres"]
        apellidos = request.POST["txtApellidos"]
        correo = request.POST["txtCorreo"]
        tipo = request.POST["cbTipo"]
        foto = request.FILES.get("fileFoto",False)
        idRol = int(request.POST["cbRol"])
        with transaction.atomic():
            #crear un objeto de tipo User
            user = User(username=correo, first_name=nombres, last_name=apellidos, email=correo, userTipo=tipo, userFoto=foto)
            user.save()
            #obtener el Rol de acuerdo a id del rol 
            rol=Group.objects.get(pk=idRol)
            #agregar el usuario a ese Rol
            user.groups.add(rol)
            #si el rol es Administrador se habilita para que tenga acceso al sitio web del administrador
            if(rol.name=="Administrador"):user.is_staff=True#problemas cuando se es administrador
            #guardamos el usuario con lo que tenemos
            user.save()
            #llamamos a la funcion generarPassword 
            passwordGenerado = generarPassword()
            print (f"password {passwordGenerado}")
            #con el usuario creado llamamos a la función set_password que 
            # # encripta el password y lo agrega al campo password del user.
            user.set_password (passwordGenerado)
            #se actualiza el user
            user.save()
            mensaje="Usuario Agregado Correctamente" 
            retorno = {"mensaje":mensaje}
            #enviar correo al usuario
            asunto='Registro Sistema Serviteca'
            mensaje=f'Cordial saludo, <b>{user.first_name} {user.last_name}</b>, nos permitimos.\
                informarle que usted ha sido registrado en el Sistema de ServitecaOpita.\
                Nos permitimos enviarle las credenciales de Ingreso a nuestro sistema.<br>\
                <br><b>Username: </b> {user.username}\
                <br><b>Password: </b> {passwordGenerado}\
                <br><br>Lo invitamos a ingresar a nuestro sistema en la url:\
                http://gestioninventario.sena.edu.co.'
            thread = threading.Thread(target=enviarCorreo, args=(asunto,mensaje, user.email) )
            thread.start()
            return redirect("/vistaGestionarUsuarios/", retorno)
    except Error as error:
        transaction.rollback()
        mensaje= f"{error}"
    retorno = {"mensaje":mensaje}
    return render(request,"administrador/frmRegistrarUsuario.html",retorno)

def vistaGestionarClientes(request):
    if request.user.is_authenticated:
        clientes=Cliente.objects.all()
        retorno = {"clientes":clientes,"user":request.user}
        return render(request,"asistente/vistaGestionarClientes.html",retorno)
    else:
        mensaje="Debe iniciar sesión"
        return render(request, "incio.html",{"mensaje":mensaje})

def vistaRegistrarClientes(request):
    if request.user.is_authenticated:
        retorno = {"user":request.user}
        return render(request,"asistente/frmRegistrarCliente.html",retorno)
    else:
        mensaje="Debe iniciar sesión"
        return render(request, "inicio.html",{"mensaje":mensaje})

def registrarCliente(request):
    estado=False
    try:
        identificacion = request.POST["txtIdentificacion"]
        nombres = request.POST["txtNombres"]
        apellidos = request.POST["txtApellidos"]
        correo = request.POST["txtCorreo"]
        numeroC = request.POST["txtNumeroC"] 
        direccion = request.POST["txtDireccion"] 
        with transaction.atomic():
            persona=Persona(perIdentificacion=identificacion, perNombres=nombres, perApellidos=apellidos, perCorreo=correo, perNumeroCelular=numeroC)
            persona.save()  
            cliente = Cliente(cliDireccion=direccion,cliPersona=persona)
            cliente.save()
            estado=True
            mensaje="Cliente Agregado Correctamente" 
    except Error as error:
        transaction.rollback()
        mensaje= f"{error}"
    retorno = {"mensaje":mensaje,"estado":estado}
    return render(request,"asistente/frmRegistrarCliente.html",retorno)

def vistaGestionarVehiculos(request):
    if request.user.is_authenticated:
        vehiculos=Vehiculo.objects.all()
        retorno = {"vehiculos":vehiculos,"tipoVeh":tipoVehiculo,"tipoMar":tiposMarcas,"user":request.user}
        return render(request,"asistente/vistaGestionarVehiculos.html",retorno)
    else:
        mensaje="Debe iniciar sesión"
        return render(request, "inicio.html",{"mensaje":mensaje})

def vistaRegistrarVehiculos(request):
    if request.user.is_authenticated:
        retorno = {"user":request.user,"tipoVeh":tipoVehiculo,"tipoMar":tiposMarcas}
        return render(request,"asistente/frmRegistrarVehiculo.html",retorno)
    else:
        mensaje="Debe iniciar sesión"
        return render(request, "inicio.html",{"mensaje":mensaje})

def registrarVehiculo(request):
    estado=False
    try:
        placa = request.POST["txtPlaca"]
        marca = request.POST["cbMarca"]
        modelo = request.POST["txtModelo"]
        tipoV = request.POST["cbTipoV"]
        with transaction.atomic():
            vehiculo = Vehiculo(vehPlaca=placa, vehMarca=marca, vehModelo=modelo, vehTipo=tipoV)
            vehiculo.save()
            estado=True
            mensaje="Vehiculo Agregado Correctamente" 
    except Error as error:
        transaction.rollback()
        mensaje= f"{error}"
    retorno = {"mensaje":mensaje,"estado":estado}
    return render(request,"asistente/frmRegistrarVehiculo.html",retorno)

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
    if request.user.is_authenticated:
        empleados=Empleado.objects.all()
        retorno = {"empleados":empleados,"estadoEmpl":estadoEmpleados,"user":request.user}
        return render(request,"administrador/vistaGestionarEmpleados.html",retorno)
    else:
        mensaje="Debe iniciar sesión"
        return render(request, "inicio.html",{"mensaje":mensaje})

def vistaRegistrarEmpleados(request):
    if request.user.is_authenticated:
        retorno = {"user":request.user,"estadoEmpl":estadoEmpleados}
        return render(request,"administrador/frmRegistrarEmpleado.html",retorno)
    else:
        mensaje="Debe iniciar sesión"
        return render(request, "inicio.html",{"mensaje":mensaje})

def registrarEmpleado(request):
    estado=False
    try:
        identificacion = request.POST["txtIdentificacion"]
        nombres = request.POST["txtNombres"]
        apellidos = request.POST["txtApellidos"]
        correo = request.POST["txtCorreo"]
        numeroC = request.POST["txtNumeroC"] 
        cargo = request.POST["txtCargo"] 
        sueldo = request.POST["txtSueldo"] 
        estadoE = request.POST["cbEstado"] 
        with transaction.atomic():
            persona=Persona(perIdentificacion=identificacion, perNombres=nombres, perApellidos=apellidos, perCorreo=correo, perNumeroCelular=numeroC)
            persona.save()  
            cliente = Empleado(empCargo=cargo,empSueldo=sueldo,empEstado=estadoE,empPersona=persona)
            cliente.save()
            estado=True
            mensaje="Empleado Agregado Correctamente" 
    except Error as error:
        transaction.rollback()
        mensaje= f"{error}"
    retorno = {"mensaje":mensaje,"estado":estado}
    return render(request,"administrador/frmRegistrarEmpleado.html",retorno)    
    

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
    if request.user.is_authenticated:
        vehiculos=Vehiculo.objects.all()
        clientes=Cliente.objects.all()
        empleados=Empleado.objects.all()
        servicios=Servicio.objects.all()
        servicioPrestados=ServicioPrestado.objects.all()
        retorno = {"empleados":empleados,"servicios":servicios,"serviciosPrestados":servicioPrestados,"vehiculos":vehiculos,"clientes":clientes,"estadoSP":estadoServicioPrestado,"user":request.user}
        return render(request,"asistente/frmRegistrarServicioPrestado.html",retorno)
    else:
        mensaje="Debe iniciar sesión"
        return render(request, "inicio.html",{"mensaje":mensaje})
    
def registrarServicioPrestado(request):
    if request.method == 'POST':
        try:
            with transaction.atomic():
                estado = False
                idCliente = int(request.POST['cliente'])
                idVehiculo = int(request.POST['vehiculo'])
                idEmpleado = int(request.POST['empleado'])
                estado = request.POST['estado']
                fechaHora = request.POST.get('fechaHora', None)
                idServicio = int(request.POST['servicioS'])
                observaciones = request.POST['observaciones']
                cliente = Cliente.objects.get(pk=idCliente)
                vehiculo = Vehiculo.objects.get(pk=idVehiculo)
                empleado = Empleado.objects.get(pk=idEmpleado)
                servicio = Servicio.objects.get(pk=idServicio)
                servicioprestado = ServicioPrestado(serpCli=cliente, serpVehi=vehiculo, serpEmp=empleado, serpServicio=servicio,
                                                    serpEstado=estado, serpObservaciones=observaciones, serpFechaServicio=fechaHora)
                servicioprestado.save()
                
                detalleServicios = json.loads(request.POST['detalle'])
                sumaCostos = 0
                
                for detalle in detalleServicios:
                    idServicio = int(detalle['idServicio'])
                    costo = int(request.POST['costo'])  # Obtener el costo del servicio
                    
                    servicio = Servicio.objects.get(id=idServicio, costo=costo)
                    sumaCostos += costo
                    detalleServicioPrestado = DetalleServicioPrestado(detNovedad=observaciones, detMonto=sumaCostos, detServicio=servicio,
                                                                      detServicioPrestado=servicioprestado)
                    detalleServicioPrestado.save()
                
                estado = True
                mensaje = "Se ha registrado el servicio prestado correctamente"
        except Error as error:
            transaction.rollback()
            mensaje = str(error)
        
        retorno = {"estado": estado, "mensaje": mensaje}
        return JsonResponse(retorno)
        
def vistaGestionarFacturas(request):
    if request.user.is_authenticated:
        return render(request,"asistente/vistaGestionarFacturas.html")
    else:
        mensaje="Debe iniciar sesión"
        return render(request, "inicio.html",{"mensaje":mensaje})
    
def vistaGestionarSolicitudesV(request):
    if request.user.is_authenticated:
        return render(request,"tecnico/vistaGestionarSolicitudesVehiculos.html")
    else:
        mensaje="Debe iniciar sesión"
        return render(request, "inicio.html",{"mensaje":mensaje})

def vistaGestionarConsultasC(request):
    return render(request,"cliente/vistaGestionarConsultasC.html")
    
def consultarCliente(request):
    try:
        id = request.POST["txtIdentificacion"]
        if id:
            persona = Persona.objects.get(perIdentificacion=id)
            mensaje = "Cliente consultado de manera exitosa"
            estado = True
        else:
            mensaje = "Por favor, ingrese una identificación"
            persona = None
            estado = False
    except Persona.DoesNotExist:
        mensaje = "No se encontró un cliente con esa identificación"
        persona = None
        estado = False
    except Exception as error:
        mensaje = f"Problemas --> {error}"
        persona = None
        estado = False

    retorno = {
        "mensaje": mensaje,
        "persona": persona,
        "estado": estado,
    }
    return render(request, "cliente/vistaGestionarConsultasC.html", retorno)