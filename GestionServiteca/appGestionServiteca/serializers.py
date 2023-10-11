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
            'perIdentificacion': persona.perIdentificacion,
            'perNombres': persona.perNombres,
            'perApellidos': persona.perApellidos,
            'perCorreo': persona.perCorreo,
            'perNumeroCelular': persona.perNumeroCelular,
        }

    class Meta:
        model = Cliente
        fields = ('id', 'cliDireccion', 'cliPersona', 'cliPersona_info')


class ServicioPrestadoSerializer(serializers.ModelSerializer):
    serpCli_info = ClienteSerializer(source='serpCli', read_only=True)
    serpVehi_placa = serializers.CharField(
        source='serpVehi.vehPlaca', read_only=True)

    class Meta:
        model = ServicioPrestado
        fields = ('id', 'serpCli_info', 'serpVehi_placa',
                  'serpEstado', 'serpObservaciones', 'serpFechaServicio')


class DetalleServicioPrestadoSerializer(serializers.ModelSerializer):
    detServicio = serializers.CharField(
        source='detServicio.serNombre', read_only=True)
    detEmpleado = serializers.CharField(
        source='detEmpleado.empPersona.perNombres', read_only=True)
    detObservaciones = serializers.SerializerMethodField()

    def get_detObservaciones(self, obj):
        if obj.detObservaciones is not None:
            return obj.detObservaciones
        else:
            return "No hay observaciones hechas por el técnico todavía."

    class Meta:
        model = DetalleServicioPrestado
        fields = ('id', 'detServicio', 'detEmpleado', 'detEstadoServicio',
                  'detObservaciones', 'detServicioPrestado')
