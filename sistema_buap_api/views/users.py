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

class AdminAll(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    def get(self, request, *args, **kwargs):
        admin = Administradores.objects.filter(user__is_active = 1).order_by("id")
        lista = AdminSerializer(admin, many=True).data
        
        return Response(lista, 200)

class AdminView(generics.CreateAPIView):
    def get(self, request, *args, **kwargs):
        admin = get_object_or_404(Administradores, id = request.GET.get("id"))
        admin = AdminSerializer(admin, many=False).data

        return Response(admin, 200)
    
    @transaction.atomic
    def post(self, request, *args, **kwargs):

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

            admin = Administradores.objects.create(user=user,
                                            clave_admin= request.data["clave_admin"],
                                            telefono= request.data["telefono"],
                                            rfc= request.data["rfc"].upper(),
                                            edad= request.data["edad"],
                                            ocupacion= request.data["ocupacion"])
            admin.save()

            return Response({"admin_created_id": admin.id }, 201)

        return Response(user.errors, status=status.HTTP_400_BAD_REQUEST)
    
class AdminsViewEdit(generics.CreateAPIView):
        permission_classes = (permissions.IsAuthenticated,)
        def get(self, request, *args, **kwargs):
            admin = Administradores.objects.filter(user__is_active = 1).order_by("id")
            lista_admins = AdminSerializer(admin, many=True).data
            total_admins = len(lista_admins)

            maestros = Maestros.objects.filter(user__is_active = 1).order_by("id")
            lista_maestros = MaestroSerializer(maestros, many=True).data
            total_maestros = 0
            if lista_maestros:
                for maestro in lista_maestros:
                    maestro["materias_json"] = json.loads(maestro["materias_json"])
                    total_maestros = len(lista_maestros)

            alumnos = Alumnos.objects.filter(user__is_active = 1).order_by("id")
            lista_alumnos = AlumnoSerializer(alumnos, many=True).data
            total_alumnos = len(lista_alumnos)

            return Response({'admins': total_admins, 'maestros': total_maestros, 'alumnos': total_alumnos }, 200)
    
        def put(self, request, *args, **kwargs):
            admin = get_object_or_404(Administradores, id=request.data["id"])
            admin.clave_admin = request.data["clave_admin"]
            admin.telefono = request.data["telefono"]
            admin.rfc = request.data["rfc"].upper()
            admin.edad = request.data["edad"]
            admin.ocupacion = request.data["ocupacion"]
            admin.save()
            temp = admin.user
            temp.first_name = request.data["first_name"]
            temp.last_name = request.data["last_name"]
            temp.save()
            user = AdminSerializer(admin, many=False).data

            return Response(user,200)
    
        def delete(self, request, *args, **kwargs):
            admin = get_object_or_404(Administradores, id=request.GET.get("id"))
            try:
                admin.user.delete()
                return Response({"details":"Administrador eliminado"},200)
            except Exception as e:
                return Response({"details":"Algo pasó al eliminar"},400)