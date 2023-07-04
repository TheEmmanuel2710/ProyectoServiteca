servicios = []
$(function () {
    $("#fileFoto").on("change", mostrarImagen);

    $("#cbServicio").change(function () {
        posServicio = servicios.findIndex(servicio => servicio.id == $("#cbServicio").val());
        costoServicio = servicios[posServicio].costo;
        $("#txtCosto").val("$" + costoServicio);
    })
    $("#btn-Consultar").click(function () {
        $("#tblServiciosSolicitados").removeAttr('disabled');
        $("#tblHistorialC").removeAttr('disabled');
    });
})

function Iniciar() {
    document.getElementById("tblServiciosSolicitados").style.display = "block";
    document.getElementById("tblHistorialC").style.display = "block";
}

function mostrarImagen(evento) {
    const archivos = evento.target.files
    const archivo = archivos[0]
    const url = URL.createObjectURL(archivo)
    $("#imagenMostrar").attr("src", url)
}

function cargarServicios(id, nombre, costo) {
    const servicio = {
        id: id,
        nombre: nombre,
        costo: costo
    }

    servicios.push(servicio);
}


$(function () {
    $("#fileFoto").on("change", mostrarImagen);
  });
  
  function mostrarImagen(evento) {
    const archivos = evento.target.files;
    const archivo = archivos[0];
    const url = URL.createObjectURL(archivo);
    $("#imagenMostrar").attr("src", url);
  }
  
  document.addEventListener("DOMContentLoaded", () => {
    const wrapper = document.querySelector(".wrapper");
    const btnPopup = document.querySelector(".btnLogin-popup");
    const iconClose = document.querySelector(".icon-close");
  
    btnPopup.addEventListener("click", () => {
      wrapper.classList.add("active-popup");
    });
  
    iconClose.addEventListener("click", () => {
      wrapper.classList.remove("active-popup");
    });
  });
  


  