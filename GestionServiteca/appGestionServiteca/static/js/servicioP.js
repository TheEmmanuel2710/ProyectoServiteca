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
    $("#btnAgregarDatosGenerales").click(function () {
        agregarDatosG();
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
 * Realiza la peticion ajax para registrar
 * la entrada de serviciosPrestados 
 */
function agregarDatosG() {
    var datos = {
        "cliente": $("#cbCliente").val(),
        "vehiculo": $("#cbVehiculo").val(),
        "observaciones": $("#txtObservaciones").val(),
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
 * Agrega cada servicio al arreglo de DetalleServiciosPrestados,
 * primero valida que no se haya agregado previamente
 */
function agregarServiciospDetalle() {
    //Averigua si ya se ha agregado el servicio
    const d = DetalleServiciosPrestados.find(servicio => servicio.idServicio == $("#cbServicio").val());
    if (d == null) {
        const servi = {
            "empleado": $("#cbEmpleado").val(),
            "estado": $("#cbEstado").val(),
            "idServicio": $("#cbServicio").val(),
            "costo": $("#txtCosto").val(),
        }
        DetalleServiciosPrestados.push(servi);
        frmDatosGenerales.reset();
        mostrarDatosTabla();
    } else {
        Swal.fire("Sistema Serviteca",
            "El Servicio seleccionado ya se ha agregado en el detalle.", "info");
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
        datos += "<td class='text-center' style='whidth:69%;'>" + clientes[posC].nombre + "</td>";
        datos += "<td class='text-center'>" + vehiculos[posV].placa + "</td>";
        datos += "<td class='text-center'>" + empleados[posE].nombre + "</td>";
        datos += "<td class='text-center'>" + "Melo" + "</td>";
        datos += "<td class='text-center'>" + servicios[posS].nombre + "</td>";
        datos += "<td class='text-center'>" + "$" + servicios[posS].costo + "</td>";
        datos += "<td class='text-center'>" + "Hoy" + "</td>";
        datos += "<td class='text-center'>" + "La buena hp" + "</td>";
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
function cargarClientes(nombre) {
    const cliente = {
        nombre: nombre,
    }
    clientes.push(cliente);
}


function cargarVehiculos(placa) {
    const vehiculo = {
        placa: placa
    }
    vehiculos.push(vehiculo);
}

function cargarEmpleados(nombre) {
    const empleado = {
        nombre: nombre,
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