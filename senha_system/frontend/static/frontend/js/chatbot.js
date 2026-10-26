document.addEventListener("DOMContentLoaded", function () {

    const chatbotButton = document.getElementById("chatbot-button");
    const chatbotWindow = document.getElementById("chatbot-window");
    const chatbotClose = document.getElementById("chatbot-close");

    const chatbotInput = document.getElementById("chatbot-input");
    const chatbotSend = document.getElementById("chatbot-send");

    const chatbotMessages = document.getElementById("chatbot-messages");

    /*
     * ==============================
     * ABRIR / FECHAR
     * ==============================
     */

    chatbotButton.addEventListener("click", function () {

        chatbotWindow.classList.toggle("active");

        if (chatbotWindow.classList.contains("active")) {
            chatbotInput.focus();
        }
    });

    chatbotClose.addEventListener("click", function () {
        chatbotWindow.classList.remove("active");
    });


    /*
     * ==============================
     * CSRF
     * ==============================
     */

    function getCookie(name) {

        let cookieValue = null;

        if (document.cookie && document.cookie !== "") {

            const cookies = document.cookie.split(";");

            for (let cookie of cookies) {

                cookie = cookie.trim();

                if (cookie.startsWith(name + "=")) {

                    cookieValue = decodeURIComponent(
                        cookie.substring(name.length + 1)
                    );

                    break;
                }
            }
        }

        return cookieValue;
    }


    /*
     * ==============================
     * ADICIONAR MENSAGEM
     * ==============================
     */

    function adicionarMensagem(texto, tipo) {

        const mensagem = document.createElement("div");

        mensagem.classList.add(
            "chat-message",
            tipo
        );

        mensagem.textContent = texto;

        chatbotMessages.appendChild(mensagem);

        chatbotMessages.scrollTop =
            chatbotMessages.scrollHeight;
    }


    /*
     * ==============================
     * SUGESTÕES
     * ==============================
     */

    function adicionarSugestoes(sugestoes) {

        if (!sugestoes || sugestoes.length === 0) {
            return;
        }

        const container =
            document.createElement("div");

        container.classList.add(
            "chatbot-suggestions"
        );

        sugestoes.forEach(function (sugestao) {

            const button =
                document.createElement("button");

            button.classList.add(
                "chatbot-suggestion"
            );

            button.textContent = sugestao;

            button.addEventListener(
                "click",
                function () {

                    chatbotInput.value = sugestao;

                    enviarPergunta();
                }
            );

            container.appendChild(button);
        });

        chatbotMessages.appendChild(container);

        chatbotMessages.scrollTop =
            chatbotMessages.scrollHeight;
    }


    /*
     * ==============================
     * INDICADOR
     * ==============================
     */

    function mostrarDigitando() {

        const typing =
            document.createElement("div");

        typing.id = "chatbot-typing";

        typing.classList.add(
            "chatbot-typing"
        );

        typing.textContent =
            "Assistente está digitando...";

        chatbotMessages.appendChild(typing);

        chatbotMessages.scrollTop =
            chatbotMessages.scrollHeight;
    }


    function removerDigitando() {

        const typing =
            document.getElementById(
                "chatbot-typing"
            );

        if (typing) {
            typing.remove();
        }
    }


    /*
     * ==============================
     * ENVIAR PERGUNTA
     * ==============================
     */

    async function enviarPergunta() {

        const pergunta =
            chatbotInput.value.trim();

        if (!pergunta) {
            return;
        }

        adicionarMensagem(
            pergunta,
            "user"
        );

        chatbotInput.value = "";

        chatbotSend.disabled = true;

        mostrarDigitando();

        try {

            const response =
                await fetch("/filas/chatbot/", {

                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json",

                        "X-CSRFToken":
                            getCookie("csrftoken")
                    },

                    body: JSON.stringify({
                        pergunta: pergunta
                    })
                });


            const data =
                await response.json();

            removerDigitando();


            if (!response.ok || !data.sucesso) {

                adicionarMensagem(
                    "Não foi possível processar sua pergunta.",
                    "bot"
                );

                return;
            }


            /*
             * Pequeno atraso para deixar
             * a conversa mais natural.
             */

            setTimeout(function () {

                adicionarMensagem(
                    data.resposta,
                    "bot"
                );

                adicionarSugestoes(
                    data.sugestoes
                );

            }, 300);


        } catch (error) {

            removerDigitando();

            console.error(
                "Erro no chatbot:",
                error
            );

            adicionarMensagem(
                "Não foi possível conectar ao assistente. Verifique sua conexão com o sistema e tente novamente.",
                "bot"
            );

        } finally {

            chatbotSend.disabled = false;

            chatbotInput.focus();
        }
    }


    /*
     * ==============================
     * BOTÃO ENVIAR
     * ==============================
     */

    chatbotSend.addEventListener(
        "click",
        enviarPergunta
    );


    /*
     * ==============================
     * ENTER
     * ==============================
     */

    chatbotInput.addEventListener(
        "keydown",
        function (event) {

            if (event.key === "Enter") {

                event.preventDefault();

                enviarPergunta();
            }
        }
    );

});