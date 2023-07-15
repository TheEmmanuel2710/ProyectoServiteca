var idioma =
{
    "sProcessing": "Procesando...",
    "sLengthMenu": "Mostrar _MENU_ registros",
    "sZeroRecords": "No se encontraron resultados",
    "sEmptyTable": "Ningún dato disponible en esta tabla",
    "sInfo": "Mostrando registros del _START_ al _END_ de un total de _TOTAL_ registros",
    "sInfoEmpty": "Mostrando registros del 0 al 0 de un total de 0 registros",
    "sInfoFiltered": "(filtrado de un total de _MAX_ registros)",
    "sInfoPostFix": "",
    "sSearch": "Buscar:",
    "sUrl": "",
    "sInfoThousands": ",",
    "sLoadingRecords": "Cargando...",
    "oPaginate": {
        "sFirst": "Primero",
        "sLast": "Último",
        "sNext": "Siguiente",
        "sPrevious": "Anterior"
    },
    "oAria": {
        "sSortAscending": ": Activar para ordenar la columna de manera ascendente",
        "sSortDescending": ": Activar para ordenar la columna de manera descendente"
    },
    "buttons": {
        "copyTitle": 'Informacion copiada',
        "copyKeys": 'Use your keyboard or menu to select the copy command',
        "copySuccess": {
            "_": '%d filas copiadas al portapapeles',
            "1": '1 fila copiada al portapapeles'
        },

        "pageLength": {
            "_": "Mostrar %d filas",
            "-1": "Mostrar Todo"
        }
    }
};

var empresa = "SERVITECA OPITA";
var fecha = new Date();
var hoy = fecha.getDate() + "/" + (fecha.getMonth() + 1) + "/" + fecha.getFullYear();

/**
 *
 * @param {*} tabla tabla a utilizar
 * @param {*} titulo titulo a colocar en el documento a exportar
 * @param {*} columnas número de columnas en el datatable
 */
function cargarDataTable(tabla, titulo, col) {

    var columnas = [];
    for (i = 0; i < col; i++) {
        columnas.push(i);
    }

    if (col > 6) {
        orientacion = "landscape";
    } else {
        orientacion = "portrait";
    }
    tabla.dataTable({
        "paging": true,
        "destroy": true,
        "lengthChange": true,
        "searching": true,
        "ordering": true,
        "info": true,
        "autoWidth": true,
        "language": idioma,
        "lengthMenu": [[5, 20, 50, -1], [5, 20, 50, "Mostrar Todo"]],
        dom: 'Bfrtip',
        buttons: {
            dom: {
                container: {
                    tag: 'div',
                    //className: 'flexcontent'
                },
                buttonLiner: {
                    tag: null
                }
            },
            buttons: [
                {
                    extend: 'pageLength',
                    titleAttr: 'Registros a mostrar',
                    className: 'selectTable'
                },
                // {
                //     extend: 'copyHtml5',
                //     title: empresa,
                //     text:'<i class="fa fa-files-o"></i>',
                //     messageTop: titulo + "       Fecha: "+hoy,                           
                //     exportOptions: {
                //         columns:columnas
                //     }
                // },

                {
                    extend: 'pdfHtml5',
                    footer: true,
                    title: empresa,
                    titleAttr: 'Generar PDF',
                    className: 'bg-danger',
                    text: '<i class="fa fa-file-pdf-o text-white"></i>',
                    messageTop: titulo,
                    orientation: orientacion,
                    pageSize: 'LETTER',
                    exportOptions: {
                        columns: columnas
                    },
                    customize: function (doc) {
                        doc.content[1].margin = [5, 5, 5, 5],
                            doc.pageMargins = [20, 35, 20, 30],

                            doc.styles.title = {
                                color: '#39A900',
                                fontSize: '18',
                                alignment: 'center'
                            },
                            doc.styles.message = {
                                color: '#39A900',
                                fontSize: '14',
                                alignment: 'center'
                            },

                            doc.styles['td:nth-child(2)'] = {
                                width: '100px',
                                'max-width': '150px'
                            },

                            doc.styles.tableHeader = {
                                fillColor: '#00324D',
                                color: 'white',
                                alignment: 'center',
                            },
                            doc["header"] = function () {
                                return {
                                    columns: [
                                        {
                                            image: 'data:image/png;base64,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',
                                            width: 50,
                                            height: 50
                                        }
                                    ],
                                    margin: [40, 20, 0, 0]
                                }
                            },
                            doc['footer'] = (function (page, pages) {
                                return {
                                    columns: [
                                        {
                                            text: "Fecha: " + hoy,
                                            alignment: 'lef',
                                            color: '#39A900',
                                        },
                                        {
                                            text: "Centro de la Industria, la Empresa y los Servicios",
                                            alignment: 'center',
                                            color: '#39A900',
                                        },

                                        {
                                            alignment: 'right',
                                            color: '#39A900',
                                            text: ['página ', { text: page.toString() }, ' de ', { text: pages.toString() }]
                                        }
                                    ],
                                    margin: [50, 0],
                                }
                            });


                    }
                },
                // {
                //     extend: 'excelHtml5',                   
                //     title: empresa,
                //     text: '<i class="fa fa-file-excel-o text-success"></i>',
                //     messageTop: titulo + "       Fecha: "+hoy,                  
                //     exportOptions: {
                //         columns: columnas
                //     },
                // },
                {
                    extend: 'csvHtml5',
                    title: empresa,
                    titleAttr: 'Generar CSV',
                    className: 'bg-dark',
                    text: '<i class="fa fa-file-text-o text-white"></i>',
                    messageTop: titulo + "       Fecha: " + hoy,
                    exportOptions: {
                        columns: columnas
                    }
                },
            ]
        }
    });
}
