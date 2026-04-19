from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model


class RegisterTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.User = get_user_model()

    def test_register_page_renders(self):
        response = self.client.get(reverse('register:register'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Create account')

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
        self.assertIn(resp.status_code, (302, 301))
        self.assertEqual(resp.url, '/payments/')
        user = self.User.objects.filter(username='alice').first()
        self.assertIsNotNone(user)
        self.assertEqual(user.email, 'alice@example.com')
        self.assertEqual(user.currency, 'GBP')

    def test_register_rejects_password_mismatch(self):
        url = reverse('register:register')
        data = {
            'username': 'bob',
            'first_name': 'Bob',
            'last_name': 'Example',
            'email': 'bob@example.com',
            'password1': 'pass1',
            'password2': 'pass2',
            'currency': 'EUR',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertIn("The two password fields didn’t match.", response.content.decode())
        self.assertFalse(self.User.objects.filter(username='bob').exists())
