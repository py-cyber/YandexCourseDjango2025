import django.forms

import problems.models


class FormControlMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_bootstrap_class()

    def add_bootstrap_class(self):
        for field in self.visible_fields():
            if not isinstance(field.field.widget, django.forms.CheckboxInput):
                field.field.widget.attrs['class'] = 'form-control'
            else:
                field.field.widget.attrs['class'] = 'form-check-input'


class ProblemsForm(FormControlMixin, django.forms.ModelForm):
    class Meta:
        model = problems.models.Problem

        fields = (
            problems.models.Problem.title.field.name,
            problems.models.Problem.description.field.name,
            problems.models.Problem.difficult.field.name,
            problems.models.Problem.is_public.field.name,
            problems.models.Problem.auther_solution.field.name,
            problems.models.Problem.auther_language.field.name,
            problems.models.Problem.input_format.field.name,
            problems.models.Problem.output_format.field.name,
            problems.models.Problem.time_limit.field.name,
            problems.models.Problem.memory_limit.field.name,
        )
