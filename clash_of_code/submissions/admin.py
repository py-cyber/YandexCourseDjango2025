import django.contrib.admin

import submissions.models


@django.contrib.admin.register(submissions.models.Submission)
class SubmissionAdmin(django.contrib.admin.ModelAdmin):
    list_display = (
        'problem_name',
        'user_name',
        submissions.models.Submission.verdict.field.name,
        submissions.models.Submission.test_error.field.name,
    )

    @django.contrib.admin.display(empty_value='???')
    def problem_name(self, obj):
        return obj.problem.title[:20]

    @django.contrib.admin.display(empty_value='???')
    def user_name(self, obj):
        return obj.user.username[:20]
