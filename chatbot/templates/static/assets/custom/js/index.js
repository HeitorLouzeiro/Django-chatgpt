let chat = document.querySelector('#chat');
let input = document.querySelector('#input');
let botaoEnviar = document.querySelector('#botao-enviar');

async function enviarMensagem() {
    if (input.value === "" || input.value === null) return;

    let mensagem = input.value;
    input.value = "";

    let novaBolha = criaBolhaUsuario();
    novaBolha.innerHTML = mensagem;
    chat.appendChild(novaBolha);

    let novaBolhaBot = criaBolhaBot();
    chat.appendChild(novaBolhaBot);
    vaiParaFinalDoChat();

    // Envia requisição com a mensagem para a API do ChatBot
    const resposta = await fetch("http://127.0.0.1:8000/chat/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({'msg': mensagem}),
    });

    const respostaJson = await resposta.json();
    const respostaFormatada = respostaJson.response.join('');

    await exibirComEfeitoDeDigitacao(novaBolhaBot, respostaFormatada);
}


async function exibirComEfeitoDeDigitacao(elemento, texto) {
    const delay = 20; // Ajuste o atraso conforme necessário
    const textoComQuebrasDeLinha = texto.replace(/\n/g, '<br>');
    for (let i = 0; i < textoComQuebrasDeLinha.length; i++) {
        await esperar(delay);
        elemento.innerHTML += textoComQuebrasDeLinha[i];
        vaiParaFinalDoChat();
    }

    // Use uma div para garantir que as quebras de linha sejam exibidas corretamente
    const div = document.createElement('div');
    div.innerHTML = textoComQuebrasDeLinha;
    elemento.innerHTML = div.innerHTML;
}

function esperar(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

function criaBolhaUsuario() {
    let bolha = document.createElement('p');
    bolha.classList = 'chat__bolha chat__bolha--usuario';
    return bolha;
}

function criaBolhaBot() {
    let bolha = document.createElement('p');
    bolha.classList = 'chat__bolha chat__bolha--bot';
    return bolha;
}

function vaiParaFinalDoChat() {
    chat.scrollTop = chat.scrollHeight;
}

botaoEnviar.addEventListener('click', enviarMensagem);
input.addEventListener("keyup", function(event) {
    event.preventDefault();
    if (event.keyCode === 13) {
        botaoEnviar.click();
    }
});