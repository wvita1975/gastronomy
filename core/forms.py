from django import forms
from core.models import MovimientoInventario

class MovimientoInventarioForm(forms.ModelForm):
    stock_actual = forms.DecimalField(label="Stock actual", required=False, disabled=True)

    class Meta:
        model = MovimientoInventario
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        articulo = getattr(self.instance, "articulo", None)
        if articulo:
            self.fields['stock_actual'].initial = articulo.cantidad