from django.core.exceptions import ValidationError
import django.forms

import contests.models
import problems.models


class ContestForm(django.forms.ModelForm):
    class Meta:
        model = contests.models.Contest
        fields = [
            contests.models.Contest.name.field.name,
            contests.models.Contest.start_time.field.name,
            contests.models.Contest.end_time.field.name,
            contests.models.Contest.is_public.field.name,
            contests.models.Contest.description.field.name,
            contests.models.Contest.registration_open.field.name,
        ]
        widgets = {
            contests.models.Contest.start_time.field.name: django.forms.DateTimeInput(
                attrs={'type': 'datetime-local'},
            ),
            contests.models.Contest.end_time.field.name: django.forms.DateTimeInput(
                attrs={'type': 'datetime-local'},
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.visible_fields():
            if not isinstance(field.field.widget, django.forms.CheckboxInput):
                field.field.widget.attrs['class'] = 'form-control'
            else:
                field.field.widget.attrs['class'] = 'form-check-input'


class AddProblemToContestForm(django.forms.ModelForm):
    problem = django.forms.ModelChoiceField(
        queryset=problems.models.Problem.objects.all(),
        required=False,
        widget=django.forms.Select(attrs={'class': 'form-select'}),
    )
    new_problem = django.forms.BooleanField(
        required=False,
        initial=False,
        label='Создать новую задачу',
    )
    show_only_mine = django.forms.BooleanField(
        required=False,
        initial=False,
        label='Мои задачи',
        widget=django.forms.CheckboxInput(attrs={
            'onchange': 'filterProblems(this)'
        })
    )

    class Meta:
        model = contests.models.ContestProblem
        fields = [
            'problem',
            'new_problem',
            contests.models.ContestProblem.points.field.name,
            contests.models.ContestProblem.order.field.name,
        ]
        widgets = {
            contests.models.ContestProblem.points.field.name: django.forms.NumberInput(
                attrs={'class': 'form-control'},
            ),
            contests.models.ContestProblem.order.field.name: django.forms.NumberInput(
                attrs={'class': 'form-control'},
            ),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if self.user:
            self.fields['problem'].queryset = problems.models.Problem.objects.filter(
                django.db.models.Q(author=self.user) | django.db.models.Q(is_public=True)
            ).order_by('title')
        for field in self.visible_fields():
            if not isinstance(field.field.widget, django.forms.CheckboxInput):
                field.field.widget.attrs['class'] = 'form-control'
            else:
                field.field.widget.attrs['class'] = 'form-check-input'

    def clean(self):
        cleaned_data = super().clean()
        new_problem = cleaned_data.get('new_problem')
        problem = cleaned_data.get('problem')

        if not hasattr(self, 'contest') or not self.contest:
            raise ValidationError('Контест не указан')

        if contests.models.ContestProblem.objects.filter(
            contest=self.contest,
            problem=cleaned_data.get('problem'),
        ).exists():
            raise django.forms.ValidationError('Эта задача уже добавлена в контест')

        if not new_problem and not problem:
            raise django.forms.ValidationError(
                'Выберите существующую задачу или создайте новую',
            )

        return cleaned_data
