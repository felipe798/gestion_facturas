
from django.contrib import admin
from django.urls import path,include

urlpatterns = [
    path('api/usuarios/', include('usuarios.urls')),
]
