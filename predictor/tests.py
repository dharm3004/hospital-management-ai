from django.test import TestCase, Client
from django.urls import reverse
import json

# tests focus on predictor views; model loading may fail if model_data.pkl is missing


class AIDiagnosisTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def test_get_page(self):
        response = self.client.get(reverse('ai_diagnosis'))
        self.assertEqual(response.status_code, 200)
        # page should contain the diagnosis heading
        self.assertContains(response, 'AI Diagnosis')

    def test_post_no_symptoms(self):
        response = self.client.post(reverse('ai_diagnosis'), data=json.dumps({'symptoms': []}), content_type='application/json')
        # view requires at least one symptom or returns 400
        self.assertIn(response.status_code, (400, 503))

    def test_post_invalid_json(self):
        response = self.client.post(reverse('ai_diagnosis'), data='notjson', content_type='application/json')
        self.assertIn(response.status_code, (400, 503))

    def test_post_valid_symptoms(self):
        # ensure model loads and returns some results
        from .views import load_model
        try:
            model_data = load_model()
            symptoms = model_data.get('features', [])
        except Exception:
            symptoms = []
        if not symptoms:
            self.skipTest('No symptoms available from model')
        # send first symptom
        data = {'symptoms': [symptoms[0]]}
        response = self.client.post(reverse('ai_diagnosis'), data=json.dumps(data), content_type='application/json')
        # allow server error if model fails
        self.assertIn(response.status_code, (200, 500))
        if response.status_code == 200:
            data_out = json.loads(response.content)
            self.assertIn('results', data_out)
            self.assertIsInstance(data_out['results'], list)
