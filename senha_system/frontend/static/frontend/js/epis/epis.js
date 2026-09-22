document.addEventListener("DOMContentLoaded", function () {


const formulariosExclusao = document.querySelectorAll(
    ".form-excluir"
);

formulariosExclusao.forEach(function (formulario) {

    formulario.addEventListener("submit", function (event) {

        const nome = formulario.dataset.nome;

        const confirmar = window.confirm(
            `Tem certeza que deseja excluir o EPI "${nome}"?`
        );

        if (!confirmar) {
            event.preventDefault();
        }

    });

});


});
