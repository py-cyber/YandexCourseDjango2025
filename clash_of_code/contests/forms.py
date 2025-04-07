import django.forms

from contests.models import Contest


class ContestForm(django.forms.ModelForm):
    class Meta:
        model = Contest
        fields = [
            Contest.name.field.name,
            Contest.start_time.field.name,
            Contest.end_time.field.name,
            Contest.is_public.field.name,
            Contest.description.field.name,
            Contest.registration_open.field.name,
        ]
        widgets = {
            Contest.start_time.field.name: django.forms.DateTimeInput(
                attrs={'type': 'datetime-local'},
            ),
            Contest.end_time.field.name: django.forms.DateTimeInput(
                attrs={'type': 'datetime-local'},
            ),
        }
