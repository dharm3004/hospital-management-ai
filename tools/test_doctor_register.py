from django.test import Client
from django.contrib.auth.models import User

c = Client()
data = {
    'username': 'doc_test_auto',
    'email': 'doc_test_auto@example.com',
    'first_name': 'Alice',
    'last_name': 'Smith',
    'password1': 'AutoPass123!',
    'password2': 'AutoPass123!',
    'license_number': 'AUTO12345',
    'specialization': 'Cardiology'
}

resp = c.post('/auth/doctor/register/', data)
print('STATUS', resp.status_code)
print('CONTENT', resp.content.decode('utf-8', errors='ignore'))

try:
    u = User.objects.get(username='doc_test_auto')
    print('USER_FOUND', u.username, u.first_name, u.last_name, u.email)
except Exception as e:
    print('USER_NOT_CREATED', e)
