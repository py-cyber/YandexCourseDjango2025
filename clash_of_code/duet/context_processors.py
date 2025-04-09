from duet.models import RoomInvitation


def invitations_count(request):
    if request.user.is_authenticated:
        return {
            'unaccepted_invites_count': RoomInvitation.objects.filter(
                invitee=request.user,
                is_accepted=False,
            ).count(),
        }

    return {}
