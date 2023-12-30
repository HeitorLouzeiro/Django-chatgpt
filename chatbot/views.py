import json
import os
from time import sleep

import tiktoken
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from openai import OpenAI

# Set OpenAI API key
api_key = os.environ.get('OPENAI_API_KEY')
client = OpenAI(api_key=api_key)

# Create your views here.


def conta_tokens(prompt):
    codificador = tiktoken.encoding_for_model("gpt-3.5-turbo")
    lista_de_tokens = codificador.encode(prompt)
    contagem = len(lista_de_tokens)
    return contagem


def carrega(nome_do_arquivo):
    try:
        with open(nome_do_arquivo, "r") as arquivo:
            dados = arquivo.read()
            return dados
    except IOError as e:
        print(f"Erro no carregamento de arquivo: {e}")


def salva(nome_do_arquivo, conteudo):
    try:
        with open(nome_do_arquivo, "a", encoding="utf-8") as arquivo:
            arquivo.write(conteudo)
    except IOError as e:
        print(f"Erro ao salvar arquivo: {e}")


dados_ecommerce = carrega('dados_ecommerce.txt')
print(conta_tokens(dados_ecommerce))


MAX_RETRIES = 1


def bot(prompt, historico):
    max_retries = MAX_RETRIES
    retries = 0

    while True:
        try:
            # 4000 tokens
            model = 'gpt-3.5-turbo'
            system_prompt = """
            Você é um chatbot de atendimento a clientes de um e-commerce.
            Você não deve responder perguntas que não sejam dados do ecommerce informado!
            ## Dados do ecommerce:
            """ + dados_ecommerce + """
            ## Histórico de conversa:
            """ + historico + """
            """
            tamanho_esperado_saida = 2000
            total_de_tokens_modelo = 4000

            if conta_tokens(system_prompt) >= total_de_tokens_modelo - tamanho_esperado_saida:  # noqa
                model = 'gpt-3.5-turbo-16k'

            query = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                stream=True,
                temperature=1,
                max_tokens=256,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0,
                model=model
            )
            return query

        except Exception as error:
            retries += 1
            if retries >= max_retries:
                return {"error": f"Error in GPT-3: {error}"}
            print(f'Communication error with OpenAI: {error}')
            sleep(1)


def index(request):
    template_name = 'pages/index.html'
    return render(request, template_name)


@csrf_exempt
def chat(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            prompt = data['msg']

            nome_do_arquivo = 'historico.txt'

            historico = ''
            if os.path.exists(nome_do_arquivo):
                historico = carrega(nome_do_arquivo)

            # Process the prompt (replace this with your actual processing logic)
            response = list(trata_resposta(prompt, historico, nome_do_arquivo))

            # Return the result as a JsonResponse
            return JsonResponse({'response': response})

        except json.JSONDecodeError as e:
            return JsonResponse({'error': 'Invalid JSON format'}, status=400)

    # If the request is not a POST request, render a template
    template_name = 'pages/chat.html'
    return render(request, template_name)


def trata_resposta(prompt, historico, nome_do_arquivo):
    resposta_parcial = ''
    for resposta in bot(prompt, historico):
        pedaco_da_resposta = resposta.choices[0].delta.content
        if pedaco_da_resposta is not None and len(pedaco_da_resposta):
            resposta_parcial += pedaco_da_resposta
            yield pedaco_da_resposta
    conteudo = f""" 
    Usuário: {prompt}
    Chatbot: {resposta_parcial}
    """
    salva(nome_do_arquivo, conteudo)
