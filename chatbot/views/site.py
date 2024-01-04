
import json
import os

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt

from .chatbot import carrega, trata_resposta


@login_required(login_url='accounts:login', redirect_field_name='next')
def index(request):
    template_name = 'pages/index.html'
    return render(request, template_name)


@login_required(login_url='accounts:login', redirect_field_name='next')
@csrf_exempt
def chat(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        prompt = data['msg']

        nome_do_arquivo = request.user.username

        historico = ''
        if os.path.exists(nome_do_arquivo):
            historico = carrega(nome_do_arquivo)

        response = list(trata_resposta(prompt, historico, nome_do_arquivo))

        # Return the result as a JsonResponse
        return JsonResponse({'response': response})
    else:
        return redirect('chatbot:index')


@login_required(login_url='accounts:login', redirect_field_name='next')
@csrf_exempt
def limpar_historico(request):
    nome_do_arquivo = request.user.username
    if os.path.exists(nome_do_arquivo):
        os.remove(nome_do_arquivo)
    return JsonResponse({'response': 'Histórico apagado!'})
