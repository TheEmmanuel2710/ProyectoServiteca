from rest_framework import serializers
from appGestionServiteca.models import Cliente, Persona


class PersonaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Persona
        fields = ('id', 'perIdentificacion', 'perNombres',
                  'perApellidos', 'perCorreo', 'perNumeroCelular')


class ClienteSerializer(serializers.ModelSerializer):
    cliDireccion = PersonaSerializer

    class Meta:
        model = Cliente
        fields = ('id', 'cliDireccion', 'cliPersona')
