from rest_framework import serializers
from rest_framework.authtoken.models import Token
from sistema_buap_api.models import *
from django.contrib.auth.models import User
from datetime import datetime, date

class UserSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    email = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('id','first_name','last_name', 'email')

class AdminSerializer(serializers.ModelSerializer):
    user=UserSerializer(read_only=True)
    class Meta:
        model = Administradores
        fields = '__all__'

class AlumnoSerializer(serializers.ModelSerializer):
    user=UserSerializer(read_only=True)
    class Meta:
        model = Alumnos
        fields = '__all__'

class MaestroSerializer(serializers.ModelSerializer):
    user=UserSerializer(read_only=True)
    class Meta:
        model = Maestros
        fields = '__all__'

class RFCResponsableField(serializers.Field):
    """Campo personalizado que convierte RFC a User"""
    
    def to_internal_value(self, data):
        """Convierte RFC a objeto User"""
        if not data:
            raise serializers.ValidationError("El RFC del responsable es requerido")
        
        rfc_upper = data.upper() if isinstance(data, str) else str(data).upper()
        
        maestro = Maestros.objects.filter(rfc=rfc_upper).first()
        administrador = Administradores.objects.filter(rfc=rfc_upper).first()
        
        if maestro:
            return maestro.user
        elif administrador:
            return administrador.user
        else:
            raise serializers.ValidationError(
                f"El RFC {data} no existe en la base de datos de maestros o administradores"
            )
    
    def to_representation(self, value):
        """Convierte User a ID para la respuesta"""
        return value.id if value else None

class EventoSerializer(serializers.ModelSerializer):
    responsable = RFCResponsableField(write_only=True)
    responsable_id = serializers.IntegerField(source='responsable.id', read_only=True)
    responsable_nombre = serializers.SerializerMethodField()
    
    class Meta:
        model = Eventos
        fields = '__all__'
        read_only_fields = ('id', 'creation', 'update')
    
    def get_responsable_nombre(self, obj):
        """Obtiene el nombre completo del responsable"""
        if obj.responsable:
            nombre_completo = f"{obj.responsable.first_name} {obj.responsable.last_name}".strip()
            return nombre_completo if nombre_completo else None
        return None
    
    def validate_cupo_maximo(self, value):
        """Validar que el cupo máximo sea mayor a 0"""
        if value <= 0:
            raise serializers.ValidationError("El cupo máximo debe ser mayor a 0")
        return value
    
    def validate_fecha_realizacion(self, value):
        """Validar que la fecha de realización sea válida"""
        if value < date.today():
            raise serializers.ValidationError("La fecha de realización no puede ser en el pasado")
        return value
    
    def validate_hora_fin(self, value):
        """Validar que hora_fin sea posterior a hora_inicio"""
        hora_inicio = self.initial_data.get('hora_inicio')
        if hora_inicio:
            try:
                inicio = datetime.strptime(hora_inicio, '%H:%M').time()
                fin = datetime.strptime(value, '%H:%M').time()
                if fin <= inicio:
                    raise serializers.ValidationError("La hora de fin debe ser posterior a la hora de inicio")
            except ValueError:
                raise serializers.ValidationError("Formato de hora inválido. Use HH:MM")
        return value
    
    def validate(self, data):
        """Validaciones a nivel de objeto"""
        publico_objetivo = data.get('publico_objetivo')
        programa_educativo = data.get('programa_educativo')
        
        if publico_objetivo == 'Estudiantes' and not programa_educativo:
            raise serializers.ValidationError({
                'programa_educativo': 'El programa educativo es requerido cuando el público objetivo es Estudiantes'
            })
        
        campos_requeridos = [
            'nombre_evento', 'tipo_evento', 'fecha_realizacion', 
            'hora_inicio', 'hora_fin', 'lugar', 'publico_objetivo',
            'responsable', 'descripcion_breve', 'cupo_maximo'
        ]
        
        campos_faltantes = [campo for campo in campos_requeridos if campo not in data or data[campo] is None]
        if campos_faltantes:
            raise serializers.ValidationError({
                'campos_faltantes': f'Los siguientes campos son requeridos: {", ".join(campos_faltantes)}'
            })
        
        return data