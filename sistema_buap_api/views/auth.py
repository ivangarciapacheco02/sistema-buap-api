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
from rest_framework.exceptions import ValidationError
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
import logging

logger = logging.getLogger('sistema_buap_api')

class CustomAuthToken(ObtainAuthToken):

    def post(self, request, *args, **kwargs):
        
        try:
            serializer = self.serializer_class(data=request.data,
                                               context={'request': request})
            
            logger.debug("Validando serializer...")
            if not serializer.is_valid():
                username = request.data.get('username', 'NO PROPORCIONADO')
                from django.contrib.auth import get_user_model
                User = get_user_model()
                user_exists = User.objects.filter(username=username).exists()                
                return Response(
                    {"details": "Credenciales inválidas. Verifique su usuario y contraseña."},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            user = serializer.validated_data['user']
            if user.is_active:
                roles = user.groups.all()
                role_names = []
                for role in roles:
                    role_names.append(role.name)
               
                if not role_names:
                    return Response({"details": "Usuario sin roles asignados"}, status=status.HTTP_403_FORBIDDEN)
                
                role_names = role_names[0]

                token, created = Token.objects.get_or_create(user=user)
                
                if role_names == 'alumno':
                    alumno = Alumnos.objects.filter(user=user).first()
                    if not alumno:
                        return Response({"details": "Perfil de alumno no encontrado"}, status=status.HTTP_404_NOT_FOUND)
                    alumno = AlumnoSerializer(alumno).data
                    alumno["token"] = token.key
                    alumno["rol"] = "alumno"
                    return Response(alumno, 200)
                    
                if role_names == 'maestro':
                    maestro = Maestros.objects.filter(user=user).first()
                    if not maestro:
                        return Response({"details": "Perfil de maestro no encontrado"}, status=status.HTTP_404_NOT_FOUND)
                    maestro = MaestroSerializer(maestro).data
                    maestro["token"] = token.key
                    maestro["rol"] = "maestro"
                    logger.info(f"Login exitoso como maestro: {user.username}")
                    return Response(maestro, 200)
                    
                if role_names == 'administrador':
                    user_data = UserSerializer(user, many=False).data
                    user_data["token"] = token.key
                    user_data["rol"] = "administrador"
                    return Response(user_data, 200)
                else:
                    return Response({"details": "Forbidden", "rol": role_names}, 403)
            else:
                return Response({"details": "Usuario inactivo"}, status=status.HTTP_403_FORBIDDEN)

        except ValidationError as e:
           return Response(
                {"details": "Credenciales inválidas. Verifique su usuario y contraseña."},
                status=status.HTTP_401_UNAUTHORIZED
            )
        except Exception as e:
            return Response(
                {"details": "Error interno del servidor. Por favor, intente más tarde."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class Logout(generics.GenericAPIView):

    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        user = request.user
        
        try:
            if user.is_active:
                token = Token.objects.get(user=user)
                token.delete()
                return Response({'logout': True})
            else:
                return Response({'logout': False, 'details': 'Usuario inactivo'})
        except Token.DoesNotExist:
            return Response({'logout': False, 'details': 'Token no encontrado'})
        except Exception as e:
            return Response({'logout': False, 'details': str(e)})