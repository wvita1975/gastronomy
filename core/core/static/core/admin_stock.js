document.addEventListener('DOMContentLoaded', function () {
    const articuloSelect = document.querySelector('#id_articulo');
    const stockField = document.querySelector('#id_stock_actual');

    if (!articuloSelect || !stockField) return;

    articuloSelect.addEventListener('change', function () {
        const articuloId = this.value;
        if (!articuloId) return;

        fetch(`/admin/core/articulo/${articuloId}/stock/`)
            .then(response => response.json())
            .then(data => {
                stockField.value = data.cantidad;
            });
    });
});