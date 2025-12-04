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

class AlumnosAll(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    def get(self, request, *args, **kwargs):
        alumnos = Alumnos.objects.filter(user__is_active = 1).order_by("id")
        alumnos = AlumnoSerializer(alumnos, many=True).data
        if not alumnos:
            return Response([], 200)
        return Response(alumnos, 200)
    
class AlumnoView(generics.CreateAPIView):
    def get(self, request, *args, **kwargs):
        alumno = get_object_or_404(Alumnos, id = request.GET.get("id"))
        alumno = AlumnoSerializer(alumno, many=False).data

        return Response(alumno, 200)
    
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        try:
            campos_requeridos = ['rol', 'first_name', 'last_name', 'email', 'password', 
                                'id_alumno', 'fecha_nacimiento', 'curp', 'rfc', 'edad', 
                                'telefono', 'ocupacion']
            campos_faltantes = [campo for campo in campos_requeridos if campo not in request.data]
            
            user = UserSerializer(data=request.data)
            if user.is_valid():
                role = request.data['rol']
                first_name = request.data['first_name']
                last_name = request.data['last_name']
                email = request.data['email']
                password = request.data['password']
                
                existing_user = User.objects.filter(email=email).first()

                if existing_user:
                    return Response({"message":"Username "+email+", is already taken"},400)

                user = User.objects.create( username = email,
                                            email = email,
                                            first_name = first_name,
                                            last_name = last_name,
                                            is_active = 1)

                user.save()
                user.set_password(password)
                user.save()

                group, created = Group.objects.get_or_create(name=role)
                group.user_set.add(user)
                user.save()

                alumno = Alumnos.objects.create(user=user,
                                                id_alumno= request.data["id_alumno"],
                                                fecha_nacimiento= request.data["fecha_nacimiento"],
                                                curp= request.data["curp"].upper(),
                                                rfc= request.data["rfc"].upper(),
                                                edad= request.data["edad"],
                                                telefono= request.data["telefono"],
                                                ocupacion= request.data["ocupacion"])
                alumno.save()

                return Response({"alumno_created_id": alumno.id }, 201)
            else:
                return Response(user.errors, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response({"details":"Error interno al crear el alumno","message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
class AlumnosViewEdit(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    def put(self, request, *args, **kwargs):
        alumno = get_object_or_404(Alumnos, id=request.data["id"])
        alumno.id_alumno = request.data["id_alumno"]
        alumno.fecha_nacimiento = request.data["fecha_nacimiento"]
        alumno.curp = request.data["curp"].upper()
        alumno.rfc = request.data["rfc"].upper()
        alumno.edad = request.data["edad"]
        alumno.telefono = request.data["telefono"]
        alumno.ocupacion = request.data["ocupacion"]
        alumno.save()
        temp = alumno.user
        temp.first_name = request.data["first_name"]
        temp.last_name = request.data["last_name"]
        temp.save()
        user = AlumnoSerializer(alumno, many=False).data

        return Response(user,200)
    
    def delete(self, request, *args, **kwargs):
        profile = get_object_or_404(Alumnos, id=request.GET.get("id"))
        try:
            profile.user.delete()
            return Response({"details":"Alumno eliminado"},200)
        except Exception as e:
            return Response({"details":"Algo pasó al eliminar"},400)