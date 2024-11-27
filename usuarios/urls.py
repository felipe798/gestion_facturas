from django.urls import path
from .views import (
    RegistroView,
    LoginView,
    UsuarioCRUDView,
    ClienteView,
    ProveedorView,#-------JK
  
)
urlpatterns = [
    # Registro y autenticación
    path('registro/', RegistroView.as_view(), name='registro'),
    path('login/', LoginView.as_view(), name='login'),

    # Gestión de usuarios
    path('', UsuarioCRUDView.as_view(), name='usuarios_crud'),
    path('<int:pk>/', UsuarioCRUDView.as_view(), name='usuario_crud_detail'),
    # Clientes y Proveedores
    path('clientes/', ClienteView.as_view(), name='clientes'),
    path('proveedores/', ProveedorView.as_view(), name='proveedores'),


]