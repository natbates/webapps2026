from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model


class LoginTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.User = get_user_model()
        self.user = self.User.objects.create_user(
            username='alice',
            email='alice@example.com',
            password='pass123',
            currency='GBP',
        )

    def test_login_page_renders(self):
        response = self.client.get(reverse('login:login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Login')

    def test_login_with_valid_credentials(self):
        response = self.client.post(
            reverse('login:login'),
            {'username': 'alice', 'password': 'pass123'},
        )
        self.assertIn(response.status_code, (302, 301))
        self.assertEqual(int(self.client.session['_auth_user_id']), self.user.pk)

    def test_logout_redirects_home(self):
        self.client.login(username='alice', password='pass123')
        response = self.client.get(reverse('login:logout'))
        self.assertIn(response.status_code, (302, 301))
        self.assertEqual(response.url, '/')
