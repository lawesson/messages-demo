from rest_framework.test import APITestCase, APITransactionTestCase


class UsersTest(APITransactionTestCase):
    def test_user_crud(self):
        user = self.client.post('/api/v1/broker/users/', dict(name='foo', is_supervisor=False)).data
        self.assertEqual(user['name'], 'foo')
        self.client.patch(f'/api/v1/broker/users/{user["name"]}/', dict(is_supervisor=True))
        user = self.client.get(f'/api/v1/broker/users/{user["name"]}/').data
        self.assertEqual(user['is_supervisor'], True)

    def test_new_messages_small_page_size(self):
        self.new_messages(2)

    def test_new_messages_normal_page_size(self):
        self.new_messages(100)

    def new_messages(self, page_size: int):
        n = 333
        users = [self.client.post('/api/v1/broker/users/', dict(name=f'user{x}')).data for x in range(3)]
        for user in users:
            for i in range(n):
                message = f'Message {i} to {user["name"]}'
                self.client.post('/api/v1/broker/messages/', dict(user=user['name'], payload=message))
        user = users[1]

        messages = self.client.get(f'/api/v1/broker/users/{user["name"]}/new_messages/?page_size={page_size}').data
        self.assertEqual(messages['count'], n)
        self.assertEqual(len(messages['results']), page_size)

        messages = self.client.get(f'/api/v1/broker/users/{user["name"]}/new_messages/?page_size={page_size}').data
        self.assertEqual(messages['count'], n - page_size)
        self.assertEqual(len(messages['results']), page_size)
        first = messages['results'][0]['payload']
        self.assertTrue(f'Message {page_size} to' in first, msg=f'not the first we expected: {first}')

    def test_bad_user(self):
        response = self.client.get(f'/api/v1/broker/users/bill/new_messages/')
        self.assertEqual(response.status_code, 404)


class MessagesTest(APITestCase):
    def test_message_pagination(self):
        n = 1000
        user = self.client.post('/api/v1/broker/users/', dict(name='foo')).data
        for i in range(n):
            message = f'Message {i:04} to {user["name"]}'
            self.client.post('/api/v1/broker/messages/', dict(user=user['name'], payload=message))

        page_size = 13
        page_count = n // page_size
        if page_count * page_size < n:
            page_count += 1

        all_messages = []
        for page in range(1, page_count + 1):
            batch = self.client.get(f'/api/v1/broker/messages/?page_size={page_size}&page={page}').data
            all_messages.extend(list(batch['results']))

        # Check that we got all messages by traversing the pages
        self.assertEqual(len(all_messages), n)
        all_payloads = [m['payload'] for m in all_messages]

        # Check that the messages indeed were shown in order
        self.assertListEqual(all_payloads, sorted(all_payloads))
