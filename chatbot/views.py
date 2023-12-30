import json
import os
from time import sleep

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from openai import OpenAI

# Set OpenAI API key
api_key = os.environ.get('OPENAI_API_KEY')
client = OpenAI(api_key=api_key)

# Create your views here.


MAX_RETRIES = 1


def bot(prompt):
    max_retries = MAX_RETRIES
    retries = 0

    while True:
        try:
            model = 'gpt-3.5-turbo'
            system_prompt = """
            Você é um chatbot de atendimento a clientes de um e-commerce.
            Você não deve responder perguntas que não sejam dados do ecommerce informado!
            """

            query = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=1,
                max_tokens=256,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0,
                model=model
            )
            response = query.choices[0].message.content
            return response

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
            response = bot(prompt=prompt)

            # Return a JSON response
            return JsonResponse({'response': response})

        except json.JSONDecodeError as e:
            return JsonResponse({'error': 'Invalid JSON format'}, status=400)

    template_name = 'pages/chat.html'
    return render(request, template_name)
