import csv
from io import BytesIO
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from .models import Usuario, Cliente, Proveedor, Factura
from .serializers import UsuarioSerializer, ClienteSerializer, ProveedorSerializer, FacturaSerializer
from .models import Factura, Proveedor
from io import TextIOWrapper
from .models import Proveedor, Factura
from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum, Count
from datetime import date

#----------- PARTE DE JHON----------------------
class RegistroView(APIView):
    # Método para manejar solicitudes POST
    def post(self, request):
        data = request.data  # Obtiene los datos enviados en el cuerpo de la solicitud
        # Verifica que el rol especificado sea "Administrador"
        if data.get('rol') != 'Administrador':
            # Retorna un error si el rol no es "Administrador"
            return Response({'error': 'Solo se pueden registrar administradores'}, status=status.HTTP_403_FORBIDDEN)
        # Instancia el serializador con los datos recibidos
        serializer = UsuarioSerializer(data=data)
        # Valida los datos del serializador
        if serializer.is_valid():
            # Si los datos son válidos, crea un nuevo usuario con el método create_user
            Usuario.objects.create_user(
                email=data['email'],       # Asigna el email del usuario
                nombre=data['nombre'],     # Asigna el nombre del usuario
                password=data['password'], # Asigna la contraseña
                rol=data['rol']            # Asigna el rol
            )
            # Retorna una respuesta de éxito si el usuario fue creado correctamente
            return Response({'mensaje': 'Usuario creado exitosamente'}, status=status.HTTP_201_CREATED)

        # Si los datos no son válidos, retorna los errores de validación
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
# Vista para el inicio de sesión de usuarios
class LoginView(APIView):
    def post(self, request):
        # Obtiene las credenciales de inicio de sesión del cuerpo de la solicitud
        email = request.data.get('email')
        password = request.data.get('password')
        
        # Autentica al usuario con las credenciales proporcionadas
        user = authenticate(email=email, password=password)
        if user:
            # Genera tokens de acceso y actualización para el usuario autenticado
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),                # Token de actualización
                'access': str(refresh.access_token),    # Token de acceso
                'rol': user.rol                         # Rol del usuario
            })
        
        # Si las credenciales son incorrectas, retorna un error 401
        return Response({'error': 'Credenciales incorrectas'}, status=status.HTTP_401_UNAUTHORIZED)


# Vista CRUD para la gestión de usuarios -------------------------------
class UsuarioCRUDView(APIView):
    # Restringe el acceso a usuarios autenticados
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Verifica si el usuario tiene el rol de "Administrador"
        if request.user.rol != 'Administrador':
            return Response({'error': 'No autorizado'}, status=status.HTTP_403_FORBIDDEN)
        
        # Obtiene todos los usuarios y los serializa para enviarlos en la respuesta
        usuarios = Usuario.objects.all()
        serializer = UsuarioSerializer(usuarios, many=True)
        return Response(serializer.data)

    def post(self, request):
        # Verifica si el usuario tiene el rol de "Administrador"
        if request.user.rol != 'Administrador':
            return Response({'error': 'No autorizado'}, status=status.HTTP_403_FORBIDDEN)
        
        # Serializa los datos enviados en la solicitud
        serializer = UsuarioSerializer(data=request.data)
        if serializer.is_valid():
            # Si los datos son válidos, crea un nuevo usuario
            Usuario.objects.create_user(
                email=request.data['email'],               # Email del usuario
                nombre=request.data['nombre'],             # Nombre del usuario
                password=request.data['password'],         # Contraseña del usuario
                rol=request.data.get('rol', 'Contador')    # Rol con valor por defecto "Contador"
            )
            return Response({'mensaje': 'Usuario creado exitosamente'}, status=status.HTTP_201_CREATED)
        
        # Si los datos no son válidos, retorna errores de validación
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        # Verifica si el usuario tiene el rol de "Administrador"
        if request.user.rol != 'Administrador':
            return Response({'error': 'No autorizado'}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            # Busca el usuario por su ID (pk)
            usuario = Usuario.objects.get(pk=pk)
        except Usuario.DoesNotExist:
            # Retorna un error si el usuario no existe
            return Response({'error': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        
        # Serializa los datos y valida la información para actualizar al usuario
        serializer = UsuarioSerializer(usuario, data=request.data)
        if serializer.is_valid():
            serializer.save()  # Guarda los cambios en el usuario
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        # Si los datos no son válidos, retorna errores de validación
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        # Verifica si el usuario tiene el rol de "Administrador"
        if request.user.rol != 'Administrador':
            return Response({'error': 'No autorizado'}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            # Busca el usuario por su ID (pk)
            usuario = Usuario.objects.get(pk=pk)
            usuario.delete()  # Elimina al usuario
            return Response({'mensaje': 'Usuario eliminado correctamente'}, status=status.HTTP_200_OK)
        except Usuario.DoesNotExist:
            # Retorna un error si el usuario no existe
            return Response({'error': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        
#-----------------------------------------------------------------------
# Clase para manejar las operaciones relacionadas con Clientes
class ClienteView(APIView):
    permission_classes = [IsAuthenticated]

    # Maneja solicitudes GET para obtener todos los clientes
    def get(self, request):
        clientes = Cliente.objects.all()
        serializer = ClienteSerializer(clientes, many=True)
        return Response(serializer.data)

    # Maneja solicitudes POST para crear un nuevo cliente
    def post(self, request):
        serializer = ClienteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Clase para manejar las operaciones relacionadas con Proveedores
class ProveedorView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        proveedores = Proveedor.objects.all()
        serializer = ProveedorSerializer(proveedores, many=True)
        return Response(serializer.data)

    # Maneja solicitudes POST para crear un nuevo proveedor
    def post(self, request):
        serializer = ProveedorSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#--------------------------ASTA AQUI -----------------------------------------------------
