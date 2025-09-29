from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .forms import MovimientoInventarioForm
from .models import (
    Usuario, Locacion, Cliente, Almacen, CategoriaArticulo, 
    Articulo, Stock, MovimientoInventario, OrdenServicio, DetalleOrdenServicio,
)

# 1. Personalización del Admin para el modelo Usuario
# ----------------------------------------------------

@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Datos Adicionales', {'fields': ('rol', 'telefono', 'documento_identidad', 'codigo_usuario')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Datos Adicionales', {'fields': ('rol', 'telefono', 'documento_identidad')}),
    )
    
    list_display = ('username', 'first_name', 'last_name', 'rol', 'codigo_usuario', 'is_staff')
  
    list_filter = UserAdmin.list_filter + ('rol',)
    # código de usuario de solo lectura
    readonly_fields = ('codigo_usuario',)


# 2. Modelos simples con personalización básica
# -----------------------------------------------

@admin.register(Locacion)
class LocacionAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'tipo', 'capacidad')
    list_filter = ('tipo',)
    search_fields = ('codigo',)

@admin.register(CategoriaArticulo)
class CategoriaArticuloAdmin(admin.ModelAdmin):
    list_display = ('codigo_categoria', 'nombre')
    search_fields = ('nombre', 'codigo_categoria')
    readonly_fields = ('codigo_categoria',)

# 3. Modelos con Inlines para gestión anidada
# ---------------------------------------------
# Inline para gestionar el Stock desde el Artículo o el Almacén
class StockForArticuloInline(admin.TabularInline):
    model = Stock
    extra = 1
    autocomplete_fields = ['almacen'] 

class StockForAlmacenInline(admin.TabularInline):
    model = Stock
    extra = 1
    autocomplete_fields = ['articulo']    


# 4. Admin para Articulo y Almacen (usando los inlines correctos)

@admin.register(Articulo)
class ArticuloAdmin(admin.ModelAdmin):
    list_display = ('codigo_articulo', 'nombre', 'categoria', 'unidad_medida', 'stock_total')
    list_filter = ('codigo_articulo', 'categoria', 'unidad_medida')
    search_fields = ('nombre', 'codigo_articulo')
    readonly_fields = ('codigo_articulo', 'stock_total')
    inlines = [StockForArticuloInline] # Usa el inline específico para Artículo
    autocomplete_fields = ['categoria']

@admin.register(Almacen)
class AlmacenAdmin(admin.ModelAdmin):
    list_display = ('codigo_almacen', 'nombre', 'tipo_almacen')
    list_filter = ('tipo_almacen',)
    search_fields = ('nombre', 'codigo_almacen')
    readonly_fields = ('codigo_almacen',)
    inlines = [StockForAlmacenInline] # Usa el inline específico para Almacén


# 4. Modelo Cliente con organización de campos
# ----------------------------------------------

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('codigo_cliente', 'nombres_apellidos', 'tipo_cliente', 'documento_identidad', 'villa', 'mesa')
    list_filter = ('tipo_cliente',)
    search_fields = ('nombres_apellidos', 'documento_identidad', 'codigo_cliente')
    readonly_fields = ('codigo_cliente',)
    fieldsets = (
        ('Información Personal', {'fields': ('nombres_apellidos', 'tipo_identificacion', 'documento_identidad', 'telefono', 'direccion')}),
        ('Clasificación y Ubicación', {'fields': ('tipo_cliente', 'villa', 'mesa')}),
        ('Sistema', {'fields': ('codigo_cliente',), 'classes': ('collapse',)})
    )
    autocomplete_fields = ['villa', 'mesa']


# 5. Modelos de Inventario (principalmente para consulta)
# --------------------------------------------------------
@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ('articulo', 'almacen', 'cantidad')
    list_filter = ('almacen',)
    search_fields = ('articulo__nombre', 'almacen__nombre')
    autocomplete_fields = ['articulo', 'almacen']

@admin.register(MovimientoInventario)
class MovimientoInventarioAdmin(admin.ModelAdmin):
    form = MovimientoInventarioForm
    list_display = ('codigo_movimiento', 'articulo', 'almacen', 'tipo_movimiento', 'cantidad', 'fecha_movimiento', 'orden_servicio')
    list_filter = ('tipo_movimiento', 'almacen', 'fecha_movimiento')
    search_fields = ('codigo_movimiento', 'articulo__nombre', 'orden_servicio__codigo_orden')
    readonly_fields = [f.name for f in MovimientoInventario._meta.fields]
    autocomplete_fields = ['articulo', 'almacen', 'orden_servicio']
    # def has_add_permission(self, request): return False
    # def has_delete_permission(self, request, obj=None): return False

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return [field.name for field in self.model._meta.fields]
        return []

    def has_add_permission(self, request):
        return True

    def has_delete_permission(self, request, obj=None):
        return False

# Vinculamos nuestro archivo JavaScript a esta página del admin.
    class Media:
        js = ('admin/js/stock_fetcher.js',)


# 6. Gestión Completa de Órdenes de Servicio
# ---------------------------------------------

class DetalleOrdenServicioInline(admin.TabularInline):
    model = DetalleOrdenServicio
    extra = 1 # Muestra 1 línea vacía para añadir un nuevo artículo
    readonly_fields = ('subtotal',) # Muestra el subtotal calculado
    autocomplete_fields = ['articulo', 'almacen'] # Facilita la selección de artículos y almacenes
    fields = ('articulo', 'almacen', 'cantidad', 'precio_unitario', 'subtotal')


@admin.register(OrdenServicio)
class OrdenServicioAdmin(admin.ModelAdmin):
    inlines = [DetalleOrdenServicioInline]
    list_display = ('codigo_orden', 'cliente', 'estatus', 'total_final', 'fecha_creacion', 'usuario')
    list_filter = ('estatus', 'fecha_creacion')
    search_fields = ('codigo_orden', 'cliente__nombres_apellidos', 'cedula_cliente')
    
    # Se ha añadido 'fecha_creacion' a la lista de campos de solo lectura.
    readonly_fields = (
        'codigo_orden', 'cedula_cliente', 'numero_villa', 'numero_mesa',
        'total_neto', 'total_final', 'fecha_cierre', 'fecha_creacion' 
    )
    
    # Organiza el formulario de edición en secciones claras
    fieldsets = (
        ('Información General', {
            'fields': ('codigo_orden', 'estatus', 'usuario', 'cliente')
        }),
        ('Datos Congelados del Cliente', {
            'fields': ('cedula_cliente', 'numero_villa', 'numero_mesa'),
            'classes': ('collapse',)
        }),
        ('Cálculos y Finanzas', {
            'fields': ('porcentaje_servicio', 'porcentaje_impuesto', 'porcentaje_descuento', 'total_neto', 'total_final')
        }),
        # Ahora que 'fecha_creacion' es readonly, Django lo mostrará correctamente aquí.
        ('Fechas Importantes', {
            'fields': ('fecha_creacion', 'fecha_cierre')
        }),
    )
    date_hierarchy = 'fecha_creacion'
    actions = ['marcar_como_cerrada', 'marcar_como_facturada']

    def get_readonly_fields(self, request, obj=None):
        # Si la orden ya existe (no es nueva), hacer cliente y usuario de solo lectura
        if obj: 
            return self.readonly_fields + ('cliente', 'usuario')
        return self.readonly_fields

    @admin.action(description='Marcar órdenes seleccionadas como Cerradas')
    def marcar_como_cerrada(self, request, queryset):
        queryset.update(estatus='cerrada')
        self.message_user(request, "Las órdenes seleccionadas han sido cerradas.")

    @admin.action(description='Marcar órdenes seleccionadas como Facturadas')
    def marcar_como_facturada(self, request, queryset):
        queryset.update(estatus='facturada')
        self.message_user(request, "Las órdenes seleccionadas han sido facturadas.")