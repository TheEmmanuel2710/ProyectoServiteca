from rest_framework import serializers
from appGestionServiteca.models import Cliente, Persona, ServicioPrestado, DetalleServicioPrestado


class PersonaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Persona
        fields = ('id', 'perIdentificacion', 'perNombres',
                  'perApellidos', 'perCorreo', 'perNumeroCelular')


class ClienteSerializer(serializers.ModelSerializer):
    cliPersona_info = serializers.SerializerMethodField()

    def get_cliPersona_info(self, obj):
        persona = obj.cliPersona
        return {
            'perNombres': persona.perNombres,
            'perApellidos': persona.perApellidos,
            'perCorreo': persona.perCorreo,
            'perNumeroCelular': persona.perNumeroCelular,
        }

    class Meta:
        model = Cliente
        fields = ('id', 'cliDireccion', 'cliPersona', 'cliPersona_info')


class ServicioPrestadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServicioPrestado
        fields = ('id', 'serpCli', 'serpVehi', 'serpEstado',
                  'serpObservaciones', 'serpFechaServicio')


class DetalleServicioPrestadoSerializer(serializers.ModelSerializer):
    detServicio = serializers.CharField(
        source='detServicio.serNombre', read_only=True)
    detEmpleado = serializers.CharField(
        source='detEmpleado.empPersona.perNombres', read_only=True)

    class Meta:
        model = DetalleServicioPrestado
        fields = ('id', 'detServicio', 'detEmpleado')
