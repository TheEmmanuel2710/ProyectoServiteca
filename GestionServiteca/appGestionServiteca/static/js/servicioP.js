let serviciosPrestados = []
let DetalleServiciosPrestados = []

$(function () {
    $.ajaxSetup({
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    $("#btnAgregarServicioPDetalle").click(function() {
        agregarServiciopDetalle();
    })
    $("#btnRegistrarDetalleServicioP").click(function() {
        registroDetalleEntrada();
    })
})

/**
 * Funcion utilizada para hacer peticiones ajax
 * necesarias en django reemplaza el csrf utilizado
 * en los formularios
 * @param {*} name 
 * @returns 
 */
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

/**
 * Realiza la peticion ajax para registrar
 * la entrada de serviciosPrestados 
 */
function registroDetalleEntrada() {
    var datos = {
        "cliente": $("#cbCliente").val(),
        "vehiculo": $("#cbVehiculo").val(),
        "observaciones":$("#txtObservaciones").val(),
        "fechaHora": $("#txtFechaHoraSP").val(),
        "detalle": JSON.stringify(DetalleServiciosPrestados),
    };
    $.ajax({
        url: "/registrarServicioPrestado/",
        data: datos,
        type: 'post',
        dataType: 'json',
        cache: false,
        success: function (resultado) {
            console.log(resultado);
            if (resultado.estado) {
                frmDatosGenerales.reset();
                DetalleServiciosPrestados.length = 0;
                mostrarDatosTabla();
            }
            Swal.fire("Registro de Servcios Prestados", resultado.mensaje, "success");
        }
    })
}
/**
 * Agrega cada material al arreglo de entredaserviciosPrestados,
 * primero valida que no se haya agregado previamente
 */
function agregarServiciopDetalle() {
    //Averigua si ya se ha agregado el material
    const m = DetalleServiciosPrestados.find(material => material.idMaterial == $("#cbServicio").val());
    if (m == null) {
        const material = {
            "idServicio": $("#cbServicio").val(),
            "cantidad": $("#txtCantidad").val(),
            "precio": $("#txtPrecio").val(),
            "idUnidadMedida": $("#cbUnidadMedida").val(),
            "estado": $("#cbEstado").val(),
        }
        DetalleServiciosPrestados.push(material);
        frmDatosGenerales.reset();
        mostrarDatosTabla();
    } else {
        Swal.fire("Entrada serviciosPrestados",
            "El material seleccionado ya se ha agregado en el detalle", "info");
    }
}

function mostrarDatosTabla() {
    datos = "";
    DetalleServiciosPrestados.forEach(entrada => {
        posM = serviciosPrestados.findIndex(material => material.idMaterial == entrada.idMaterial);
        posU = unidadesMedida.findIndex(unidad => unidad.id == entrada.idUnidadMedida);
        datos += "<tr>";
        datos += "<td class='text-center'>" + serviciosPrestados[posM].codigo + "</td>";
        datos += "<td>" + serviciosPrestados[posM].nombre + "</td>";
        datos += "<td class='text-center'>" + entrada.cantidad + "</td>";
        datos += "<td class='text-end'>" + entrada.precio + ".00" + "</td>";
        datos += "<td>" + unidadesMedida[posU].nombre + "</td>";
        datos += "<td class='text-center'>" + entrada.estado + "</td>";
        datos += "</tr>";
    });
    //Agregar a la tabla con id datosTablaserviciosPrestados
    tblDetalleSP.innerHTML=datos;
}

/**
 * funcion que obtiene los datos de la vista y los guarda en un arreglo
 * @param {*} idCliente 
 * @param {*} idVehiculo 
 * @param {*} idEmpleado 
 * @param {*} idServicio 
 */
function cargarServiciosPrestados(idCliente,idVehiculo,idEmpleado,idServicio) {
    const servicioP={
        "idCliente":idCliente,
        "idVehiculo":idVehiculo,
        "idEmpleado":idEmpleado,
        "idServicio":idServicio,
    }
    serviciosPrestados.push(servicioP);  
}