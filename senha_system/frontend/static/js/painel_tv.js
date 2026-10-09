let ultimaChamada = null;
let audioLiberado = false;

function ativarAudio() {

    const teste = new SpeechSynthesisUtterance("Áudio ativado");

    teste.lang = "pt-BR";
    teste.rate = 0.9;
    teste.volume = 1;
    teste.pitch = 1;

    window.speechSynthesis.cancel();

    window.speechSynthesis.speak(teste);

    audioLiberado = true;

    document.getElementById("btnAudio").style.display = "none";

    console.log("🔊 Áudio liberado");
}

function falarSenha(senha, guiche) {
    if (!audioLiberado) {
        console.log("⚠️ Áudio ainda não foi liberado." );
        return;
    }
    const texto =`Senha ${senha}, dirigir-se ao guichê ${guiche}`;
    console.log("🔊 FALANDO:",texto);

    const speech =new SpeechSynthesisUtterance(texto);

    speech.lang = "pt-BR";
    speech.rate = 0.9;
    speech.volume = 1;
    speech.pitch = 1;

    window.speechSynthesis.cancel();

    setTimeout(() => {window.speechSynthesis.speak(speech);}, 100);
}

async function atualizarPainel() {
    try {
        const response = await fetch("/filas/tv/data/");
        if (!response.ok) {
            throw new Error("Erro HTTP: " + response.status);
        }
        const data = await response.json();

        console.log("📡 Dados recebidos:",data);

        if (data.ultima) {
            const senha = data.ultima.senha;
            const guiche = data.ultima.guiche;
            const chamadaAtual = data.ultima.chamada_id;
            const acao = data.ultima.acao;

            const senhaEl =document.getElementById("senha-atual");
            const guicheEl = document.getElementById( "guiche-atual");

            senhaEl.innerText = senha;

            guicheEl.innerText = "Dirija-se ao guichê " + guiche;

            senhaEl.classList.remove( "destaque");

            void senhaEl.offsetWidth;

            senhaEl.classList.add("destaque");

            console.log("📢 Chamada recebida:",
                {
                    id: chamadaAtual,
                    acao: acao,
                    senha: senha,
                    guiche: guiche
                }
            );


            if (ultimaChamada !==chamadaAtual) {
                console.log("🔔 NOVA CHAMADA DETECTADA");
                ultimaChamada =chamadaAtual;
                falarSenha(senha , guiche);
            }
        }

        const ultimasLista = document.getElementById("ultimas-lista");

        ultimasLista.innerHTML = "";

        data.ultimas.forEach(
            (item, index) => {
                const li = document.createElement("li");
                li.innerText =
                    `Senha ${item.senha} - ` +
                    `Guichê ${item.guiche}`;

                if (index === 0) {
                    li.classList.add("highlight");
                }
                ultimasLista.appendChild(li);
            }
        );

        const filaLista = document.getElementById("fila-lista");
        filaLista.innerHTML = "";

        data.fila.forEach(
            (senha) => {
                const li = document.createElement("li");
                li.innerText = senha;
                filaLista.appendChild(li);
            }
        );

    } catch (error) {
        console.error("❌ Erro ao atualizar painel:",error);
    }
}

setInterval(
    atualizarPainel,
    3000);

atualizarPainel();

const banners =
    JSON.parse(document.getElementById("banners-data").textContent);

let bannerIndex = 0;
let timerBanner = null;

function trocarBanner() {

    const imgEl = document.getElementById("banner-img");

    const videoEl = document.getElementById("banner-video");

    const sourceEl = document.getElementById("video-source");


    if (
        banners.length === 0) {
        imgEl.src = "/static/img/sem-propaganda.png";
        imgEl.classList.add("ativo");
        videoEl.classList.remove("ativo");
        return;
    }


    const arquivo = banners[bannerIndex];

    const arquivoLower = arquivo.toLowerCase();


    const isVideo =
        arquivoLower.includes(".mp4") ||
        arquivoLower.includes(".webm") ||
        arquivoLower.includes(".ogg");


    clearTimeout(
        timerBanner
    );

    if (isVideo) {
        console.log("🎬 VIDEO:", arquivo);
        imgEl.classList.remove("ativo");

        videoEl.pause();


        sourceEl.src = "/media/" + arquivo;

        videoEl.load();

        videoEl.classList.add("ativo");

        videoEl.play().then(() => {
                console.log("▶️ Vídeo iniciado");
            })
            .catch((erro) => {
                console.log("❌ Erro vídeo:", erro);
            });

        videoEl.onended = () => {
            bannerIndex = (bannerIndex + 1) % banners.length;
            trocarBanner();
        };


    } else {
        console.log("🖼️ IMAGEM:",arquivo );

        videoEl.pause();
        videoEl.classList.remove( "ativo");

        imgEl.src ="/media/" + arquivo;
        imgEl.classList.add("ativo");


        timerBanner =
            setTimeout(() => {
                bannerIndex =(bannerIndex + 1) % banners.length;
                trocarBanner();
            }, 8000);
    }
}

trocarBanner();