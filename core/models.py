from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.db import transaction

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

# Modelo para locaciones (mesas y villas)

class Locacion(models.Model):
    TIPO_CHOICES = [
        ('villa', 'Villa'),
        ('mesa', 'Mesa'),
    ]

    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    codigo = models.CharField(max_length=20, unique=True)
    capacidad = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.tipo.capitalize()} {self.codigo}"


# Modelo para clientes

class Cliente(models.Model):
    TIPO_IDENTIFICACION = [
        ('V', 'Venezolano'),
        ('E', 'Extranjero'),
        ('P', 'Pasaporte'),
    ]

    TIPO_CLIENTE = [
        ('huesped', 'Huésped'),
        ('visitante', 'Visitante'),
    ]

    nombres_apellidos = models.CharField(max_length=100, default='')
    tipo_identificacion = models.CharField(max_length=1, choices=TIPO_IDENTIFICACION)
    documento_identidad = models.CharField(max_length=9, unique=True)
    direccion = models.TextField(max_length=150)
    telefono = models.CharField(max_length=20)
    tipo_cliente = models.CharField(max_length=12, choices=TIPO_CLIENTE, default='visitante')

    villa = models.ForeignKey(
        'Locacion',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        limit_choices_to={'tipo': 'villa'},
        related_name='clientes_villa'
    )

    mesa = models.ForeignKey(
        'Locacion',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        limit_choices_to={'tipo': 'mesa'},
        related_name='clientes_mesa'
    )

    codigo_cliente = models.CharField(
        max_length=7,
        unique=True,
        editable=False,
        blank=True
    )

    def save(self, *args, **kwargs):
        if not self.codigo_cliente:
            ultimo = Cliente.objects.exclude(codigo_cliente='').order_by('-codigo_cliente').first()
            if ultimo and ultimo.codigo_cliente[1:].isdigit():
                nuevo_numero = int(ultimo.codigo_cliente[1:]) + 1
            else:
                nuevo_numero = 1
            self.codigo_cliente = f"C{str(nuevo_numero).zfill(6)}"
        super().save(*args, **kwargs)

    def clean(self):
        if self.tipo_cliente == 'huesped':
            if not self.villa:
                raise ValidationError({'villa': 'Los clientes tipo huésped deben tener una villa asignada.'})
            if not self.mesa:
                raise ValidationError({'mesa': 'Los clientes tipo huésped deben tener una mesa asignada.'})
        elif self.tipo_cliente == 'visitante':
            if self.villa:
                raise ValidationError({'villa': 'Los visitantes no deben tener una villa asignada.'})

    def __str__(self):
        return f"{self.codigo_cliente} - {self.nombres_apellidos} {self.nombres_apellidos}"


# Modelo para proveedores

class Proveedor(models.Model):
    nombre = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    direccion = models.TextField(blank=True)

    codigo_proveedor = models.CharField(
        max_length=7,
        unique=True,
        editable=False,
        blank=True
    )

    def save(self, *args, **kwargs):
        if not self.codigo_proveedor:
            ultimo = Proveedor.objects.exclude(codigo_proveedor='').order_by('-codigo_proveedor').first()
            if ultimo and ultimo.codigo_proveedor[1:].isdigit():
                nuevo_numero = int(ultimo.codigo_proveedor[1:]) + 1
            else:
                nuevo_numero = 1
            self.codigo_proveedor = f"P{str(nuevo_numero).zfill(6)}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.codigo_proveedor} - {self.nombre}"
    
# Modelo para almacenes

class Almacen(models.Model):
    TIPO_ALMACEN = [
        ('principal', 'Principal'),
        ('secundario', 'Secundario'),
    ]

    nombre = models.CharField(max_length=50)
    ubicacion = models.CharField(max_length=100, blank=True)
    tipo_almacen = models.CharField(max_length=10, choices=TIPO_ALMACEN)

    codigo_almacen = models.CharField(
        max_length=4,
        unique=True,
        editable=False,
        blank=True
    )

    def save(self, *args, **kwargs):
        if not self.codigo_almacen:
            ultimo = Almacen.objects.exclude(codigo_almacen='').order_by('-codigo_almacen').first()
            if ultimo and ultimo.codigo_almacen[1:].isdigit():
                nuevo_numero = int(ultimo.codigo_almacen[1:]) + 1
            else:
                nuevo_numero = 1
            self.codigo_almacen = f"A{str(nuevo_numero).zfill(3)}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.codigo_almacen} - {self.nombre} ({self.tipo_almacen})"
    
# Modelo para categorías de artículos

class CategoriaArticulo(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    
    codigo_categoria = models.CharField(
        max_length=10,
        unique=True,
        editable=False,
        blank=True
    )

    def save(self, *args, **kwargs):
        if not self.codigo_categoria:
            ultimo = CategoriaArticulo.objects.exclude(codigo_categoria='').order_by('-codigo_categoria').first()
            if ultimo and ultimo.codigo_categoria[1:].isdigit():
                nuevo_numero = int(ultimo.codigo_categoria[1:]) + 1
            else:
                nuevo_numero = 1
            self.codigo_categoria = f"T{str(nuevo_numero).zfill(5)}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.codigo_categoria} - {self.nombre}"
    

# Modelo para artículos

UNIDADES_CHOICES = [
    ('unidad', 'Unidad'),
    ('kg', 'Kilogramo'),
    ('lt', 'Litro'),
    ('m', 'Metro'),
    ('cm', 'Centímetro'),
    ('g', 'Gramo'),
    ('ml', 'Mililitro'),
]

class Categoria(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

class Articulo(models.Model):
    nombre = models.CharField(max_length=100)
    categoria = models.ForeignKey(CategoriaArticulo, on_delete=models.CASCADE)
    codigo = models.CharField(max_length=6, unique=True, editable=False)
    unidad = models.CharField(max_length=10, choices=UNIDADES_CHOICES, default='unidad')
    cantidad = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    almacen = models.ForeignKey('Almacen', on_delete=models.PROTECT)
    
    def save(self, *args, **kwargs):
        if not self.codigo:
            ultimo = Articulo.objects.order_by('-id').first()
            siguiente_numero = 1 if not ultimo else ultimo.id + 1
            self.codigo = f"A{siguiente_numero:05d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nombre} ({self.codigo})"


def __str__(self):
    if self.articulo_id:
        return f"{self.tipo.capitalize()} de {self.articulo.nombre}"
    return "Movimiento sin artículo"
    
#####  Modelo de movimientos de inventario

class MovimientoInventario(models.Model):
    TIPO_MOVIMIENTO = [
        ('entrada', 'Entrada'),
        ('salida', 'Salida'),
        ('ajuste', 'Ajuste'),
    ]

    codigo_movimiento = models.CharField(
        max_length=7,
        unique=True,
        editable=False,
        blank=True
    )

    articulo = models.ForeignKey('Articulo', on_delete=models.CASCADE)
    tipo = models.CharField(max_length=10, choices=TIPO_MOVIMIENTO)
    cantidad = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateTimeField(auto_now_add=True)
    almacen = models.ForeignKey('Almacen', on_delete=models.PROTECT)
    orden_servicio = models.ForeignKey('OrdenServicio', null=True, blank=True, on_delete=models.SET_NULL)
    creado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    descripcion = models.TextField(blank=True)

    motivo_ajuste = models.CharField(
        max_length=100,
        blank=True,
        help_text="Solo se usa si el tipo de movimiento es 'ajuste'. Ej: pérdida, corrección, sobrante"
    )

    def __str__(self):
        if self.articulo_id:
            return f"{self.codigo_movimiento} - {self.tipo.capitalize()} {self.articulo.nombre} ({self.cantidad}) en {self.almacen.nombre}"
        return "Movimiento sin artículo"

    def clean(self):
        super().clean()
        
        # 1. Validación de la cantidad de entrada/salida (debe ser positiva)
        if self.tipo in ['entrada', 'salida']:
            if self.cantidad <= 0:
                raise ValidationError({'cantidad': f'La cantidad para una {self.tipo} debe ser mayor a cero.'})
        
        # 2. Validación de ajustes (el signo se respeta)
        elif self.tipo == 'ajuste':
            if not self.motivo_ajuste:
                raise ValidationError({'motivo_ajuste': 'Debe especificar el motivo del ajuste.'})
        
        # 3. Normalizar la cantidad para la validación de inventario
        # Solo necesitamos que el valor sea negativo si va a restar stock.
        cantidad_a_validar = self.cantidad
        if self.tipo == 'salida':
            cantidad_a_validar = -self.cantidad # La salida siempre resta
        
        # 4. Validar existencia SI el movimiento reduce inventario (cantidad_a_validar es < 0)
        if cantidad_a_validar < 0:
            # Si el artículo se mueve a un almacén diferente (no es el stock actual)
            # Esto puede ser una validación compleja. Asumiremos que el stock del artículo 
            # (self.articulo.cantidad) es el stock en el almacén de este movimiento (self.almacen).
            
            # Comprobar si al aplicar el movimiento (resta) el stock se vuelve negativo.
            if self.articulo.cantidad + cantidad_a_validar < 0:
                raise ValidationError({
                    'cantidad': f'No hay suficiente inventario disponible en este almacén. Stock actual: {self.articulo.cantidad}, intento de retiro: {abs(cantidad_a_validar)}.'
                })

    def save(self, *args, **kwargs):
        with transaction.atomic():
            es_nuevo = not self.pk

        # --- PRE-GUARDADO DEL MovimientoInventario ---

        # Generar código único M000001 (Solo al crear)
        if es_nuevo and not self.codigo_movimiento:
            base_numero = 1
            while True:
                nuevo_codigo = f"M{str(base_numero).zfill(6)}"
                if not self.__class__.objects.filter(codigo_movimiento=nuevo_codigo).exists():
                    self.codigo_movimiento = nuevo_codigo
                    break
                base_numero += 1

        # NORMALIZAR LA CANTIDAD FINAL
        # Esta será la cantidad que se guardará en el objeto.
        if self.tipo == 'salida':
            # La cantidad que se guarda es NEGATIVA
            self.cantidad = -abs(self.cantidad)
        elif self.tipo == 'entrada':
            # La cantidad que se guarda es POSITIVA
            self.cantidad = abs(self.cantidad)
        # Para 'ajuste', la cantidad se respeta (puede ser +/-)

        # --- GUARDAR EL MovimientoInventario ---
        super().save(*args, **kwargs)

        # --- POST-GUARDADO: ACTUALIZACIÓN DEL Articulo ---
        # El cambio de stock solo debe aplicarse si el movimiento es NUEVO.
        if es_nuevo:
            # 1. Actualizar almacén (solo si la cantidad es positiva para un nuevo stock)
            if self.articulo.almacen != self.almacen and self.cantidad > 0:
                self.articulo.almacen = self.almacen
            
            # 2. Aplicar el cambio de stock
            # Se usa self.cantidad, que ya está normalizada (+ para entrada, - para salida/ajuste negativo).
            self.articulo.cantidad += self.cantidad
            
            # 3. Guardar el Artículo una sola vez
            self.articulo.save(update_fields=['cantidad', 'almacen']) 

# Modelo para órdenes de servicio

class OrdenServicio(models.Model):
    ESTATUS = [
        ('abierta', 'Abierta'),
        ('cerrada', 'Cerrada'),
        ('facturada', 'Facturada'),
        ('anulada', 'Anulada'),
    ]

    codigo_orden = models.CharField(max_length=8, unique=True, editable=False, blank=True)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    cliente = models.ForeignKey('Cliente', on_delete=models.PROTECT)
    cedula_cliente = models.CharField(max_length=20, editable=False)
    numero_villa = models.CharField(max_length=10, editable=False)
    numero_mesa = models.CharField(max_length=10, editable=False)

    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_cierre = models.DateTimeField(null=True, blank=True)
    estatus = models.CharField(max_length=20, choices=ESTATUS, default='abierta')

    porcentaje_servicio = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    porcentaje_impuesto = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    porcentaje_descuento = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)

    total_neto = models.DecimalField(max_digits=12, decimal_places=2, editable=False, default=0.00)
    total_final = models.DecimalField(max_digits=12, decimal_places=2, editable=False, default=0.00)

    def save(self, *args, **kwargs):
        es_nueva = not self.pk

        # Generar código único tipo OS000001
        if es_nueva and not self.codigo_orden:
            base_numero = 1
            while True:
                nuevo_codigo = f"OS{str(base_numero).zfill(6)}"
                if not OrdenServicio.objects.filter(codigo_orden=nuevo_codigo).exists():
                    self.codigo_orden = nuevo_codigo
                    break
                base_numero += 1

        # Congelar datos del cliente y ubicación
        if es_nueva:
            self.cedula_cliente = self.cliente.documento_identidad
            self.numero_villa = self.cliente.villa.codigo
            self.numero_mesa = self.cliente.mesa.codigo

        # Bloquear edición si está facturada y el usuario no tiene permisos
        if not es_nueva and self.estatus == 'facturada':
            if not self.usuario.groups.filter(name__in=['Supervisor', 'Administrador']).exists():
                raise ValidationError("No puedes modificar una orden facturada.")

        # Registrar fecha de cierre si aplica
        if self.estatus == 'cerrada' and not self.fecha_cierre:
            self.fecha_cierre = timezone.now()
        elif self.estatus != 'cerrada':
            self.fecha_cierre = None

        super().save(*args, **kwargs)  # ✅ Guarda primero para obtener el PK

        # Calcular totales después de guardar
        detalles = self.detalles.all()
        self.total_neto = sum(d.precio_unitario * d.cantidad for d in detalles)


        servicio = self.total_neto * (self.porcentaje_servicio / 100)
        impuesto = self.total_neto * (self.porcentaje_impuesto / 100)
        descuento = self.total_neto * (self.porcentaje_descuento / 100)

        self.total_final = self.total_neto + servicio + impuesto - descuento

        super().save(update_fields=['total_neto', 'total_final'])

        # Generar movimientos de inventario solo si es nueva
        if es_nueva:
            from core.models import MovimientoInventario
            for detalle in detalles:
                MovimientoInventario.objects.create(
                    articulo=detalle.articulo,
                    tipo='salida',
                    cantidad=detalle.cantidad,
                    almacen=detalle.articulo.almacen,
                    observacion=f"Salida por orden de servicio {self.codigo_orden}"
                )

    def __str__(self):
        return f"{self.codigo_orden} - {self.cliente.nombres_apellidos} ({self.estatus})"


# Modelo para detalles de órdenes de servicio

class DetalleOrdenServicio(models.Model):
    orden = models.ForeignKey('OrdenServicio', related_name='detalles', on_delete=models.CASCADE)
    articulo = models.ForeignKey('Articulo', on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    creado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)

    def subtotal(self):
        return self.cantidad * self.precio_unitario

    def clean(self):
        if self.articulo.cantidad < self.cantidad:
            raise ValidationError(f"Inventario insuficiente para '{self.articulo.nombre}'. Disponible: {self.articulo.cantidad}")

    def save(self, *args, **kwargs):
        self.full_clean()  # Ejecuta validaciones
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.articulo.nombre} x {self.cantidad} ({self.orden.codigo_orden})"