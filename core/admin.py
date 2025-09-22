from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario
from .models import Cliente
from .models import Proveedor
from .models import Locacion
from .models import Almacen
from .models import Articulo
from .models import MovimientoInventario
from .models import OrdenServicio
from .models import DetalleOrdenServicio

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

# Registro del modelo Locacion en el admin

@admin.register(Locacion)
class LocacionAdmin(admin.ModelAdmin):
    list_display = ('tipo', 'codigo', 'capacidad')


# Registro del modelo Cliente en el admin

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    readonly_fields = ('codigo_cliente',)
    list_display = (
        'codigo_cliente',
        'tipo_cliente',
        'tipo_identificacion',
        'nombres_apellidos',
        'documento_identidad',
        'villa',
        'mesa'
    )


# Registro del modelo Proveedor en el admin

@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    readonly_fields = ('codigo_proveedor',)
    list_display = ('codigo_proveedor', 'nombre', 'telefono', 'email')

# Registro del modelo Almacen en el admin

@admin.register(Almacen)
class AlmacenAdmin(admin.ModelAdmin):
    readonly_fields = ('codigo_almacen',)
    list_display = ('codigo_almacen', 'nombre', 'tipo_almacen', 'ubicacion')


# Registro del modelo CategoriaArticulo en el admin

from .models import CategoriaArticulo

@admin.register(CategoriaArticulo)
class CategoriaArticuloAdmin(admin.ModelAdmin):
    readonly_fields = ('codigo_categoria',)
    list_display = ('codigo_categoria', 'nombre')

# Registro del modelo Articulo en el admin

@admin.register(Articulo)
class ArticuloAdmin(admin.ModelAdmin):
    readonly_fields = ('codigo_articulo',)
    list_display = ('codigo_articulo', 'nombre', 'categoria', 'almacen', 'precio_unitario', 'cantidad')


# Registro del modelo MovimientoInventario en el admin

@admin.register(MovimientoInventario)
class MovimientoInventarioAdmin(admin.ModelAdmin):
    list_display = ('tipo', 'articulo', 'cantidad', 'fecha')


# Registro del modelo OrdenServicio y DetalleOrdenServicio en el admin

class DetalleOrdenInline(admin.TabularInline):
    model = DetalleOrdenServicio
    extra = 1
    readonly_fields = ('subtotal',)
    fields = ('articulo', 'cantidad', 'precio_unitario', 'subtotal')
    can_delete = False

    def subtotal(self, obj):
        return obj.subtotal() if obj.pk else '—'
    subtotal.short_description = 'Subtotal'

@admin.register(OrdenServicio)
class OrdenServicioAdmin(admin.ModelAdmin):
    inlines = [DetalleOrdenInline]

    readonly_fields = (
        'codigo_orden', 'fecha_creacion', 'fecha_cierre',
        'cedula_cliente', 'numero_villa', 'numero_mesa',
        'total_neto', 'total_final',
    )

    list_display = (
        'codigo_orden', 'cliente', 'cedula_cliente',
        'numero_villa', 'numero_mesa', 'estatus',
        'total_final', 'usuario', 'fecha_creacion', 'fecha_cierre',
    )

    list_filter = ('estatus', 'fecha_creacion', 'cliente')
    search_fields = ('codigo_orden', 'cliente__nombres_apellidos', 'cedula_cliente')
