from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authentication import TokenAuthentication
from django.contrib.auth.models import AbstractUser, User
from django.conf import settings

class BearerTokenAuthentication(TokenAuthentication):
    keyword = u"Bearer"

class Administradores(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False, default=None)
    clave_admin = models.CharField(max_length=255,null=True, blank=True)
    telefono = models.CharField(max_length=255, null=True, blank=True)
    rfc = models.CharField(max_length=255,null=True, blank=True)
    edad = models.IntegerField(null=True, blank=True)
    ocupacion = models.CharField(max_length=255,null=True, blank=True)
    creation = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    update = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return "Perfil del admin "+self.first_name+" "+self.last_name
    
class Alumnos(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False, default=None)
    id_alumno = models.CharField(max_length=255,null=True, blank=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    curp = models.CharField(max_length=255,null=True, blank=True)
    rfc = models.CharField(max_length=255,null=True, blank=True)
    edad = models.IntegerField(null=True, blank=True)
    telefono = models.CharField(max_length=255, null=True, blank=True)
    ocupacion = models.CharField(max_length=255,null=True, blank=True)
    creation = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    update = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return "Perfil del alumno "+self.first_name+" "+self.last_name

class Maestros(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False, default=None)
    id_trabajador = models.CharField(max_length=255,null=True, blank=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    telefono = models.CharField(max_length=255, null=True, blank=True)
    rfc = models.CharField(max_length=255,null=True, blank=True)
    cubiculo = models.CharField(max_length=255,null=True, blank=True)
    area_investigacion = models.CharField(max_length=255,null=True, blank=True)
    materias_json = models.CharField(max_length=255, null=True, blank=True)
    creation = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    update = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return "Perfil del maestro "+self.first_name+" "+self.last_name

class Eventos(models.Model):
    TIPO_EVENTO_CHOICES = [
        ('Conferencia', 'Conferencia'),
        ('Taller', 'Taller'),
        ('Seminario', 'Seminario'),
        ('Curso', 'Curso'),
        ('Congreso', 'Congreso'),
        ('Simposio', 'Simposio'),
        ('Foro', 'Foro'),
        ('Otro', 'Otro'),
    ]
    
    PUBLICO_OBJETIVO_CHOICES = [
        ('Estudiantes', 'Estudiantes'),
        ('Profesores', 'Profesores'),
        ('Público general', 'Público general'),
    ]
    
    id = models.BigAutoField(primary_key=True)
    nombre_evento = models.CharField(max_length=255, null=False, blank=False)
    tipo_evento = models.CharField(max_length=50, choices=TIPO_EVENTO_CHOICES, null=False, blank=False)
    fecha_realizacion = models.DateField(null=False, blank=False)
    hora_inicio = models.CharField(max_length=10, null=False, blank=False)
    hora_fin = models.CharField(max_length=10, null=False, blank=False)
    lugar = models.CharField(max_length=255, null=False, blank=False)
    publico_objetivo = models.CharField(max_length=50, choices=PUBLICO_OBJETIVO_CHOICES, null=False, blank=False)
    programa_educativo = models.CharField(max_length=255, null=True, blank=True)
    responsable = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False, related_name='eventos_responsable')
    descripcion_breve = models.TextField(null=False, blank=False)
    cupo_maximo = models.IntegerField(null=False, blank=False)
    creation = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    update = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return f"Evento: {self.nombre_evento} - {self.fecha_realizacion}"
    
    def clean(self):
        """Validaciones a nivel de modelo"""
        from django.core.exceptions import ValidationError
        
        if self.responsable:
            es_administrador = Administradores.objects.filter(user=self.responsable).exists()
            es_maestro = Maestros.objects.filter(user=self.responsable).exists()
            
            if not es_administrador and not es_maestro:
                raise ValidationError('El responsable debe ser un maestro o administrador')
        
        if self.publico_objetivo == 'Estudiantes' and not self.programa_educativo:
            raise ValidationError('El programa educativo es requerido cuando el público objetivo es Estudiantes')
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

