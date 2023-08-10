let serviciosPrestados = []
let DetalleServiciosPrestados = []
let servicios = []
let clientes = []
let vehiculos = []
let empleados = []

$(function () {
    $.ajaxSetup({
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        }
    });
    $("#btnAgregarDetalleServicioP").click(function () {
        agregarServiciospDetalle();
    });
    $("#cbServicio").change(function () {
        posServicio = servicios.findIndex(servicio => servicio.id == $("#cbServicio").val());
        costoServicio = servicios[posServicio].costo;
        $("#txtCosto").val("$" + costoServicio);
    });
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
 * Agrega cada servicio al arreglo de DetalleServiciosPrestados,
 * primero valida que no se haya agregado previamente
 */
function agregarServiciospDetalle() {
    const cliente = $("#cbCliente").val();
    const vehiculo = $("#cbVehiculo").val();
    const observaciones = $("#txtObservaciones").val();
    const fechaHora = $("#txtFechaHoraSP").val();
    const empleado = $("#cbEmpleado").val();
    const estado = $("#cbEstado").val();
    const idServicio = $("#cbServicio").val();

    if (!cliente || !vehiculo || !observaciones || !fechaHora || !empleado || !estado || !idServicio) {
        Swal.fire("Registro Servicio Prestado",
            "Por favor, completa todos los campos antes de agregar el servicio.", "error");
        return;
    }

    const d = DetalleServiciosPrestados.find(servicio => servicio.idServicio == idServicio);
    if (d == null) {
        const servi = {
            "cliente": cliente,
            "vehiculo": vehiculo,
            "observaciones": observaciones,
            "fechaHora": fechaHora,
            "empleado": empleado,
            "estado": estado,
            "idServicio": idServicio,
            "servicio": $('#cbServicio option:selected').html(),
            "costo": $("#txtCosto").val(),
        }
        DetalleServiciosPrestados.push(servi);
        frmDatosGenerales.reset();
        mostrarDatosTabla();
    } else {
        Swal.fire("Sistema Serviteca",
            "El Servicio seleccionado ya se ha agregado en el detalle.", "error");
    }
}

function mostrarDatosTabla() {
    datos = "";
    DetalleServiciosPrestados.forEach(detail => {
        posC = clientes.findIndex(cliente => cliente.id == detail.idCliente);
        posV = vehiculos.findIndex(vehiculo => vehiculo.id == detail.idVehiculo);
        posE = empleados.findIndex(empleado => empleado.id == detail.idEmpleado);
        posS = servicios.findIndex(servicio => servicio.id == detail.idServicio);
        datos += "<tr>";
        datos += "<td class='text-center'>" + detail.cliente+ "</td>";
        datos += "<td class='text-center'>" + detail.vehiculo + "</td>";
        datos += "<td class='text-center'>" + detail.empleado + "</td>";
        datos += "<td class='text-center'>" + detail.estado + "</td>";
        datos += "<td class='text-center'>" + detail.servicio + "</td>";
        datos += "<td class='text-center'>" + detail.costo + "</td>";
        datos += "<td class='text-center'>" + detail.fechaHora + "</td>";
        datos += "<td class='text-center'>" + detail.observaciones + "</td>";
        datos += "</tr>";
    });
    //Agregar a la tabla con id tblDetalleSP
    tblDetalleSP.innerHTML = datos;
}

/**
 * Funcion que obtiene los datos de la lista y los guarda en un arreglo
 * @param {*} id 
 * @param {*} nombre 
 */
function cargarClientes(idCliente, nombre) {
    const cliente = {
        idCliente: idCliente,
        nombre: nombre
    }
    clientes.push(cliente);
}


function cargarVehiculos(idVehiculo, placa) {
    const vehiculo = {
        idVehiculo: idVehiculo,
        placa: placa
    }
    vehiculos.push(vehiculo);
}

function cargarEmpleados(idEmpleado, nombre) {
    const empleado = {
        idEmpleado: idEmpleado,
        nombre: nombre
    }
    empleados.push(empleado);
}

function cargarServicios(id, nombre, costo) {
    const servicio = {
        id: id,
        nombre: nombre,
        costo: costo
    }

    servicios.push(servicio);
}