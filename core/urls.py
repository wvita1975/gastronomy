from django.urls import path
from core.views import get_stock_api # Asegúrate de importar la vista

urlpatterns = [
    # ... tus otras urls (como path('admin/', admin.site.urls),) ...
    path('api/get-stock/', get_stock_api, name='api_get_stock'),
]