from django.core.exceptions import ValidationError
import django.forms

import problems.models


class ProblemForm(django.forms.ModelForm):
    class Meta:
        model = problems.models.Problem
        fields = [
            problems.models.Problem.title.field.name,
            problems.models.Problem.description.field.name,
            problems.models.Problem.difficult.field.name,
            problems.models.Problem.time_limit.field.name,
            problems.models.Problem.memory_limit.field.name,
            problems.models.Problem.is_public.field.name,
        ]
        widgets = {
            problems.models.Problem.title.field.name: django.forms.TextInput(
                attrs={'class': 'form-control'},
            ),
            problems.models.Problem.description.field.name: django.forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 5,
                },
            ),
            problems.models.Problem.difficult.field.name: django.forms.Select(
                attrs={'class': 'form-select'},
            ),
            problems.models.Problem.time_limit.field.name: django.forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'min': 1,
                    'max': 10,
                },
            ),
            problems.models.Problem.memory_limit.field.name: django.forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'min': 64,
                    'max': 1024,
                },
            ),
            problems.models.Problem.is_public.field.name: django.forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input',
                },
            ),
        }
        labels = {
            problems.models.Problem.is_public.field.name: 'Публичная задача',
        }
        help_texts = {
            problems.models.Problem.time_limit.field.name: 'В секундах (1-10)',
            problems.models.Problem.memory_limit.field.name: 'В мегабайтах (64-1024)',
        }

    def clean_time_limit(self):
        time_limit = self.cleaned_data['time_limit']
        if time_limit < 1 or time_limit > 10:
            raise ValidationError('Лимит времени должен быть между 1 и 10 секундами')

        return time_limit

    def clean_memory_limit(self):
        memory_limit = self.cleaned_data['memory_limit']
        if memory_limit < 64 or memory_limit > 1024:
            raise ValidationError('Лимит памяти должен быть между 64 и 1024 MB')

        return memory_limit

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.visible_fields():
            if not isinstance(field.field.widget, django.forms.CheckboxInput):
                field.field.widget.attrs['class'] = 'form-control'
