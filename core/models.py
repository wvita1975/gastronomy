from django.contrib.auth.models import AbstractUser
from django.db import models

class Usuario(AbstractUser):
    ROLES = [
        ('admin', 'Administrador'),
        ('mesonero', 'Mesonero'),
        ('cocinero', 'Cocinero'),
        ('cajero', 'Cajero'),
        ('supervisor', 'Supervisor'),
    ]
    rol = models.CharField(max_length=20, choices=ROLES)
    telefono = models.CharField(max_length=20, blank=True)
    documento_identidad = models.CharField(max_length=20, blank=True)

    codigo_usuario = models.CharField(
        max_length=4,
        unique=True,
        editable=False,
        blank=True
    )

    def save(self, *args, **kwargs):
        if not self.codigo_usuario:
            # Buscar el último código generado
            ultimo_codigo = Usuario.objects.exclude(codigo_usuario='').order_by('-codigo_usuario').first()
            if ultimo_codigo and ultimo_codigo.codigo_usuario.isdigit():
                nuevo_codigo = int(ultimo_codigo.codigo_usuario) + 1
            else:
                nuevo_codigo = 1
            self.codigo_usuario = str(nuevo_codigo).zfill(4)
        super().save(*args, **kwargs)