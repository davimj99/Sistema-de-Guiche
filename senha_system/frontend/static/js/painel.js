async function atualizarPainel() {
    try {
        const response = await fetch("/painel/dados/?t=" + Date.now(), {
            cache: "no-store"
        });

        if (!response.ok) {
            throw new Error("Erro HTTP: " + response.status);
        }

        const data = await response.json();

        const senhaEl = document.getElementById("senha-atual");
        const guicheEl = document.getElementById("guiche-atual");
        const filaEl = document.getElementById("fila-espera");

        if (data.status === "sucesso") {

            const senha = data.dados.senha;
            const guiche = data.dados.guiche;
            const chamadaId = data.dados.chamada_id;

            senhaEl.innerText = senha;
            guicheEl.innerText = "Dirija-se ao " + guiche;

            senhaEl.classList.remove("destaque");
            void senhaEl.offsetWidth;
            senhaEl.classList.add("destaque");

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

    } catch (error) {
        console.error("Erro ao atualizar painel:", error);
    }
}

setInterval(atualizarPainel, 3000);

atualizarPainel();