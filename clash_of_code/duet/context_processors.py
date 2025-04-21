from duet.models import RoomInvitation


def invitations_count(request):
    if request.user.is_authenticated:
        count = RoomInvitation.objects.filter(
            invitee=request.user,
            is_accepted=False,
        ).count()
        return {'invitations_count': count}

    return {'invitations_count': 0}
