from rest_framework import serializers
from .models import Usuario
from .models import Cliente, Proveedor, Factura

# Serializador para el modelo Usuario
class UsuarioSerializer(serializers.ModelSerializer):
    # Definimos el campo 'password' para que sea solo de escritura (write_only=True) y no sea obligatorio
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Usuario  # Define el modelo sobre el que este serializador actuará
        fields = ['id', 'email', 'nombre', 'rol', 'password', 'fecha_creacion']  # Campos que serán incluidos en la serialización

    # Método sobrescrito para crear un nuevo usuario
    def create(self, validated_data):
        """
        Sobrescribe el método de creación para manejar contraseñas correctamente.
        """
        # Extrae la contraseña del diccionario de datos validados
        password = validated_data.pop('password', None)
        usuario = Usuario(**validated_data)
        if password:
            usuario.set_password(password)  
        usuario.save()  # Guarda el nuevo usuario
        return usuario  # Devuelve el usuario creado

    # Método sobrescrito para actualizar un usuario existente
    def update(self, instance, validated_data):
        """
        Sobrescribe el método de actualización para manejar contraseñas y otros campos.
        """
        # Extrae la contraseña de los datos validados
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)  # Actualiza la contraseña encriptada
        instance.save()  # Guarda los cambios en el usuario
        return instance  # Devuelve el usuario actualizado

# Serializador para el modelo Cliente
class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente  # Define el modelo sobre el que este serializador actuará
        fields = ['id', 'nombre', 'email']  # Campos que serán incluidos en la serialización

# Serializador para el modelo Proveedor
class ProveedorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proveedor  # Define el modelo sobre el que este serializador actuará
        fields = ['id', 'nombre', 'email']  # Campos que serán incluidos en la serialización

#--------------------------------------------------------------------


class FacturaSerializer(serializers.ModelSerializer):
    cliente_nombre = serializers.CharField(source='cliente.nombre', read_only=True)
    proveedor_nombre = serializers.CharField(source='proveedor.nombre', read_only=True)  # Agregado para el nombre del proveedor

    class Meta:
        model = Factura
        fields = [
            'id', 'numero_factura', 'proveedor', 'proveedor_nombre',  # Agregado proveedor_nombre
            'cliente', 'cliente_nombre',
            'fecha_emision', 'fecha_vencimiento', 'monto_total', 'estado', 'penalizacion'
        ]
