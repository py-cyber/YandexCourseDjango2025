import django.forms
from tinymce.widgets import TinyMCE

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
            problems.models.Problem.author_solution.field.name,
            problems.models.Problem.author_language.field.name,
            problems.models.Problem.input_format.field.name,
            problems.models.Problem.output_format.field.name,
            problems.models.Problem.time_limit.field.name,
            problems.models.Problem.memory_limit.field.name,
            problems.models.Problem.tags.field.name,
        )

        widgets = {
            problems.models.Problem.description.field.name: TinyMCE(),
            problems.models.Problem.input_format.field.name: TinyMCE(),
            problems.models.Problem.output_format.field.name: TinyMCE(),
        }


class TestForm(django.forms.ModelForm):
    pk = django.forms.IntegerField(min_value=0, required=False)

    class Meta:
        model = problems.models.TestCase
        fields = (
            problems.models.TestCase.is_sample.field.name,
            problems.models.TestCase.number.field.name,
            problems.models.TestCase.input_data.field.name,
            problems.models.TestCase.output_data.field.name,
        )
