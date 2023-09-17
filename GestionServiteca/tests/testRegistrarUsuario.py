from django.test import TestCase
from django.urls import reverse
from .models import Persona, Cliente

class RegistrarClienteTestCase(TestCase):

    def test_registro_cliente_exitoso(self):
        response = self.client.post(reverse('registrar_cliente'), {
            'txtIdentificacion': '123456789',
            'txtNumeroC': '5555555555',
            'txtCorreo': 'nuevo_cliente@example.com',
            'txtNombres': 'Nuevo',
            'txtApellidos': 'Cliente',
            'txtDireccion': '123 Calle Principal'
        })

        
        self.assertRedirects(response, reverse('pagina_de_exito'))

    
        self.assertTrue(Persona.objects.filter(perIdentificacion='123456789').exists())
        self.assertTrue(Cliente.objects.filter(cliDireccion='123 Calle Principal').exists())

    def test_registro_cliente_con_identificacion_existente(self):
        # Crea una persona con la misma identificación antes de realizar el registro
        Persona.objects.create(
            perIdentificacion='123456789',
            perNombres='Cliente Existente',
            perApellidos='Existente',
            perCorreo='cliente_existente@example.com',
            perNumeroCelular='5555555555'
        )

        # Simula una solicitud POST para registrar un cliente con la misma identificación
        response = self.client.post(reverse('registrar_cliente'), {
            'txtIdentificacion': '123456789',
            'txtNumeroC': '5555555555',
            'txtCorreo': 'nuevo_cliente@example.com',
            'txtNombres': 'Nuevo',
            'txtApellidos': 'Cliente',
            'txtDireccion': '123 Calle Principal'
        })

        
        self.assertContains(response, 'Error : La Identificación ya está registrada en otro cliente.')

    
