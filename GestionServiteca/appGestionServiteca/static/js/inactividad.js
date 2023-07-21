let inactivityTime = 0;
const sessionTimeout = 2; // 3 minutos = 180 segundos
let isLoggedOut = false; // Variable para controlar si ya se mostró el mensaje

function resetTimer() {
    inactivityTime = 0;
}

function checkInactivity() {
    inactivityTime++;

    if (inactivityTime >= sessionTimeout && !isLoggedOut) {
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

        isLoggedOut = true; // Marca la variable como verdadera para que no se muestre el mensaje nuevamente
        // Aquí puedes agregar la lógica para cerrar la sesión si es necesario.
    }
}

window.onload = function() {
    document.onmousemove = resetTimer;
    document.onkeypress = resetTimer;
    document.addEventListener("click", resetTimer);
};

setInterval(checkInactivity, 1000);
