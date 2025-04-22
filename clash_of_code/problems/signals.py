from django.db.models.signals import pre_save
from django.dispatch import receiver

import problems.models


@receiver(pre_save, sender=problems.models.Problem)
def check_update_author_solution(sender, instance, **kwargs):
    if instance.pk:
        old_author_solution = problems.models.Problem.objects.get(pk=instance.pk).author_solution

        if old_author_solution != instance.author_solution:
            instance.is_correct = False
