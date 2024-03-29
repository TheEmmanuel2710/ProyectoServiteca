let serviciosPrestados = []
let servicios = []
let clientes = []
let vehiculos = []
let empleados = []
let idServicio;

$(function () {
    $.ajaxSetup({
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        }
    });
    $("#btnAgregarDetalleServicioP").click(function () {
        if (validarCamposDetalleServicioP()) {
            agregarDetalleServicioPrestados();
        } else {
            Swal.fire({
                title: "Registro Servicio Prestado",
                text: "Por favor, complete todos los campos del formulario.",
                icon: "error",
                confirmButtonText: "OK",
                confirmButtonColor: "black"
            });
        }
    });

    $("#btnRegistrarServicioP").click(function () {
        if (validarCamposRegistroServicioP()) {
            registroServivicioPrestado();
        } else {
            Swal.fire({
                title: "Registro Servicio Prestado",
                text: "Por favor, complete todos los campos del formulario.",
                icon: "error",
                confirmButtonText: "OK",
                confirmButtonColor: "black"
            });
        }
    });

    $("#cbServicio").change(function () {
        idServicio = $("#cbServicio").val();
        posServicio = servicios.findIndex(servicio => servicio.id == idServicio);
        costoServicio = servicios[posServicio].costo;
        $("#txtCosto").val("$" + costoServicio);
    });
})

/**
 * Validacion del formulario
 */
function validarCamposDetalleServicioP() {
    return ($("#cbCliente").val() !== "" && $("#cbVehiculo").val() !== "" && $("#cbEmpleado").val() !== "" && $("#cbServicio").val() !== "");
}


function validarCamposRegistroServicioP() {
    return ($("#cbCliente").val() !== "" && $("#cbVehiculo").val() !== "" && $("#txtObservaciones").val() !== "" && serviciosPrestados.length > 0);
}


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
 *  Realiza una petición AJAX para registrar un servicio prestado, 
 * enviando datos relevantes como el cliente, el vehículo, la fecha&hora, observaciones y detalles.
 */
function registroServivicioPrestado() {
    var datos = {
        "idCliente": $("#cbCliente").val(),
        "idVehiculo": $("#cbVehiculo").val(),
        "observaciones": $("#txtObservaciones").val(),
        "detalle": JSON.stringify(serviciosPrestados),
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
                serviciosPrestados.length = 0;
                mostrarDatosTabla();
                Swal.fire({
                    title: 'Registro de Servicio Prestado',
                    text: resultado.mensaje,
                    icon: 'success',
                    confirmButtonColor: 'black',
                    confirmButtonText: 'Aceptar'
                }).then((result) => {
                    if (result.isConfirmed) {
                        location.href = "/vistaGestionarServiciosPrestados/"
                    }
                });
            } else {
                Swal.fire({
                    title: 'Error en el registro',
                    text: resultado.mensaje,
                    icon: 'error',
                    confirmButtonColor: 'black',
                    confirmButtonText: 'Aceptar'
                });
            }
        },
        error: function (error) {
            console.error(error);
            Swal.fire({
                title: 'Error en la petición',
                text: 'Ha ocurrido un error en la petición AJAX.',
                icon: 'error',
                confirmButtonColor: 'black',
                confirmButtonText: 'Aceptar'
            });
        }
    });
}

/**
 * Agrega detalles de un servicio prestado al arreglo serviciosPrestados, 
 * verificando si el servicio ya ha sido agregado.
 */
function agregarDetalleServicioPrestados() {
    const d = serviciosPrestados.find(servicio => servicio.idServicio == idServicio);
    if (d == null) {
        const detalle = {
            "idEmpleado": $("#cbEmpleado").val(),
            "idServicio": $("#cbServicio").val(),
            "servicio": $('#cbServicio option:selected').html(),
            "costo": $("#txtCosto").val(),
            "idCliente": $("#cbCliente").val(),
            "idVehiculo": $("#cbVehiculo").val(),
            "observaciones": $("#txtObservaciones").val(),
        }
        serviciosPrestados.push(detalle);
        frmdetalleSerciosP.reset();
        mostrarDatosTabla();
    } else {
        Swal.fire({
            title: 'Registro Detalle',
            text: 'El servicio seleccionado ya se ha agregado en el detalle,por favor verificar.',
            icon: 'info',
            confirmButtonColor: 'black',
            confirmButtonText: 'Aceptar'
        });
    }
}
/**
 * Construye filas de una tabla HTML para mostrar los detalles de los servicios prestados en el elemento tblDetalleSP.
*/
function mostrarDatosTabla() {
    datos = "";

    serviciosPrestados.forEach(detail => {
        posC = clientes.findIndex(cliente => cliente.idCliente == detail.idCliente);
        posV = vehiculos.findIndex(vehiculo => vehiculo.idVehiculo == detail.idVehiculo);
        posE = empleados.findIndex(empleado => empleado.idEmpleado == detail.idEmpleado);
        datos += "<tr>";
        datos += "<td class='text-center'>" + clientes[posC].nombre + "</td>";
        datos += "<td class='text-center'>" + vehiculos[posV].placa + "</td>";
        datos += "<td class='text-center'>" + empleados[posE].nombre + "</td>";
        datos += "<td class='text-center'>" + detail.servicio + "</td>";
        datos += "<td class='text-center'>" + detail.costo + "</td>";
        datos += "<td class='text-center'>" + detail.observaciones + "</td>";
        datos += "</tr>";
    });

    tblDetalleSP.innerHTML = datos;
}


/**
 *  Agrega datos de un cliente al arreglo clientes.
 * @param {*} idCliente 
 * @param {*} nombre 
 */
function cargarClientes(idCliente, nombre) {
    const cliente = {
        idCliente: idCliente,
        nombre: nombre
    }
    clientes.push(cliente);
}

/**
 *  Agrega datos de un vehículo al arreglo vehiculos.
 * @param {*} idVehiculo 
 * @param {*} placa 
 */
function cargarVehiculos(idVehiculo, placa) {
    const vehiculo = {
        idVehiculo: idVehiculo,
        placa: placa
    }
    vehiculos.push(vehiculo);
}

/**
 Agrega datos de un empleado al arreglo empleados.
 * @param {*} idEmpleado 
 * @param {*} nombre 
 */
function cargarEmpleados(idEmpleado, nombre) {
    const empleado = {
        idEmpleado: idEmpleado,
        nombre: nombre
    }
    empleados.push(empleado);
}

/**
 *  Agrega datos de un servicio al arreglo servicios.
 * @param {*} id 
 * @param {*} nombre 
 * @param {*} costo 
 */
function cargarServicios(id, nombre, costo) {
    const servicio = {
        id: id,
        nombre: nombre,
        costo: costo
    }

    servicios.push(servicio);
}