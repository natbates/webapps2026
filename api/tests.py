from django.test import TestCase, Client
from django.urls import reverse


class ConversionAPITests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_conversion_success(self):
        url = reverse('api:conversion', args=['GBP', 'USD', '100'])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn('rate', data)
        self.assertIn('converted_amount', data)
        # rate for GBP->USD is expected to be a positive number
        self.assertGreater(float(data['rate']), 0)

    def test_conversion_unsupported(self):
        url = reverse('api:conversion', args=['XXX', 'USD', '10'])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)
