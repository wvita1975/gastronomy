from django.http import JsonResponse
from .models import Stock

def get_stock_api(request):
    articulo_id = request.GET.get('articulo')
    almacen_id = request.GET.get('almacen')
    stock = 0
    unidad = ""
    
    if articulo_id and almacen_id:
        try:
            stock_entry = Stock.objects.select_related('articulo').get(
                articulo_id=articulo_id, 
                almacen_id=almacen_id
            )
            stock = stock_entry.cantidad
            unidad = stock_entry.articulo.get_unidad_medida_display()
        except Stock.DoesNotExist:
            # Si no hay entrada de stock, la cantidad es 0
            stock = 0
            
    return JsonResponse({'stock': stock, 'unidad': unidad})