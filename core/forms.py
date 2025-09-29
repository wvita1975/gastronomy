from django import forms
from .models import MovimientoInventario, Stock

class MovimientoInventarioForm(forms.ModelForm):
    stock_actual = forms.DecimalField(
        label="Stock actual en almacén",
        required=False,
        disabled=True,
        widget=forms.NumberInput(attrs={'placeholder': 'Seleccione un artículo y un almacén'})
    )

    class Meta:
        model = MovimientoInventario
        fields = [
            'articulo', 
            'almacen', 
            'tipo_movimiento', 
            'cantidad',
            'motivo_ajuste',
            'descripcion',
            'stock_actual' ###
        ]
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['articulo'].widget.attrs.update({'class': 'select2'})
        self.fields['almacen'].widget.attrs.update({'class': 'select2'})

        self.order_fields([
            'articulo',
            'almacen',
            'stock_actual', # Mostrar el stock justo después de seleccionar el almacén.
            'tipo_movimiento',
            'cantidad',
            'motivo_ajuste',
            'descripcion'
        ])
    
    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data