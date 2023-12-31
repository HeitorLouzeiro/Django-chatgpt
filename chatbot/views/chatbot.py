import os
from time import sleep

import tiktoken
from openai import OpenAI

from .resumidor import criando_resumo

# Set OpenAI API key
api_key = os.environ.get('OPENAI_API_KEY')
client = OpenAI(api_key=api_key)


# Conta o número de tokens de uma string
def conta_tokens(prompt):
    codificador = tiktoken.encoding_for_model("gpt-3.5-turbo")
    lista_de_tokens = codificador.encode(prompt)
    contagem = len(lista_de_tokens)
    return contagem

# Carrega um arquivo de texto e retorna seu conteúdo


def carrega(nome_do_arquivo):
    try:
        with open(nome_do_arquivo, "r") as arquivo:
            dados = arquivo.read()
            return dados
    except IOError as e:
        print(f"Erro no carregamento de arquivo: {e}")

# Salva um arquivo de texto com o conteúdo informado


def salva(nome_do_arquivo, conteudo):
    try:
        # w = write (escrita)
        with open(nome_do_arquivo, "w", encoding="utf-8") as arquivo:
            arquivo.write(conteudo)
    except IOError as e:
        print(f"Erro ao salvar arquivo: {e}")


dados_ecommerce = carrega('dados_ecommerce.txt')


def bot(prompt, historico):
    max_retries = 1
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


def trata_resposta(prompt, historico, nome_do_arquivo):
    resposta_parcial = ''
    historico_resumido = criando_resumo(historico)
    for resposta in bot(prompt, historico_resumido):
        pedaco_da_resposta = resposta.choices[0].delta.content
        if pedaco_da_resposta is not None and len(pedaco_da_resposta):
            resposta_parcial += pedaco_da_resposta
            yield pedaco_da_resposta
    conteudo = f""" 
    Histórico: {historico_resumido}
    Usuário: {prompt}
    Chatbot: {resposta_parcial}
    """
    salva(nome_do_arquivo, conteudo)
