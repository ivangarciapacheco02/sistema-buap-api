from django.shortcuts import render
from django.db.models import *
from django.db import transaction
from sistema_buap_api.serializers import *
from sistema_buap_api.models import *
from rest_framework.authentication import BasicAuthentication, SessionAuthentication, TokenAuthentication
from rest_framework.generics import CreateAPIView, DestroyAPIView, UpdateAPIView
from rest_framework import permissions
from rest_framework import generics
from rest_framework import status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.reverse import reverse
from rest_framework import viewsets
from django.shortcuts import get_object_or_404
from django.core import serializers
from django.utils.html import strip_tags
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import rest_framework as filters
from datetime import datetime
from django.conf import settings
from django.template.loader import render_to_string
import string
import random
import json
import logging

logger = logging.getLogger('sistema_buap_api')

class EventosAll(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    
    def get(self, request, *args, **kwargs):
        logger.info("=== OBTENIENDO LISTA DE EVENTOS ===")
        try:
            eventos = Eventos.objects.all().order_by("fecha_realizacion", "hora_inicio")
            eventos = EventoSerializer(eventos, many=True).data
            
            if not eventos:
                logger.info("No se encontraron eventos, retornando lista vacía")
                return Response([], 200)
            
            logger.info(f"Retornando {len(eventos)} eventos")
            return Response(eventos, 200)
        except Exception as e:
            logger.error(f"Error al obtener eventos: {str(e)}", exc_info=True)
            return Response(
                {"details": "Error al obtener eventos", "message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
class EventosView(generics.CreateAPIView):
    
    def get(self, request, *args, **kwargs):
        logger.debug(f"Obteniendo evento con ID: {request.GET.get('id')}")
        try:
            evento = get_object_or_404(Eventos, id=request.GET.get("id"))
            evento = EventoSerializer(evento, many=False).data
            logger.info(f"Evento obtenido exitosamente: {evento.get('nombre_evento')}")
            return Response(evento, 200)
        except Exception as e:
            logger.error(f"Error al obtener evento: {str(e)}", exc_info=True)
            return Response(
                {"details": "Evento no encontrado", "message": str(e)},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        logger.info("=== CREACIÓN DE NUEVO EVENTO ===")
        logger.debug(f"Datos recibidos: {request.data}")
        
        try:
            campos_requeridos = [
                'nombre_evento', 'tipo_evento', 'fecha_realizacion',
                'hora_inicio', 'hora_fin', 'lugar', 'publico_objetivo',
                'responsable', 'descripcion_breve', 'cupo_maximo'
            ]
            
            campos_faltantes = [campo for campo in campos_requeridos if campo not in request.data or request.data[campo] is None or request.data[campo] == '']
            
            if campos_faltantes:
                logger.warning(f"Campos faltantes: {campos_faltantes}")
                return Response(
                    {
                        "details": "Campos requeridos faltantes",
                        "campos_faltantes": campos_faltantes,
                        "campos_requeridos": campos_requeridos
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            publico_objetivo = request.data.get('publico_objetivo')
            programa_educativo = request.data.get('programa_educativo')
            
            if publico_objetivo == 'Estudiantes' and (not programa_educativo or programa_educativo == ''):
                logger.warning("Programa educativo faltante para público objetivo Estudiantes")
                return Response(
                    {
                        "details": "El programa educativo es requerido cuando el público objetivo es Estudiantes"
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            responsable_rfc = request.data.get('responsable')
            if not responsable_rfc:
                logger.warning("RFC del responsable no proporcionado")
                return Response(
                    {
                        "details": "El RFC del responsable es requerido"
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            rfc_upper = responsable_rfc.upper()
            maestro = Maestros.objects.filter(rfc=rfc_upper).first()
            administrador = Administradores.objects.filter(rfc=rfc_upper).first()
            
            if not maestro and not administrador:
                logger.warning(f"RFC del responsable no encontrado: {responsable_rfc}")
                return Response(
                    {
                        "details": f"El RFC {responsable_rfc} no existe en la base de datos de maestros o administradores",
                        "rfc": responsable_rfc
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            serializer = EventoSerializer(data=request.data)
            if not serializer.is_valid():
                logger.warning(f"Errores de validación: {serializer.errors}")
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            evento = serializer.save()
            logger.info(f"Evento creado exitosamente con ID: {evento.id}")
            logger.info("=== FIN DE CREACIÓN DE EVENTO ===")
            
            return Response({"evento_created_id": evento.id}, status=status.HTTP_201_CREATED)
            
        except KeyError as e:
            logger.error(f"Campo faltante: {str(e)}")
            return Response(
                {
                    "details": f"Campo requerido faltante: {str(e)}",
                    "message": f"El campo '{str(e)}' es requerido pero no fue proporcionado."
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error inesperado al crear evento: {str(e)}", exc_info=True)
            return Response(
                {
                    "details": "Error interno al crear el evento",
                    "message": str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class EventosViewEdit(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    
    def put(self, request, *args, **kwargs):
        logger.info("=== ACTUALIZACIÓN DE EVENTO ===")
        logger.debug(f"Datos recibidos: {request.data}")
        
        try:
            evento_id = request.data.get("id")
            if not evento_id:
                return Response(
                    {"details": "El campo 'id' es requerido"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            evento = get_object_or_404(Eventos, id=evento_id)
            
            campos_requeridos = [
                'nombre_evento', 'tipo_evento', 'fecha_realizacion',
                'hora_inicio', 'hora_fin', 'lugar', 'publico_objetivo',
                'responsable', 'descripcion_breve', 'cupo_maximo'
            ]
            
            campos_faltantes = [campo for campo in campos_requeridos if campo not in request.data or request.data[campo] is None or request.data[campo] == '']
            
            if campos_faltantes:
                logger.warning(f"Campos faltantes: {campos_faltantes}")
                return Response(
                    {
                        "details": "Campos requeridos faltantes",
                        "campos_faltantes": campos_faltantes
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            publico_objetivo = request.data.get('publico_objetivo')
            programa_educativo = request.data.get('programa_educativo')
            
            if publico_objetivo == 'Estudiantes' and (not programa_educativo or programa_educativo == ''):
                logger.warning("Programa educativo faltante para público objetivo Estudiantes")
                return Response(
                    {
                        "details": "El programa educativo es requerido cuando el público objetivo es Estudiantes"
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            responsable_rfc = request.data.get('responsable')
            if responsable_rfc:
                rfc_upper = responsable_rfc.upper()
                maestro = Maestros.objects.filter(rfc=rfc_upper).first()
                administrador = Administradores.objects.filter(rfc=rfc_upper).first()
                
                if not maestro and not administrador:
                    logger.warning(f"RFC del responsable no encontrado: {responsable_rfc}")
                    return Response(
                        {
                            "details": f"El RFC {responsable_rfc} no existe en la base de datos de maestros o administradores",
                            "rfc": responsable_rfc
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            serializer = EventoSerializer(evento, data=request.data, partial=False)
            if not serializer.is_valid():
                logger.warning(f"Errores de validación: {serializer.errors}")
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            evento_actualizado = serializer.save()
            logger.info(f"Evento {evento_id} actualizado exitosamente")
            logger.info("=== FIN DE ACTUALIZACIÓN DE EVENTO ===")
            
            return Response(EventoSerializer(evento_actualizado).data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error al actualizar evento: {str(e)}", exc_info=True)
            return Response(
                {
                    "details": "Error al actualizar el evento",
                    "message": str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def delete(self, request, *args, **kwargs):
        logger.info("=== ELIMINACIÓN DE EVENTO ===")
        evento_id = request.GET.get("id")
        logger.debug(f"ID del evento a eliminar: {evento_id}")
        
        try:
            evento = get_object_or_404(Eventos, id=evento_id)
            evento.delete()
            logger.info(f"Evento {evento_id} eliminado exitosamente")
            logger.info("=== FIN DE ELIMINACIÓN DE EVENTO ===")
            return Response({"details": "Evento eliminado"}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error al eliminar evento: {str(e)}", exc_info=True)
            return Response(
                {"details": "Algo pasó al eliminar", "message": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

