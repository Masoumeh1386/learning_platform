from django.test import TestCase
from django.contrib.auth.models import User
from .models import Profile


class ProfileTest(TestCase):

    def test_profile_created_automatically(self):
        user = User.objects.create_user(username='newuser', password='12345')
        self.assertTrue(Profile.objects.filter(user=user).exists())

    def test_profile_str(self):
        user = User.objects.create_user(username='testuser', password='12345')
        self.assertEqual(str(user.profile), 'پروفایل testuser')