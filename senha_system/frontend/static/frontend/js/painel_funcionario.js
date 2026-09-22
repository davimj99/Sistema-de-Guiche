// Controla se já animamos/tratamos essa chamada, mesmo com o áudio desativado.
let ultimaChamada = null;

/* Áudio desativado por enquanto.
function falarSenha(senha, guiche) {
    speechSynthesis.cancel();

    const texto = `Senha ${senha}, dirigir-se ao guichê ${guiche}.`;

    function falar() {
        const voz = new SpeechSynthesisUtterance(texto);
        voz.lang = "pt-BR";
        voz.rate = 0.9;
        voz.pitch = 1;
        speechSynthesis.speak(voz);
    }

    falar();

    setTimeout(falar, 3000);
    setTimeout(falar, 6000);
}
*/

function atualizarPainel() {
    fetch("/painel/dados/?t=" + Date.now(), {
        cache: "no-store"
    })
    .then(response => response.json())
    .then(data => {

        const senhaEl = document.getElementById("senha-atual");
        const guicheEl = document.getElementById("guiche-atual");
        const filaEl = document.getElementById("fila-espera");

        if (data.status === "sucesso") {

            const senha = data.dados.senha;
            const guiche = data.dados.guiche;
            const chamadaId = data.dados.chamada_id;

            senhaEl.innerText = senha;
            guicheEl.innerText = "Dirija-se ao " + guiche;

            if (ultimaChamada !== chamadaId) {

                senhaEl.classList.remove("destaque");
                void senhaEl.offsetWidth;
                senhaEl.classList.add("destaque");

                // Áudio desativado por enquanto — descomente a função acima
                // e a linha abaixo para reativar o anúncio por voz.
                // falarSenha(senha, guiche);

                ultimaChamada = chamadaId;
            }

        } else {

            senhaEl.innerText = "---";
            guicheEl.innerText = "";
        }

        filaEl.innerHTML = "";

        data.fila.forEach(senha => {
            const li = document.createElement("li");
            li.innerText = senha;
            filaEl.appendChild(li);
        });
    })
    .catch(error => console.error("Erro:", error));
}

setInterval(atualizarPainel, 3000);
atualizarPainel();