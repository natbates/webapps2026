from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model


class RegisterTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.User = get_user_model()

    def test_register_creates_user(self):
        url = reverse('register:register')
        data = {
            'username': 'alice',
            'first_name': 'Alice',
            'last_name': 'Example',
            'email': 'alice@example.com',
            'password1': 'safepassword123',
            'password2': 'safepassword123',
            'currency': 'GBP',
        }
        resp = self.client.post(url, data)
        # successful registration redirects to the payments dashboard
        self.assertIn(resp.status_code, (302, 301))
        user = self.User.objects.filter(username='alice').first()
        self.assertIsNotNone(user)
        self.assertEqual(user.email, 'alice@example.com')
        self.assertEqual(user.currency, 'GBP')
