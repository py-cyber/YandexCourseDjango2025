import json

from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, View

from duet.models import CodeRoom, ProgrammingLanguage, RoomInvitation


class CodeRoomCreateView(LoginRequiredMixin, CreateView):
    model = CodeRoom
    fields = ['name', 'language']
    template_name = 'duet/create_room.html'

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['language'].queryset = ProgrammingLanguage.objects.all()
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['languages'] = ProgrammingLanguage.objects.all()
        return context

    def form_valid(self, form):
        form.instance.owner = self.request.user
        response = super().form_valid(form)
        self.object.participants.add(self.request.user.id)
        return response

    def get_success_url(self):
        return reverse_lazy('room_detail', kwargs={'pk': self.object.pk})


class CodeRoomDetailView(LoginRequiredMixin, DetailView):
    model = CodeRoom
    template_name = 'duet/room.html'
    context_object_name = 'room'

    def get_queryset(self):
        return super().get_queryset().filter(participants=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['languages'] = ProgrammingLanguage.objects.all()
        context['other_user'] = (
            self.get_object().participants.exclude(id=self.request.user.id).first()
        )
        return context


class UserRoomsListView(LoginRequiredMixin, ListView):
    model = CodeRoom
    template_name = 'duet/user_rooms.html'
    context_object_name = 'rooms'

    def get_queryset(self):
        return super().get_queryset().filter(participants=self.request.user)


class RoomInviteCreateView(LoginRequiredMixin, CreateView):
    model = RoomInvitation
    fields = ['invitee']
    template_name = 'duet/invite_user.html'

    def dispatch(self, request, *args, **kwargs):
        self.room = get_object_or_404(
            CodeRoom,
            pk=self.kwargs['room_id'],
            owner=request.user,
        )
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.room = self.room
        form.instance.inviter = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['room'] = self.room

        user = get_user_model()

        current_participants = self.room.participants.all()

        invited_users = user.objects.filter(
            received_invites__room=self.room,
            received_invites__is_accepted=False,
        )

        context['users'] = (
            user.objects.exclude(id=self.request.user.id)
            .exclude(id__in=current_participants.values_list('id', flat=True))
            .exclude(id__in=invited_users.values_list('id', flat=True))
        )

        return context

    def get_success_url(self):
        return reverse_lazy('room_detail', kwargs={'pk': self.room.pk})


class InvitationsListView(LoginRequiredMixin, ListView):
    model = RoomInvitation
    template_name = 'duet/invitations_list.html'
    context_object_name = 'invitations'

    def get_queryset(self):
        return RoomInvitation.objects.filter(
            invitee=self.request.user,
            is_accepted=False,
        )


class AcceptInvitationView(LoginRequiredMixin, View):
    def get(self, request, invitation_id):
        invitation = get_object_or_404(
            RoomInvitation,
            id=invitation_id,
            invitee=request.user,
            is_accepted=False,
        )

        invitation.room.participants.add(request.user.id)

        invitation.is_accepted = True
        invitation.save()

        return redirect('room_detail', pk=invitation.room.id)


class CodeRoomSaveView(LoginRequiredMixin, View):
    def post(self, request, pk):
        try:
            data = json.loads(request.body)
            content = data.get('content', '')

            room = get_object_or_404(CodeRoom, pk=pk, participants=request.user)
            room.content = content
            room.save()

            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
