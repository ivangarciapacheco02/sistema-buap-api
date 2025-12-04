"""point_experts_api URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from sistema_buap_api.views import bootstrap
from sistema_buap_api.views import users
from sistema_buap_api.views import alumnos
from sistema_buap_api.views import maestros
from sistema_buap_api.views import auth
from sistema_buap_api.views import eventos

urlpatterns = [
        path('bootstrap/version', bootstrap.VersionView.as_view()),
        path('admin/', users.AdminView.as_view()),
        path('lista-admins/', users.AdminAll.as_view()),
        path('admins-edit/', users.AdminsViewEdit.as_view()),
        path('alumnos/', alumnos.AlumnoView.as_view()),
        path('lista-alumnos/', alumnos.AlumnosAll.as_view()),
        path('alumnos-edit/', alumnos.AlumnosViewEdit.as_view()),
        path('maestros/', maestros.MaestroView.as_view()),
        path('lista-maestros/', maestros.MaestrosAll.as_view()),
        path('maestros-edit/', maestros.MaestrosViewEdit.as_view()),
        path('nombre-maestros/', maestros.MaestrosNames.as_view()),
        path('eventos/', eventos.EventosView.as_view()),
        path('lista-eventos/', eventos.EventosAll.as_view()),
        path('eventos-edit/', eventos.EventosViewEdit.as_view()),
        path('login/', auth.CustomAuthToken.as_view()),
        path('logout/', auth.Logout.as_view())
]