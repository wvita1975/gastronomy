from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from core.models import DetalleOrdenServicio, MovimientoInventario, Articulo
from django.core.exceptions import ValidationError

@receiver([post_save, post_delete], sender=DetalleOrdenServicio)
def actualizar_totales_orden(sender, instance, **kwargs):
    orden = instance.orden
    detalles = orden.detalles.all()

    total_neto = sum(d.precio_unitario * d.cantidad for d in detalles)
    servicio = total_neto * (orden.porcentaje_servicio / 100)
    impuesto = total_neto * (orden.porcentaje_impuesto / 100)
    descuento = total_neto * (orden.porcentaje_descuento / 100)

    orden.total_neto = total_neto
    orden.total_final = total_neto + servicio + impuesto - descuento
    orden.save(update_fields=['total_neto', 'total_final'])

@receiver(post_save, sender=DetalleOrdenServicio)
def comprometer_stock(sender, instance, created, **kwargs):
    if created:
        articulo = instance.articulo
        cantidad = instance.cantidad

        # Validación de stock
        if articulo.cantidad < cantidad:
            raise ValidationError(f"Stock insuficiente para {articulo.nombre}. Disponible: {articulo.cantidad}")

        # Descontar stock
        articulo.cantidad -= cantidad
        articulo.save(update_fields=['cantidad'])

        # Generar movimiento
        MovimientoInventario.objects.create(
            articulo=articulo,
            tipo='salida',
            cantidad=cantidad,
            almacen=articulo.almacen,
            orden_servicio=instance.orden,
            observacion=f"Salida por orden de servicio {instance.orden.codigo_orden}"
        )

# Senal para actualizar el stock del articulo y registrar el movimiento

@receiver(post_save, sender=MovimientoInventario)
def registrar_movimiento_inventario(instance, **kwargs):
    articulo = getattr(instance, "articulo", None)
    if articulo:
        print(f"Movimiento registrado: {instance.tipo} de {articulo.nombre} ({instance.cantidad})")
    else:
        print("Movimiento registrado sin artículo asignado")


@receiver(post_save, sender=MovimientoInventario)
def actualizar_stock(instance, created, **kwargs):
    if not created:
        return

    articulo = getattr(instance, "articulo", None)
    if not articulo:
        print("Movimiento sin artículo asignado")
        return

    if instance.tipo == 'entrada':
        articulo.cantidad += instance.cantidad
    elif instance.tipo == 'salida':
        if articulo.cantidad < instance.cantidad:
            raise ValidationError("Stock insuficiente")
        articulo.cantidad -= instance.cantidad

    articulo.save(update_fields=['cantidad'])
    print(f"✅ Stock actualizado para {articulo.nombre}: {articulo.cantidad}")

@receiver(post_save, sender=Articulo)
def crear_movimiento_inicial(sender, instance, created, **kwargs):
    if created and instance.cantidad > 0:
        MovimientoInventario.objects.create(
            tipo='entrada',
            articulo=instance,
            cantidad=instance.cantidad,
            almacen=instance.almacen  # ← asegúrate de que el artículo tenga este campo
        )
