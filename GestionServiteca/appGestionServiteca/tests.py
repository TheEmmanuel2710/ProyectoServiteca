# importar la libraria y las clases para testing
from django.test import TestCase
from django.urls import reverse
from django.http import JsonResponse
from django.http import HttpResponseNotFound
from django.contrib.auth.models import User, Group
from appGestionServiteca.models import *
import random
from .views import actualizarServicioPrestado
import string
import unittest
from django.test import RequestFactory
import json
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

# -----Inicio Emmanuel-----


class RegistrarClienteTestCase(TestCase):
    def setUp(self):
        pass

    def testRegistrarCliente(self):
        data = {
            'txtIdentificacion': '1234567890',
            'txtNumeroC': '123456789',
            'txtCorreo': 'cliente1@gmail.com',
            'txtNombres': 'John',
            'txtApellidos': 'Doe',
            'txtDireccion': '123 Caguan-Centro',
        }

        response = self.client.post(
            reverse('registrarCliente'), data, HTTP_ACCEPT='application/json')

        self.assertIsInstance(response, JsonResponse)
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(str(response.content, encoding='utf8'), {
                             "mensaje": "Cliente Agregado Correctamente.", "estado": True, "user": None})

    # def testRegistrarClienteConDatosIncorrectos(self):
    #     data = {
    #         'txtIdentificacion': '',
    #         'txtNumeroC': '123456789',
    #         'txtCorreo': 'cliente1@gmail.com',
    #         'txtNombres': 'John',
    #         'txtApellidos': 'Doe',
    #         'txtDireccion': '123 Caguan-Centro',
    #     }

    #     response = self.client.post(
    #         reverse('registrarCliente'), data, HTTP_ACCEPT='application/json')

    #     self.assertIsInstance(response, JsonResponse)
    #     self.assertEqual(response.status_code, 400)
    #     self.assertJSONEqual(str(response.content, encoding='utf8'), {
    #                          "mensaje": "Error al registrar cliente.", "estado": False, "user": None})

    def tearDown(self):
        pass


class RegistrarVehiculoTestCase(TestCase):
    def setUp(self):
        pass

    def testRegistrarVehiculo(self):
        data = {
            'txtPlaca': 'frm234',
            'cbMarca': 'Toyota',
            'cbTipoV': 'Gasolina',
            'txtModelo': '2034'
        }

        response = self.client.post(
            reverse('registrarVehiculo'), data, HTTP_ACCEPT='application/json')

        self.assertIsInstance(response, JsonResponse)
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(str(response.content, encoding='utf8'), {
                             "mensaje": "Vehículo Agregado Correctamente.", "estado": True, "user": None})

    # def testRegistrarVehiculoConDatosIncorrectos(self):
    #     data = {
    #         'txtPlaca': '',
    #         'cbMarca': 'Toyota',
    #         'cbTipoV': 'Gasolina',
    #         'txtModelo': '2034'
    #     }

    #     response = self.client.post(
    #         reverse('registrarVehiculo'), data, HTTP_ACCEPT='application/json')

    #     self.assertIsInstance(response, JsonResponse)
    #     self.assertEqual(response.status_code, 400)
    #     self.assertJSONEqual(str(response.content, encoding='utf8'), {
    #                          "mensaje": "Error al registrar vehículo.", "estado": False, "user": None})

    def tearDown(self):
        pass


class RegistrarServicioPrestadoTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword'
        )

        self.persona = Persona.objects.create(
            perIdentificacion='1234567890',
            perNombres='Nombre1',
            perApellidos='Apellido1',
            perCorreo='thepepe@gmail.com',
            perNumeroCelular='1234567890'
        )

        self.cliente = Cliente.objects.create(
            cliDireccion='kra 9 #4 sur',
            cliPersona=self.persona
        )
        self.vehiculo = Vehiculo.objects.create(
            vehPlaca='ABC123',
            vehMarca='Toyota',
            vehModelo=2020,
            vehTipo='Gasolina'
        )
        self.servicio = Servicio.objects.create(
            serNombre='Servicio1',
            serCosto=100
        )
        self.empleado = Empleado.objects.create(
            empCargo='Técnico',
            empSueldo=2000,
            empEstado='Activo',
            empPersona=self.persona
        )

    def testRegistrarServicioPrestado(self):
        data = {
            'idCliente': self.cliente.id,
            'idVehiculo': self.vehiculo.id,
            'observaciones': 'Observaciones de prueba',
            'detalle': json.dumps([
                {
                    'idServicio': self.servicio.id,
                    'idEmpleado': self.empleado.id
                }
            ])
        }

        self.client.login(username='testuser', password='testpassword')

        response = self.client.post(reverse('registrarServicioPrestado'), data)

        self.assertEqual(response.status_code, 200)

        self.assertTrue(ServicioPrestado.objects.filter(
            serpCli=self.cliente).exists())

        self.assertTrue(Factura.objects.filter(
            facServicioPrestado__serpCli=self.cliente).exists())

        expected_response = {
            'estado': True,
            'mensaje': 'Se ha registrado el servicio prestado y generado la factura correctamente.'
        }

        self.assertJSONEqual(
            str(response.content, encoding='utf8'), expected_response)

    def testRegistrarServicioPrestadoConError(self):
        data = {
            'idCliente': 999,
            'idVehiculo': self.vehiculo.id,
            'observaciones': 'Observaciones de prueba',
            'detalle': json.dumps([
                {
                    'idServicio': self.servicio.id,
                    'idEmpleado': self.empleado.id
                }
            ])
        }

        self.client.login(username='testuser', password='testpassword')

        response = self.client.post(reverse('registrarServicioPrestado'), data)

        self.assertFalse(ServicioPrestado.objects.filter(
            serpCli=self.cliente).exists())

        self.assertFalse(Factura.objects.filter(
            facServicioPrestado__serpCli=self.cliente).exists())

        expected_response = {
            'estado': False,
            'mensaje': 'El cliente no existe.'
        }

        self.assertJSONEqual(
            str(response.content, encoding='utf8'), expected_response)

    def tearDown(self):
        pass


class ActualizarClienteTestCase(TestCase):
    def setUp(self):
        self.persona = Persona.objects.create(
            perIdentificacion='1234567890',
            perNombres='Nombre1',
            perApellidos='Apellido1',
            perCorreo='per1@hotmail.com',
            perNumeroCelular='1234567890'
        )
        self.cliente = Cliente.objects.create(
            cliDireccion='NEIVA',
            cliPersona=self.persona
        )

    def testActualizarCliente(self):
        self.client.login(username='testuser', password='testpassword')
        new_identificacion = '0987654321'
        new_nombres = 'Nombre Nuevo'
        new_apellidos = 'Apellido Nuevo '
        new_correo = 'CorreoNuevo@yahoo.com'
        new_direccion = 'Dirección Nueva '
        new_numero = '9876543210'

        response = self.client.post(reverse('actualizarCliente'), {
            'idCliente': self.cliente.id,
            'txtIdentificacion': new_identificacion,
            'txtNombres': new_nombres,
            'txtApellidos': new_apellidos,
            'txtCorreo': new_correo,
            'txtDireccion': new_direccion,
            'txtNumeroC': new_numero
        })

        self.assertEqual(response.status_code, 200)

        self.cliente.refresh_from_db()
        self.persona.refresh_from_db()

        self.assertEqual(self.persona.perIdentificacion,
                         new_identificacion)
        self.assertEqual(self.persona.perNombres, new_nombres)
        self.assertEqual(self.persona.perApellidos, new_apellidos)
        self.assertEqual(self.persona.perCorreo, new_correo)
        self.assertEqual(self.cliente.cliDireccion, new_direccion)
        self.assertEqual(self.persona.perNumeroCelular, new_numero)

        self.assertContains(response, 'Cliente actualizado correctamente.')

    def testActualizarClienteNoExistente(self):
        self.client.login(username='testuser', password='testpassword')

        response = self.client.post(reverse('actualizarCliente'), {
            'idCliente': 9999,
            'txtIdentificacion': 'NuevoIdentificacion',
            'txtNombres': 'NuevoNombre',
            'txtApellidos': 'NuevoApellido',
            'txtCorreo': 'nuevo@example.com',
            'txtDireccion': 'NuevaDireccion',
            'txtNumeroC': '9876543210'
        })

        self.assertEqual(response.status_code, 200)

        self.assertContains(response, 'El cliente no existe.')

    def tearDown(self):
        pass


class ActualizarServicioPrestadoTestCase(unittest.TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword'
        )
        self.cliente = Cliente.objects.create(
            cliDireccion='Dirección de prueba',
            cliPersona=Persona.objects.create(
                perIdentificacion='1234567890',
                perNombres='Nombre del Cliente',
                perApellidos='Apellido del Cliente',
                perCorreo='cliente@example.com',
                perNumeroCelular='1234567890'
            )
        )

        # Crea un vehículo de ejemplo
        self.vehiculo = Vehiculo.objects.create(
            vehPlaca='ABC123',
            vehMarca='Toyota',
            vehModelo=2022,
            vehTipo='Gasolina'
        )

        self.servicioPrestado = ServicioPrestado.objects.create(
            serpCli=self.cliente,
            serpVehi=self.vehiculo,
            serpEstado='Solicitado',
            serpObservaciones='Ninguna observación',
        )

    def test_actualizar_servicio_prestado(self):
        request = self.factory.post('actualizarServicioPrestado', {
            'idServicioP': self.servicioPrestado.pk,
            'cbEstado': 'Terminado'
        })
        request.user = self.user

        response = actualizarServicioPrestado(request)

        self.assertEqual(response.status_code, 200)
        servicio_actualizado = ServicioPrestado.objects.get(
            pk=self.servicioPrestado.pk)
        self.assertEqual(servicio_actualizado.serpEstado, 'Terminado')

    def tearDown(self):
        self.servicioPrestado.delete()
        self.vehiculo.delete()
        self.user.delete()


if __name__ == '__main__':
    unittest.main()

# -----Fin Emmanuel-----


# -----Inicio Alex-----
# class TestGenerarPassword(TestCase):
#     def test_generar_password(self):
#         # Llama a la función generarPassword para obtener un password
#         generated_password = views.generarPassword()

#         # Verifica que la longitud del password generado sea 10
#         self.assertEqual(len(generated_password), 10)

#         # Verifica que el password contenga al menos una letra mayúscula
#         self.assertTrue(any(char.isupper() for char in generated_password))

#         # Verifica que el password contenga al menos una letra minúscula
#         self.assertTrue(any(char.islower() for char in generated_password))

#         # Verifica que el password contenga al menos un dígito
#         self.assertTrue(any(char.isdigit() for char in generated_password))

#         # Verifica que el password contenga al menos un carácter especial
#         self.assertTrue(
#             any(char in string.punctuation for char in generated_password))
# # Función para generar un password
# def generarPassword():
#     """
#     Genera un password de longitud de 10 que incluye letras mayúsculas
#     y minúsculas, dígitos y caracteres especiales.
#     Returns:
#         str: retorna un password
#     """
#     longitud = 10

#     caracteres = string.ascii_lowercase + \
#         string.ascii_uppercase + string.digits + string.punctuation
#     password = ''

#     for i in range(longitud):
#         password += ''.join(random.choice(caracteres))
#     return password


# class Error404TestCase(TestCase):
#     def test_error_404_page(self):
#         # Intenta acceder a una URL que no existe en tu aplicación
#         response = self.client.get('jkakjakjasxj/kjsdjkasdk')

#         # Verifica que la respuesta tenga el código de estado 404 (no encontrado)
#         self.assertEqual(response.status_code, 404)

#         # Verifica que el contenido de la respuesta contenga ciertas palabras o elementos específicos
#         self.assertContains(response, 'Página no encontrada', status_code=404)

#         # También puedes verificar que el template utilizado sea el correcto
#         self.assertTemplateUsed(response, '404.html')


# class LoginTestCase(TestCase):
#     def setUp(self):
#         # Crear un usuario de ejemplo para las pruebas
#         self.user = User.objects.create_user(
#             username="usuario_prueba",
#             password="contraseña_prueba"
#         )

#         # Crear grupos de ejemplo
#         self.admin_group = Group.objects.create(name="Administrador")
#         self.asistente_group = Group.objects.create(name="Asistente")
#         self.tecnico_group = Group.objects.create(name="Tecnico")

#     def test_login_exitoso(self):
#         # Configura una sesión de cliente y realiza una solicitud POST para iniciar sesión
#         response = self.client.post(reverse('login'), {
#             'txtUsername': 'usuario_prueba',
#             'txtPassword': 'contraseña_prueba',
#             # Debes establecer esto como válido para las pruebas
#             'g-recaptcha-response': 'valid_recaptcha_response'
#         })

#         # Verifica que el usuario esté autenticado y redirigido correctamente según su grupo
#         self.assertTrue(response.wsgi_request.user.is_authenticated)
#         # Ajusta esto según tu lógica de redirección
#         self.assertRedirects(response, '/inicioAdministrador/')

#     def test_login_invalido(self):
#         # Configura una sesión de cliente y realiza una solicitud POST con credenciales incorrectas
#         response = self.client.post(reverse('login'), {
#             'txtUsername': 'usuario_prueba',
#             'txtPassword': 'contraseña_incorrecta',
#             # Debes establecer esto como válido para las pruebas
#             'g-recaptcha-response': 'valid_recaptcha_response'
#         })

#         # Verifica que el usuario no esté autenticado y que se muestre un mensaje de error
#         self.assertFalse(response.wsgi_request.user.is_authenticated)
#         self.assertContains(response, "Usuario o Contraseña Incorrectas.")

#     def test_login_sin_recaptcha(self):
#         # Configura una sesión de cliente y realiza una solicitud POST sin un reCAPTCHA válido
#         response = self.client.post(reverse('login'), {
#             'txtUsername': 'usuario_prueba',
#             'txtPassword': 'contraseña_prueba',
#             'g-recaptcha-response': ''  # Deja esto en blanco para simular un reCAPTCHA no válido
#         })

#         # Verifica que el usuario no esté autenticado y que se muestre un mensaje de error
#         self.assertFalse(response.wsgi_request.user.is_authenticated)
#         self.assertContains(response, "Debe validar primero el recaptcha.")

#     def setUp(self):
#         # Crea un vehículo de ejemplo en la base de datos
#         self.vehiculo = Vehiculo.objects.create(
#             vehPlaca="ABC123",
#             vehMarca="Ford",
#             vehModelo="2022",
#             vehTipo="Sedán"
#         )

#     def test_consultar_vehiculo_existente(self):
#         # Obtiene la URL para consultar el vehículo creado en el setUp
#         url = reverse('consultarVehiculo', args=[self.vehiculo.id])

#         # Realiza una solicitud GET a la URL
#         response = self.client.get(url)

#         # Verifica que la respuesta tenga el código de estado 200 (éxito)
#         self.assertEqual(response.status_code, 200)

#         # Verifica que la respuesta sea un JSON con los datos del vehículo
#         expected_data = {
#             "vehiculo": {
#                 "id": self.vehiculo.id,
#                 "vehPlaca": "ABC123",
#                 "vehMarca": "Ford",
#                 "vehModelo": "2022",
#                 "vehTipo": "Sedán"
#             }
#         }
#         self.assertEqual(response.json(), expected_data)

#     def test_consultar_vehiculo_no_existente(self):
#         # Intenta consultar un vehículo que no existe en la base de datos
#         url = reverse('consultarVehiculo', args=[999])  # ID no existente

#         # Realiza una solicitud GET a la URL
#         response = self.client.get(url)

#         # Verifica que la respuesta tenga el código de estado 404 (no encontrado)
#         self.assertEqual(response.status_code, 404)

#         # Verifica que la respuesta contenga un mensaje de error
#         expected_error = {"error": "Vehiculo no encontrado."}
#         self.assertEqual(response.json(), expected_error)


#     class LoginTestCase(TestCase):
#         def setUp(self):
#             # Crear un usuario de ejemplo para las pruebas
#             self.user = User.objects.create_user(
#                 username="usuario_prueba",
#                 password="contraseña_prueba"
#             )

#             # Crear grupos de ejemplo
#             self.admin_group = Group.objects.create(name="Administrador")
#             self.asistente_group = Group.objects.create(name="Asistente")
#             self.tecnico_group = Group.objects.create(name="Tecnico")

#     def test_login_exitoso(self):
#         # Configura una sesión de cliente y realiza una solicitud POST para iniciar sesión
#         response = self.client.post(reverse('login'), {
#             'txtUsername': 'usuario_prueba',
#             'txtPassword': 'contraseña_prueba',
#             # Debes establecer esto como válido para las pruebas
#             'g-recaptcha-response': 'valid_recaptcha_response'
#         })

#         # Verifica que el usuario esté autenticado y redirigido correctamente según su grupo
#         self.assertTrue(response.wsgi_request.user.is_authenticated)
#         # Ajusta esto según tu lógica de redirección
#         self.assertRedirects(response, '/inicioAdministrador/')

#     def test_login_invalido(self):
#         # Configura una sesión de cliente y realiza una solicitud POST con credenciales incorrectas
#         response = self.client.post(reverse('login'), {
#             'txtUsername': 'usuario_prueba',
#             'txtPassword': 'contraseña_incorrecta',
#             # Debes establecer esto como válido para las pruebas
#             'g-recaptcha-response': 'valid_recaptcha_response'
#         })

#         # Verifica que el usuario no esté autenticado y que se muestre un mensaje de error
#         self.assertFalse(response.wsgi_request.user.is_authenticated)
#         self.assertContains(response, "Usuario o Contraseña Incorrectas.")

#     def test_login_sin_recaptcha(self):
#         # Configura una sesión de cliente y realiza una solicitud POST sin un reCAPTCHA válido
#         response = self.client.post(reverse('login'), {
#             'txtUsername': 'usuario_prueba',
#             'txtPassword': 'contraseña_prueba',
#             'g-recaptcha-response': ''  # Deja esto en blanco para simular un reCAPTCHA no válido
#         })

#         # Verifica que el usuario no esté autenticado y que se muestre un mensaje de error
#         self.assertFalse(response.wsgi_request.user.is_authenticated)
#         self.assertContains(response, "Debe validar primero el recaptcha.")
