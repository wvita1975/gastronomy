from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario

class UsuarioAdmin(UserAdmin):
    model = Usuario

    # Campos visibles al editar un usuario existente
    fieldsets = UserAdmin.fieldsets + (
        ('Información adicional', {
            'fields': ('rol', 'telefono', 'documento_identidad', 'codigo_usuario'),
        }),
    )

    # Campos visibles al crear un nuevo usuario
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'rol', 'telefono', 'documento_identidad'),
        }),
    )

    readonly_fields = ('codigo_usuario',)
    list_display = ('username', 'email', 'rol', 'codigo_usuario', 'is_staff')

admin.site.register(Usuario, UsuarioAdmin)