let tiempoInactividad = 0;
const tiempoSesionInactiva = 180;
sesionCerrada = false; 

function reiniciarTemporizador() {
    tiempoInactividad = 0;
}

function cerrarSesion() {
    if (!sesionCerrada) {
        sesionCerrada = true;
        Swal.fire({
            title: 'Sistema Serviteca',
            text: 'Inactividad detectada, cerrando sesión.',
            icon: 'info',
            confirmButtonColor: '#3085d6',
            confirmButtonText: 'Aceptar'
        }).then(() => {
            location.href = "/salir/";
        });
    }
}

function verificarInactividad() {
    tiempoInactividad++;

    if (tiempoInactividad >= tiempoSesionInactiva) {
        cerrarSesion();
    }
}

window.onload = function () {
    document.onmousemove = reiniciarTemporizador;
    document.onkeypress = reiniciarTemporizador;
    document.addEventListener("click", reiniciarTemporizador);
    document.addEventListener("mousemove", reiniciarTemporizador);
};

setInterval(verificarInactividad, 1000);
