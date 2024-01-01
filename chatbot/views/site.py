
import json
import os
from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from .chatbot import carrega, trata_resposta


@login_required(login_url='accounts:login', redirect_field_name='next')
def index(request):
    template_name = 'pages/index.html'
    return render(request, template_name)


@csrf_exempt
def chat(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            prompt = data['msg']

            nome_do_arquivo = request.user.username + '.txt'
            print(nome_do_arquivo)

            historico = ''
            if os.path.exists(nome_do_arquivo):
                historico = carrega(nome_do_arquivo)

            # Process the prompt (replace this with your actual processing logic) #noqua
            response = list(trata_resposta(prompt, historico, nome_do_arquivo))

            # Return the result as a JsonResponse
            return JsonResponse({'response': response})

        except json.JSONDecodeError:  # noqua
            return JsonResponse({'error': 'Invalid JSON format'}, status=400)

    # If the request is not a POST request, render a template
    template_name = 'pages/index.html'
    return render(request, template_name)


@csrf_exempt
def limpar_historico(request):
    nome_do_arquivo = request.user.username + '.txt'
    if os.path.exists(nome_do_arquivo):
        os.remove(nome_do_arquivo)
    return JsonResponse({'response': 'Histórico apagado!'})
