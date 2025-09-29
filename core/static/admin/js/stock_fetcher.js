// Usamos el sistema de eventos de Django para asegurarnos de que el código
// se ejecuta correctamente con los widgets del admin (como los select2)

window.addEventListener('load', function() {
    (function($) {
        $(document).ready(function() {
            const articuloSelect = $('#id_articulo');
            const almacenSelect = $('#id_almacen');
            const stockField = $('#id_stock_actual');

            if (!articuloSelect.length || !almacenSelect.length || !stockField.length) {
                return; // Salir si no se encuentran los campos
            }

            function fetchStock() {
                const articuloId = articuloSelect.val();
                const almacenId = almacenSelect.val();

                // Solo hacer la llamada si AMBOS campos tienen un valor
                if (articuloId && almacenId) {
                    // Construir la URL de forma segura
                    const url = `/api/get-stock/?articulo=${articuloId}&almacen=${almacenId}`;
                    
                    fetch(url)
                        .then(response => response.json())
                        .then(data => {
                            // Actualizar el valor y el placeholder con la unidad
                            stockField.val(data.stock);
                            stockField.attr('placeholder', `Stock: ${data.stock} ${data.unidad}`);
                        })
                        .catch(error => {
                            console.error('Error fetching stock:', error);
                            stockField.val('');
                            stockField.attr('placeholder', 'Error al cargar stock');
                        });
                } else {
                    // Limpiar el campo si falta alguna selección
                    stockField.val('');
                    stockField.attr('placeholder', 'Seleccione un artículo y un almacén');
                }
            }

            // Escuchar el evento 'change' en AMBOS selectores
            articuloSelect.on('change', fetchStock);
            almacenSelect.on('change', fetchStock);

            // Opcional: Ejecutar una vez al cargar por si el formulario ya tiene datos (en modo edición)
            fetchStock();
        });
    })(django.jQuery);
});