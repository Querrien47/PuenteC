/* Validación del Formulario */

let currentIndex = 0;
const items = document.querySelectorAll('.carousel-item');
const totalItems = items.length;

function updateCarousel() {
    items.forEach((item, index) => {
        if (index === currentIndex) {
            item.classList.add('active');
        } else {
            item.classList.remove('active');
        }
    });
    const offset = -currentIndex * 100;
    document.querySelector('.carousel-inner').style.transform = translateX(${offset}%);
}

function prevSlide() {
    currentIndex = (currentIndex === 0) ? totalItems - 1 : currentIndex - 1;
    updateCarousel();
}

function nextSlide() {
    currentIndex = (currentIndex === totalItems - 1) ? 0 : currentIndex + 1;
    updateCarousel();
}

document.addEventListener('DOMContentLoaded', () => {
    updateCarousel();
});

/* Validación dle Formulario */

function validateForm() {
    var nombre = document.getElementById('nombre').value.trim();
    var email = document.getElementById('email').value.trim();
    var contraseña = document.getElementById('contraseña').value;
    var nivel = document.querySelector('input[name="nivel"]:checked');

    var emailRegex = /^\S+@\S+\.\S+$/;

    var errores = [];

    if (nombre === "") {
        errores.push("Por favor, ingresa tu nombre.");
    }

    if (!emailRegex.test(email)) {
        errores.push("Por favor, ingresa un correo electrónico válido.");
    }

    if (contraseña.length < 6) {
        errores.push("La contraseña debe tener al menos 6 caracteres.");
    }

    if (!nivel) {
        errores.push("Por favor, selecciona tu nivel educativo.");
    }

    if (errores.length > 0) {
        mostrarErrores(errores);
        return false;
    }

    return true;
}
