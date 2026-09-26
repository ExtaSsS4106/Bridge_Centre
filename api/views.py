from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from .serializers import RegisterSerializer, UserSerializer
from .models import *
from django.shortcuts import render, redirect, get_object_or_404
from datetime import timedelta
from django.utils import timezone
from django.db.models import Count, Q
import json
from django.urls import reverse
import os
# Регистрация пользователя
class ErrorResponse(APIView):
    permission_classes = (permissions.AllowAny,)
    def get(self, request):
        return Response({"error": "Not found"}, status=404)
    
class RegisterView(generics.CreateAPIView):
    """
    POST /api/register/
    Content-Type: application/json

    {
        "username": "john",
        "password": "StrongPass123!",
        "password2": "StrongPass123!",
        "email": "john@example.com",
        "first_name": "John",
        "last_name": "Doe"
    }
    """
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,) 
    serializer_class = RegisterSerializer
class AmIsuperUser(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        user = request.user
        if user.is_superuser:
            status = True
        else:
            status = False
        return Response({"status_admin": status})
# Получение профиля текущего пользователя
class ProfileView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def put(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProfileInfo(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, user_id):
        profile = get_object_or_404(profiles, user__id=user_id)
        response = {
            "user_id": profile.user.id,
            "profile_id": profile.id,
            "username": profile.user.username,
            "email": profile.user.email,
            "date_joined": profile.user.date_joined,
        }
        return Response(response)

# Логаут (добавляем refresh-токен в чёрный список)
class LogoutView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh_token')
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
class AllUsers(APIView):
    permission_classes = (permissions.AllowAny,)
    def get(self, request):
        profiles_ = profiles.objects.all().order_by('-id')
        response = []
        for p in profiles_:
            response.append({
                                "profile_id": p.id,
                                "username": p.user.username,
                                "user_id": p.user.id,
                            })
        return Response(response)
    
    def post(self, request):
        data = json.loads(request.body)
        query = data.get('query')
        
        if query:
            profiles_ = profiles.objects.filter(user__username__icontains=query).order_by('-id')
        else:
            return Response({"error": "Not found"}, status=404)
        response = []
        for p in profiles_:
            response.append({
                                "profile_id": p.id,
                                "username": p.user.username,
                                "user_id": p.user.id,
                            })
        return Response(response)
    

class GetCards(APIView):
    """
    GET /api/cards/          — список карточек текущего пользователя
    GET /api/cards/?user=ID  — карточки конкретного пользователя
    """
    permission_classes = (permissions.AllowAny,)

    def get(self, request):
        user_id = request.query_params.get('user')

        qs = cards.objects.select_related('user').order_by('-id')
        if user_id:
            qs = qs.filter(user__id=user_id)
        elif request.user.is_authenticated:
            # если залогинен и не указан user — показываем свои
            qs = qs.filter(user=request.user)

        data = [
            {
                "id": c.id,
                "user_id": c.user.id,
                "username": c.user.username,
                "description": c.description,
                "requisites": c.requisites,
            }
            for c in qs
        ]
        return Response({"cards": data})


class EditCard(APIView):
    """
    POST   /api/cards/edit/   — создать карточку (если ещё нет)
    PUT    /api/cards/edit/   — обновить свою карточку
    DELETE /api/cards/edit/   — удалить свою карточку
    """
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        if cards.objects.filter(user=request.user).exists():
            return Response(
                {"error": "У вас уже есть карточка. Используйте PUT для изменения."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        description = request.data.get('description')
        requisites  = request.data.get('requisites')

        if not description or requisites is None:
            return Response(
                {"error": "Поля 'description' и 'requisites' обязательны"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not isinstance(requisites, (dict, list)):
            return Response(
                {"error": "'requisites' должен быть объектом или массивом JSON"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        card = cards.objects.create(
            user=request.user,
            description=description,
            requisites=requisites,
        )

        return Response(
            {
                "message": "Карточка создана",
                "id": card.id,
                "user_id": card.user.id,
                "description": card.description,
                "requisites": card.requisites,
            },
            status=status.HTTP_201_CREATED,
        )

    def put(self, request):
        try:
            card = cards.objects.get(user=request.user)
        except cards.DoesNotExist:
            return Response(
                {"error": "У вас ещё нет карточки. Создайте её через POST."},
                status=status.HTTP_404_NOT_FOUND,
            )

        description = request.data.get('description')
        requisites  = request.data.get('requisites')

        if description is not None:
            card.description = description
        if requisites is not None:
            if not isinstance(requisites, (dict, list)):
                return Response(
                    {"error": "'requisites' должен быть объектом или массивом JSON"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            card.requisites = requisites

        card.save()

        return Response({
            "message": "Карточка обновлена",
            "id": card.id,
            "user_id": card.user.id,
            "description": card.description,
            "requisites": card.requisites,
        })

    def delete(self, request):
        try:
            card = cards.objects.get(user=request.user)
        except cards.DoesNotExist:
            return Response(
                {"error": "Карточка не найдена"},
                status=status.HTTP_404_NOT_FOUND,
            )

        card.delete()
        return Response(
            {"message": "Карточка удалена"},
            status=status.HTTP_204_NO_CONTENT,
        )