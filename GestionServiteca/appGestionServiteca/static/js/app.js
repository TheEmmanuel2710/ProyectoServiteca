$(function () {
    $("#fileFoto").on("change", mostrarImagen);
})

function mostrarImagen(evento) {
    const archivos = evento.target.files;
    const archivo = archivos[0];
    const url = URL.createObjectURL(archivo);
    $("#imagenMostrar").attr("src", url)
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



  
  