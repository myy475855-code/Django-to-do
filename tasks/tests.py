from rest_framework.test import APITestCase

class TaskAPITests(APITestCase):
    def auth(self, name):
        self.client.post('/api/auth/register/', {'username': name, 'password': 'S3cure-pass-91'})
        r = self.client.post('/api/auth/token/', {'username': name, 'password': 'S3cure-pass-91'})
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + r.data['access'])

    def test_requires_auth(self):
        self.assertEqual(self.client.get('/api/tasks/').status_code, 401)

    def test_crud_and_isolation(self):
        self.auth('alice')
        r = self.client.post('/api/tasks/', {'title': 'Write docs'})
        self.assertEqual(r.status_code, 201)
        tid = r.data['id']
        self.assertEqual(self.client.patch(f'/api/tasks/{tid}/', {'completed': True}).status_code, 200)
        self.auth('bob')
        self.assertEqual(self.client.get(f'/api/tasks/{tid}/').status_code, 404)
        self.assertEqual(self.client.get('/api/tasks/').data['count'], 0)
        self.auth('alice')
        self.assertEqual(self.client.delete(f'/api/tasks/{tid}/').status_code, 204)

    def test_fields_stats_clear(self):
        self.auth('carol')
        self.client.post('/api/tasks/', {'title': 'a', 'priority': 3, 'due_date': '2000-01-01', 'category': 'Work'})
        self.client.post('/api/tasks/', {'title': 'b', 'completed': True})
        s = self.client.get('/api/tasks/stats/').data
        self.assertEqual((s['total'], s['done'], s['overdue']), (2, 1, 1))
        self.assertEqual(self.client.get('/api/tasks/?priority=3').data['count'], 1)
        self.assertEqual(self.client.get('/api/tasks/?search=work').data['count'], 1)
        self.assertEqual(self.client.post('/api/tasks/clear_completed/').data['deleted'], 1)
