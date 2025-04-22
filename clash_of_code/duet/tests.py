import http

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from duet.models import CodeRoom, ProgrammingLanguage, RoomInvitation

User = get_user_model()


class BaseDuetTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user1 = User.objects.create_user(
            username='user1',
            email='user1@test.com',
            password='testpass123',
        )
        cls.user2 = User.objects.create_user(
            username='user2',
            email='user2@test.com',
            password='testpass123',
        )
        cls.language = cls.create_programming_language()

    @classmethod
    def create_programming_language(cls):
        return ProgrammingLanguage.objects.create(name='python', ace_mode='python')


class ModelTests(BaseDuetTest):
    def test_room_creation(self):
        room = CodeRoom.objects.create(
            name='Test Room',
            language=self.language,
            owner=self.user1,
        )
        room.participants.add(self.user1.id)

        self.assertEqual(str(room), 'Test Room (python)')
        self.assertEqual(room.owner, self.user1)
        self.assertTrue(self.user1 in room.participants.all())

    def test_invitation_creation(self):
        room = CodeRoom.objects.create(
            name='Test Room',
            language=self.language,
            owner=self.user1,
        )
        invitation = RoomInvitation.objects.create(
            room=room,
            inviter=self.user1,
            invitee=self.user2,
        )

        self.assertEqual(str(invitation), 'Invite to Test Room (python) for user2')
        self.assertFalse(invitation.is_accepted)


class ViewTests(BaseDuetTest):
    def setUp(self):
        self.client = Client()
        self.room = CodeRoom.objects.create(
            name='Test Room',
            language=self.language,
            owner=self.user1,
        )
        self.room.participants.add(self.user1.id)

    def test_room_create_view(self):
        self.client.login(username='user1', password='testpass123')
        response = self.client.post(
            reverse('duet:create_room'),
            {'name': 'New Room', 'language': self.language.id},
        )

        self.assertRedirects(
            response,
            reverse('duet:room_detail', kwargs={'pk': 2}),
        )
        self.assertTrue(CodeRoom.objects.filter(name='New Room').exists())

    def test_room_detail_view(self):
        self.client.login(username='user1', password='testpass123')
        response = self.client.get(
            reverse('duet:room_detail', kwargs={'pk': self.room.pk}),
        )
        self.assertEqual(response.status_code, http.HTTPStatus.OK)
        self.assertContains(response, 'Test Room')

    def test_room_delete_view(self):
        self.client.login(username='user1', password='testpass123')
        response = self.client.post(
            reverse('duet:room_delete', kwargs={'pk': self.room.pk}),
        )
        self.assertEqual(response.status_code, http.HTTPStatus.FOUND)
        self.assertFalse(CodeRoom.objects.filter(pk=self.room.pk).exists())
