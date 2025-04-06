import django.conf
import django.core.validators
import django.db.models
from django.utils.translation import gettext_lazy as _
import tinymce.models


class LanguageChoices(django.db.models.TextChoices):
    Python_3_11 = 'Py3.11', 'Python 3.11'


class Tag(django.db.models.Model):
    name = django.db.models.CharField(
        verbose_name=_('name'),
        max_length=75,
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('tag')
        verbose_name_plural = _('tags')


class Task(django.db.models.Model):
    name = django.db.models.CharField(
        verbose_name=_('name'),
        max_length=75,
    )

    author = django.db.models.ForeignKey(
        django.conf.settings.AUTH_USER_MODEL,
        verbose_name=_('author'),
        on_delete=django.db.models.CASCADE,
        related_name='tasks',
    )

    description = tinymce.models.HTMLField(
        verbose_name=_('description'),
        help_text=_('Explain the idea of the task'),
        max_length=8000,
    )

    input_format = tinymce.models.HTMLField(
        verbose_name=_('input data format'),
        help_text=_('Input data format'),
        max_length=1000,
    )

    output_format = tinymce.models.HTMLField(
        verbose_name=_('output data format'),
        help_text=_('Output data format'),
        max_length=1000,

    )

    is_public = django.db.models.BooleanField(
        verbose_name=_('is public'),
        help_text=_(
            'If you open the task for public access, other users will be able to add'
            ' it to their contests, and moderation will be able to evaluate it and add'
            ' it to the general pool of tasks',
        ),
        default=False,
    )

    difficult = django.db.models.PositiveIntegerField(
        verbose_name=_('difficult'),
        help_text=_('Assess the complexity of your task'),
        validators=[
            django.core.validators.MaxValueValidator(100),
        ],
    )

    auther_solution = django.db.models.TextField(
        verbose_name=_('author solution'),
        help_text=_(
            "The author's solution is to take a long time to pass all the tests",
        ),
        max_length=8000,
    )

    auther_language = django.db.models.TextField(
        verbose_name=_('author language'),
        choices=LanguageChoices,
    )

    tags = django.db.models.ManyToManyField(
        Tag,
        verbose_name=_('tags'),
        blank=True,
        related_name='tasks',
    )

    def clean(self):
        # TODO когда будет тест система нужно проверить
        # авторское решение перед сейвом и добавлением теста
        pass

    def __str__(self):
        return self.name[:20]

    class Meta:
        verbose_name = _('task')
        verbose_name_plural = _('tasks')


class TestCase(django.db.models.Model):
    task = django.db.models.ForeignKey(
        Task,
        verbose_name=_('task'),
        on_delete=django.db.models.CASCADE,
        related_name='tests',
    )

    visible = django.db.models.BooleanField(
        verbose_name=_('visible'),
        help_text=_('If True, then this test will be shown as an example.'),
        default=False,
    )

    input_data = django.db.models.TextField(
        verbose_name=_('input data'),
        help_text=_(
            'Input data for the test. It will be passed '
            'to the program during execution via the standard stream',
        ),
        max_length=10000000,
    )

    output_data = django.db.models.TextField(
        verbose_name=_('output data'),
        help_text=_(
            'Test output. The program should output exactly this text in this format',
        ),
        max_length=10000000,
    )

    def __str__(self):
        return self.task.name[:20]

    class Meta:
        verbose_name = _('test case')
        verbose_name_plural = _('tests cases')


class StatusChoice(django.db.models.TextChoices):
    OK = 'OK', 'OK'
    Compilation_error = 'CE', _('Compilation error')
    Wrong_answer = 'WA', _('Wrong answer')
    Time_limit = 'TL', _('Time limit')
    Memory_limit = 'ML', _('Memory limit')
    In_queue = 'IQ', _('In queue')
    In_processing = 'IP', _('In processing')


class Solution(django.db.models.Model):
    task = django.db.models.ForeignKey(
        Task,
        on_delete=django.db.models.CASCADE,
        verbose_name=_('task'),
        related_name='solutions',
    )

    user = django.db.models.ForeignKey(
        django.conf.settings.AUTH_USER_MODEL,
        on_delete=django.db.models.CASCADE,
        verbose_name=_('author'),
        related_name=_('solutions'),
    )

    code = django.db.models.TextField(
        verbose_name=_('code'),
        max_length=8000,
    )

    lang = django.db.models.TextField(
        verbose_name=_('programming language'),
        choices=LanguageChoices,
    )

    status = django.db.models.TextField(
        verbose_name=_('status'),
        choices=StatusChoice,
    )

    test_error = django.db.models.ForeignKey(
        TestCase,
        null=True,
        on_delete=django.db.models.SET_NULL,
        default=None,
    )

    dispatch_date = django.db.models.DateTimeField(
        verbose_name=_('dispatch date'),
        auto_now_add=True,
    )

    def __str__(self):
        return f'{self.lang} {self.task.name[:20]}'

    class Meta:
        verbose_name = _('solution')
        verbose_name_plural = _('solutions')
