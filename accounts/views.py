from django.contrib import auth, messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render


# Create your views here.
def login(request):
    template_name = 'accounts/pages/login.html'
    if request.method != 'POST':
        return render(request, template_name)

    username = request.POST.get('username')
    password = request.POST.get('password')

    user = auth.authenticate(request, username=username, password=password)

    if not user:
        messages.error(request, 'Invalid username or password')
        return render(request, template_name)

    else:
        auth.login(request, user)
        return redirect('chatbot:index')


@login_required(login_url='accounts:login', redirect_field_name='next')
def logout(request):
    auth.logout(request)
    return redirect('accounts:login')
