from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model


class AdminDashboardTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.User = get_user_model()
        self.admin_user = self.User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass',
        )
        self.regular_user = self.User.objects.create_user(
            username='user',
            email='user@example.com',
            password='userpass',
            currency='GBP',
        )

    def test_admin_dashboard_requires_login(self):
        response = self.client.get(reverse('admindashboard:admin_dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_admin_dashboard_forbidden_for_non_superuser(self):
        self.client.login(username='user', password='userpass')
        response = self.client.get(reverse('admindashboard:admin_dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('payapp:dashboard'))

    def test_admin_dashboard_can_create_admin_user(self):
        self.client.login(username='admin', password='adminpass')
        response = self.client.post(
            reverse('admindashboard:admin_dashboard'),
            {
                'username': 'newadmin',
                'password': 'newadminpass',
                'email': 'newadmin@example.com',
                'currency': 'USD',
            },
        )
        self.assertEqual(response.status_code, 200)
        new_admin = self.User.objects.filter(username='newadmin').first()
        self.assertIsNotNone(new_admin)
        self.assertTrue(new_admin.is_superuser)
        self.assertTrue(new_admin.is_staff)
        self.assertEqual(new_admin.currency, 'USD')
