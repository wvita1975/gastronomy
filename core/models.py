from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.conf import settings
from django.utils import timezone
from django.db.models import F, Sum

# --- Modelo Usuario ---
class Usuario(AbstractUser):
    ROLES = [('admin', 'Administrador'), ('mesonero', 'Mesonero'), ('cocinero', 'Cocinero'), ('cajero', 'Cajero'), ('supervisor', 'Supervisor')]
    rol = models.CharField(max_length=20, choices=ROLES, blank=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    documento_identidad = models.CharField(max_length=20, blank=True, null=True)
    codigo_usuario = models.CharField(max_length=4, unique=True, editable=False, blank=True, null=True)
    def save(self, *args, **kwargs):
        if not self.codigo_usuario:
            with transaction.atomic():
                next_num = 1; ultimo = Usuario.objects.select_for_update().filter(codigo_usuario__regex=r'^\d{4}$').order_by(F('codigo_usuario').desc()).first()
                if ultimo:
                    try: next_num = int(ultimo.codigo_usuario) + 1
                    except (ValueError, TypeError): next_num = 1
                while True:
                    potential_code = str(next_num).zfill(4);
                    if not Usuario.objects.filter(codigo_usuario=potential_code).exists(): self.codigo_usuario = potential_code; break
                    next_num += 1
        super().save(*args, **kwargs)
    def __str__(self):
        full_name = f"{self.first_name} {self.last_name}".strip()
        return f"{self.codigo_usuario or 'Sin Código'} - {full_name or self.username}"

# --- Modelo Locacion ---
class Locacion(models.Model):
    TIPO_CHOICES = [('villa', 'Villa'), ('mesa', 'Mesa')]; tipo = models.CharField(max_length=10, choices=TIPO_CHOICES); codigo = models.CharField(max_length=20, unique=True); capacidad = models.PositiveIntegerField()
    def __str__(self): return f"{self.tipo.capitalize()} {self.codigo}"

# --- Modelo Cliente ---
class Cliente(models.Model):
    TIPO_IDENTIFICACION = [('V', 'Venezolano'), ('E', 'Extranjero'), ('P', 'Pasaporte')]; TIPO_CLIENTE = [('huesped', 'Huesped'), ('visitante', 'Visitante')]; nombres_apellidos = models.CharField(max_length=100); tipo_identificacion = models.CharField(max_length=1, choices=TIPO_IDENTIFICACION); documento_identidad = models.CharField(max_length=10, unique=True); direccion = models.TextField(max_length=150, blank=True, null=True); telefono = models.CharField(max_length=20, blank=True, null=True); tipo_cliente = models.CharField(max_length=12, choices=TIPO_CLIENTE, default='huesped'); villa = models.ForeignKey('Locacion', null=True, blank=True, on_delete=models.SET_NULL, limit_choices_to={'tipo': 'villa'}, related_name='clientes_villa'); mesa = models.ForeignKey('Locacion', null=True, blank=True, on_delete=models.SET_NULL, limit_choices_to={'tipo': 'mesa'}, related_name='clientes_mesa'); codigo_cliente = models.CharField(max_length=7, unique=True, editable=False, blank=True, null=True)
    def clean(self):
        super().clean()
        if self.tipo_cliente == 'huesped' and not self.villa: raise ValidationError({'villa': 'Huéspedes deben tener una villa.'})
        elif self.tipo_cliente == 'visitante':
            if not self.mesa: raise ValidationError({'mesa': 'Visitantes deben tener una mesa.'})
            if self.villa: raise ValidationError({'villa': 'Visitantes NO deben tener una villa.'})
    def save(self, *args, **kwargs):
        if not self.codigo_cliente:
            with transaction.atomic():
                next_num = 1; ultimo = Cliente.objects.select_for_update().filter(codigo_cliente__startswith='C').order_by(F('codigo_cliente').desc()).first()
                if ultimo and ultimo.codigo_cliente[1:].isdigit(): next_num = int(ultimo.codigo_cliente[1:]) + 1
                while True:
                    code = f"C{str(next_num).zfill(6)}";
                    if not Cliente.objects.filter(codigo_cliente=code).exists(): self.codigo_cliente = code; break
                    next_num += 1
        super().save(*args, **kwargs)
    def __str__(self): return f"{self.codigo_cliente or 'Sin Código'} - {self.nombres_apellidos}"

# --- Modelo Almacen ---
class Almacen(models.Model):
    TIPO_ALMACEN = [('principal', 'Principal'), ('secundario', 'Secundario')]; nombre = models.CharField(max_length=50, unique=True); ubicacion = models.CharField(max_length=100, blank=True, null=True); tipo_almacen = models.CharField(max_length=10, choices=TIPO_ALMACEN); codigo_almacen = models.CharField(max_length=4, unique=True, editable=False, blank=True, null=True)
    def save(self, *args, **kwargs):
        if not self.codigo_almacen:
            with transaction.atomic():
                next_num = 1; ultimo = Almacen.objects.select_for_update().filter(codigo_almacen__startswith='A').order_by(F('codigo_almacen').desc()).first()
                if ultimo and ultimo.codigo_almacen[1:].isdigit(): next_num = int(ultimo.codigo_almacen[1:]) + 1
                while True:
                    code = f"A{str(next_num).zfill(3)}";
                    if not Almacen.objects.filter(codigo_almacen=code).exists(): self.codigo_almacen = code; break
                    next_num += 1
        super().save(*args, **kwargs)
    def __str__(self): return f"{self.codigo_almacen or 'Sin Código'} - {self.nombre}"

# --- Modelo CategoriaArticulo ---
class CategoriaArticulo(models.Model):
    nombre = models.CharField(max_length=100, unique=True); descripcion = models.TextField(blank=True, null=True); codigo_categoria = models.CharField(max_length=10, unique=True, editable=False, blank=True, null=True)
    def save(self, *args, **kwargs):
        if not self.codigo_categoria:
            with transaction.atomic():
                next_num = 1; ultimo = CategoriaArticulo.objects.select_for_update().filter(codigo_categoria__startswith='CAT').order_by(F('codigo_categoria').desc()).first()
                if ultimo and ultimo.codigo_categoria[3:].isdigit(): next_num = int(ultimo.codigo_categoria[3:]) + 1
                while True:
                    code = f"CAT{str(next_num).zfill(7)}";
                    if not CategoriaArticulo.objects.filter(codigo_categoria=code).exists(): self.codigo_categoria = code; break
                    next_num += 1
        super().save(*args, **kwargs)
    def __str__(self): return f"{self.codigo_categoria or 'Sin Código'} - {self.nombre}"

UNIDADES_CHOICES = [('unidad', 'Unidad'), ('kg', 'Kilogramo'), ('lt', 'Litro'), ('m', 'Metro'), ('cm', 'Centímetro'), ('g', 'Gramo'), ('ml', 'Mililitro')]

# --- Modelo Articulo ---
class Articulo(models.Model):
    nombre = models.CharField(max_length=100, unique=True); categoria = models.ForeignKey(CategoriaArticulo, on_delete=models.PROTECT, related_name='articulos'); codigo_articulo = models.CharField(max_length=6, unique=True, editable=False, blank=True, null=True); unidad_medida = models.CharField(max_length=10, choices=UNIDADES_CHOICES, default='unidad')
    @property
    def stock_total(self): return self.stock_entries.aggregate(total=Sum('cantidad'))['total'] or 0
    def save(self, *args, **kwargs):
        if not self.codigo_articulo:
            with transaction.atomic():
                next_num = 1; ultimo = Articulo.objects.select_for_update().filter(codigo_articulo__startswith='A').order_by(F('codigo_articulo').desc()).first()
                if ultimo and ultimo.codigo_articulo[1:].isdigit(): next_num = int(ultimo.codigo_articulo[1:]) + 1
                while True:
                    code = f"A{str(next_num).zfill(5)}";
                    if not Articulo.objects.filter(codigo_articulo=code).exists(): self.codigo_articulo = code; break
                    next_num += 1
        super().save(*args, **kwargs)
    def __str__(self): return f"{self.codigo_articulo or 'Sin Código'} - {self.nombre}"

# --- Modelo Stock ---
class Stock(models.Model):
    articulo = models.ForeignKey(Articulo, on_delete=models.CASCADE, related_name='stock_entries'); almacen = models.ForeignKey(Almacen, on_delete=models.CASCADE, related_name='stock_entries'); cantidad = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    class Meta: unique_together = ('articulo', 'almacen')
    def clean(self):
        if self.cantidad < 0: raise ValidationError({'cantidad': 'La cantidad de stock no puede ser negativa.'})
    def __str__(self): return f"{self.articulo.nombre} en {self.almacen.nombre}: {self.cantidad}"

# --- Modelo MovimientoInventario ---
class MovimientoInventario(models.Model):
    TIPO_MOVIMIENTO = [('entrada', 'Entrada'), ('salida', 'Salida'), ('ajuste', 'Ajuste')]; codigo_movimiento = models.CharField(max_length=7, unique=True, editable=False, blank=True, null=True); articulo = models.ForeignKey('Articulo', on_delete=models.CASCADE, related_name='movimientos_inventario'); tipo_movimiento = models.CharField(max_length=10, choices=TIPO_MOVIMIENTO); cantidad = models.DecimalField(max_digits=10, decimal_places=2); fecha_movimiento = models.DateTimeField(auto_now_add=True); almacen = models.ForeignKey('Almacen', on_delete=models.PROTECT, related_name='movimientos_inventario'); orden_servicio = models.ForeignKey('OrdenServicio', null=True, blank=True, on_delete=models.SET_NULL, related_name='movimientos_inventario'); creado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='movimientos_inventario_creados'); descripcion = models.TextField(blank=True, null=True); motivo_ajuste = models.CharField(max_length=100, blank=True, null=True, help_text="Solo si el tipo es 'ajuste'.")
    class Meta: ordering = ['-fecha_movimiento']
    def __str__(self): return f"{self.codigo_movimiento or 'N/A'}"
    def clean(self):
        super().clean()
        if self.cantidad is None: return
        if self.cantidad <= 0 and self.tipo_movimiento in ['entrada', 'salida']: raise ValidationError({'cantidad': 'La cantidad debe ser > 0.'})
        if self.tipo_movimiento == 'ajuste' and not self.motivo_ajuste: raise ValidationError({'motivo_ajuste': 'Especifique el motivo.'})
        if self.tipo_movimiento == 'salida' or (self.tipo_movimiento == 'ajuste' and self.cantidad < 0):
            if not self.articulo or not self.almacen: return
            stock_entry = Stock.objects.filter(articulo=self.articulo, almacen=self.almacen).first()
            cantidad_a_verificar = abs(self.cantidad) if self.tipo_movimiento == 'ajuste' else self.cantidad
            if not stock_entry or stock_entry.cantidad < cantidad_a_verificar:
                disponible = stock_entry.cantidad if stock_entry else 0
                raise ValidationError({'cantidad': f'Stock insuficiente en {self.almacen.nombre}. Disponible: {disponible}'})
    def save(self, *args, **kwargs):
        is_new = not self.pk;
        if is_new: self.full_clean()
        with transaction.atomic():
            if is_new and not self.codigo_movimiento:
                next_num = 1; ultimo = MovimientoInventario.objects.select_for_update().filter(codigo_movimiento__startswith='M').order_by(F('codigo_movimiento').desc()).first()
                if ultimo and ultimo.codigo_movimiento and ultimo.codigo_movimiento[1:].isdigit(): next_num = int(ultimo.codigo_movimiento[1:]) + 1
                while True:
                    code = f"M{str(next_num).zfill(6)}";
                    if not MovimientoInventario.objects.filter(codigo_movimiento=code).exists(): self.codigo_movimiento = code; break
                    next_num += 1
            if is_new:
                cantidad_original = self.cantidad
                if self.tipo_movimiento == 'salida': self.cantidad = -abs(cantidad_original)
                elif self.tipo_movimiento == 'entrada': self.cantidad = abs(cantidad_original)
            super().save(*args, **kwargs)
            if is_new:
                stock_entry, created = Stock.objects.select_for_update().get_or_create(articulo=self.articulo, almacen=self.almacen, defaults={'cantidad': 0})
                stock_entry.cantidad = F('cantidad') + self.cantidad; stock_entry.save(update_fields=['cantidad']); stock_entry.refresh_from_db()

# --- Modelo OrdenServicio ---
class OrdenServicio(models.Model):
    ESTATUS = [('abierta', 'Abierta'), ('cerrada', 'Cerrada'), ('facturada', 'Facturada'), ('anulada', 'Anulada')]; codigo_orden = models.CharField(max_length=8, unique=True, editable=False, blank=True, null=True); usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='ordenes_creadas'); cliente = models.ForeignKey('Cliente', on_delete=models.PROTECT, related_name='ordenes_servicio'); cedula_cliente = models.CharField(max_length=20, editable=False, blank=True, null=True); numero_villa = models.CharField(max_length=10, editable=False, blank=True, null=True); numero_mesa = models.CharField(max_length=10, editable=False, blank=True, null=True); fecha_creacion = models.DateTimeField(auto_now_add=True); fecha_cierre = models.DateTimeField(null=True, blank=True); estatus = models.CharField(max_length=20, choices=ESTATUS, default='abierta'); porcentaje_servicio = models.DecimalField(max_digits=5, decimal_places=2, default=0.00); porcentaje_impuesto = models.DecimalField(max_digits=5, decimal_places=2, default=0.00); porcentaje_descuento = models.DecimalField(max_digits=5, decimal_places=2, default=0.00); total_neto = models.DecimalField(max_digits=12, decimal_places=2, editable=False, default=0.00); total_final = models.DecimalField(max_digits=12, decimal_places=2, editable=False, default=0.00)
    class Meta: ordering = ['-fecha_creacion']
    def __str__(self): return f"{self.codigo_orden or 'N/A'}"
    def recalcular_y_guardar_totales(self):
        detalles_agregados = self.detalles.aggregate(total_calculado=Sum(F('cantidad') * F('precio_unitario'))); subtotal = detalles_agregados['total_calculado'] or 0.00; servicio = subtotal * (self.porcentaje_servicio / 100); impuesto = subtotal * (self.porcentaje_impuesto / 100); descuento = subtotal * (self.porcentaje_descuento / 100); self.total_neto = subtotal; self.total_final = self.total_neto + servicio + impuesto - descuento; super().save(update_fields=['total_neto', 'total_final'])
    def save(self, *args, **kwargs):
        is_new = not self.pk;
        with transaction.atomic():
            if is_new and not self.codigo_orden:
                next_num = 1; ultimo = OrdenServicio.objects.select_for_update().filter(codigo_orden__startswith='OS').order_by(F('codigo_orden').desc()).first()
                if ultimo:
                    try: next_num = int(ultimo.codigo_orden[2:]) + 1
                    except (ValueError, IndexError): next_num = 1
                while True:
                    code = f"OS{str(next_num).zfill(6)}";
                    if not OrdenServicio.objects.filter(codigo_orden=code).exists(): self.codigo_orden = code; break
                    next_num += 1
            if is_new: self.cedula_cliente = self.cliente.documento_identidad; self.numero_villa = getattr(self.cliente.villa, 'codigo', None); self.numero_mesa = getattr(self.cliente.mesa, 'codigo', None)
            if self.estatus == 'cerrada' and not self.fecha_cierre: self.fecha_cierre = timezone.now()
            elif self.estatus != 'cerrada' and self.fecha_cierre: self.fecha_cierre = None
            super().save(*args, **kwargs)

# --- Modelo DetalleOrdenServicio ---
class DetalleOrdenServicio(models.Model):
    orden = models.ForeignKey('OrdenServicio', related_name='detalles', on_delete=models.CASCADE); articulo = models.ForeignKey('Articulo', on_delete=models.PROTECT, related_name='detalles_orden'); almacen = models.ForeignKey('Almacen', on_delete=models.PROTECT, related_name='detalles_despachados', null=True, blank=True); cantidad = models.PositiveIntegerField(null=True, blank=True); precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True); creado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='detalles_creados'); fecha_creacion = models.DateTimeField(auto_now_add=True); fecha_modificacion = models.DateTimeField(auto_now=True)
    @property
    def subtotal(self):
        if self.cantidad is not None and self.precio_unitario is not None: return self.cantidad * self.precio_unitario
        return 0
    def __str__(self): return f"{self.articulo.nombre if self.articulo else 'N/A'}"
    def clean(self):
        super().clean()
        if not self.articulo or not self.almacen or not self.cantidad: return
        try:
            stock_entry = Stock.objects.get(articulo=self.articulo, almacen=self.almacen)
            cantidad_disponible = stock_entry.cantidad
            if self.pk:
                try: cantidad_disponible += DetalleOrdenServicio.objects.get(pk=self.pk).cantidad
                except DetalleOrdenServicio.DoesNotExist: pass
            if cantidad_disponible < self.cantidad: raise ValidationError({'cantidad': f'Stock insuficiente en {self.almacen.nombre}. Disponible: {stock_entry.cantidad}'})
        except Stock.DoesNotExist: raise ValidationError({'articulo': f'No existe stock para {self.articulo.nombre} en {self.almacen.nombre}.'})
    def save(self, *args, **kwargs):
        if self.articulo and self.almacen and self.cantidad and self.precio_unitario: self.full_clean()
        super().save(*args, **kwargs)
        if self.orden_id and self.articulo and self.cantidad and self.precio_unitario:
            if hasattr(self.orden, 'recalcular_y_guardar_totales'): self.orden.recalcular_y_guardar_totales()
    def delete(self, *args, **kwargs):
        orden_a_actualizar = self.orden; super().delete(*args, **kwargs)
        if hasattr(orden_a_actualizar, 'recalcular_y_guardar_totales'): orden_a_actualizar.recalcular_y_guardar_totales()