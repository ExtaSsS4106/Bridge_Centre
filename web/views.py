from django.contrib.auth.decorators import login_required
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib import messages  
from django.shortcuts import render, redirect, get_object_or_404  
from .forms import RegisterForm
from django.shortcuts import render

# Create your views here.
"""Рендер первой страницы"""
def index(request):
    return render(request, 'main/index.html')



"""Выход из аккаунта"""
@login_required(login_url='/login/')
def logout_view(request):
    auth_logout(request)
    return redirect('login')


"""Вход в аккаунт"""
def login_view(request):
    if request.method == 'POST':
        from django.contrib.auth import authenticate
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect('index')
        else:
            messages.error(request, 'Неверный логин или пароль')
    return render(request, 'registration/login.html')


"""Регистрация"""
def sign_up(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('index')
    else:
        form = RegisterForm()
    return render(request, 'registration/reg.html', {"form": form})



def get_cards(request):
    pass