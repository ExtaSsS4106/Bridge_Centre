from django.contrib.auth.decorators import login_required
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib import messages  
from django.shortcuts import render, redirect, get_object_or_404  
from .forms import RegisterForm, CardForm
from django.shortcuts import render

import json
from django.views.decorators.http import require_http_methods
from api.models import cards

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



# ---------- Своя карточка ----------
@login_required(login_url='/login/')
def my_card(request):
    """Показать свою карточку или предложить создать."""
    card = cards.objects.filter(user=request.user).first()
    return render(request, 'cards/my_card.html', {
        'card': card,
        'requisites_pretty': json.dumps(card.requisites, ensure_ascii=False, indent=2)
                             if card else None,
    })


# ---------- Создать ----------
@login_required(login_url='/login/')
def card_create(request):
    if cards.objects.filter(user=request.user).exists():
        messages.info(request, 'У вас уже есть карточка — отредактируйте её.')
        return redirect('my_card')

    if request.method == 'POST':
        form = CardForm(request.POST)
        if form.is_valid():
            card = form.save(commit=False)
            card.user = request.user           # жёстко владелец = текущий
            card.save()
            messages.success(request, 'Карточка создана')
            return redirect('my_card')
    else:
        form = CardForm()

    return render(request, 'cards/card_form.html', {
        'form': form,
        'title': 'Создание карточки',
        'submit_label': 'Создать',
    })


# ---------- Редактировать ----------
@login_required(login_url='/login/')
def card_edit(request):
    card = get_object_or_404(cards, user=request.user)   # только своя

    if request.method == 'POST':
        form = CardForm(request.POST, instance=card)
        if form.is_valid():
            form.save()
            messages.success(request, 'Карточка обновлена')
            return redirect('my_card')
    else:
        form = CardForm(instance=card)

    return render(request, 'cards/card_form.html', {
        'form': form,
        'title': 'Редактирование карточки',
        'submit_label': 'Сохранить',
    })


# ---------- Удалить ----------
@login_required(login_url='/login/')
@require_http_methods(['POST'])          # удаление только через POST
def card_delete(request):
    card = get_object_or_404(cards, user=request.user)
    card.delete()
    messages.success(request, 'Карточка удалена')
    return redirect('my_card')


# ---------- Чужая карточка (только чтение) ----------
def card_view(request, user_id):
    card = get_object_or_404(cards, user__id=user_id)
    return render(request, 'cards/card_view.html', {
        'card': card,
        'requisites_pretty': json.dumps(card.requisites, ensure_ascii=False, indent=2),
        'is_owner': request.user.is_authenticated and request.user.id == card.user_id,
    })