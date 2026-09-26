from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from api.models import profiles
import json
from api.models import cards

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        
        if commit:
            user.save()  
        
        profiles.objects.update_or_create(user=user)
        
        return user

class CardForm(forms.ModelForm):
    class Meta:
        model = cards
        fields = ('description', 'requisites')
        widgets = {
            'description': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Например: карта лояльности клиента',
                'class': 'form-input',
            }),
        }

    def clean_requisites(self):
        """Принимаем либо dict, либо строку JSON — приводим к dict."""
        data = self.cleaned_data['requisites']

        if isinstance(data, (dict, list)):
            return data

        if isinstance(data, str):
            data = data.strip()
            if not data:
                raise forms.ValidationError('Реквизиты не могут быть пустыми')
            try:
                parsed = json.loads(data)
            except json.JSONDecodeError:
                raise forms.ValidationError('Некорректный JSON')
            if not isinstance(parsed, (dict, list)):
                raise forms.ValidationError('JSON должен быть объектом или массивом')
            return parsed

        raise forms.ValidationError('Некорректный формат реквизитов')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # если редактируем — покажем JSON строкой в textarea
        if self.instance and self.instance.pk and isinstance(self.instance.requisites, (dict, list)):
            self.initial['requisites'] = json.dumps(
                self.instance.requisites, ensure_ascii=False, indent=2
            )
        self.fields['requisites'] = forms.CharField(
            required=True,
            widget=forms.Textarea(attrs={
                'rows': 6,
                'placeholder': '{"bank": "Сбербанк", "number": "1234 5678 9012 3456"}',
                'class': 'form-input',
            }),
            label='Реквизиты (JSON)',
        )