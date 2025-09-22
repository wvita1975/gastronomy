from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from core.models import DetalleOrdenServicio, OrdenServicio

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