let tiempoInactividad = 0;
const tiempoSesionInactiva = 180; // 3 minutos = 180 segundos
let sesionCerrada = false; // Variable para controlar si ya se mostró el mensaje

function reiniciarTemporizador() {
    tiempoInactividad = 0;
}

function verificarInactividad() {
    tiempoInactividad++;

    if (tiempoInactividad >= tiempoSesionInactiva && !sesionCerrada) {
        Swal.fire({
            title: 'Sistema Serviteca',
            text: 'Inactividad detectada, cerrando sesión.',
            icon: 'info',
            confirmButtonColor: '#3085d6',
            confirmButtonText: 'Aceptar'
        }).then((result) => {
            if (result.isConfirmed) {
                location.href = "/salir/";
            }
        });

        sesionCerrada = true; // Marca la variable como verdadera para que no se muestre el mensaje nuevamente
        // Aquí puedes agregar la lógica para cerrar la sesión si es necesario.
    }
}

window.onload = function() {
    document.onmousemove = reiniciarTemporizador;
    document.onkeypress = reiniciarTemporizador;
    document.addEventListener("click", reiniciarTemporizador);

    // Agregamos la detección del movimiento del mouse
    document.addEventListener("mousemove", reiniciarTemporizador);
};

setInterval(verificarInactividad, 1000);
