import unittest
from flask import json
from tests import api_test


class MessageTest(api_test.ApiTest):
    def test_add_message_to_user_that_not_in_your_contacts(self):
        current_user = self.login_by_user(number='0509998800')
        self.create_random_user('0509998870')
        response, status_code = self.add_message(message='hello', number='0509998870')
        assert status_code == 404
        assert response['errors']['message'] == 'Undefined contact'

    def test_add_message(self):
        current_user = self.login_by_user(number='0509998800')
        self.create_random_user('0509998870')
        self.add_contact('0509998870')
        response, status_code = self.add_message(message='hello', number='0509998870')
        assert status_code == 200
        assert response['result']['message'] == 'hello'

    def test_messages_paginate(self):
        limit = 20
        current_user = self.login_by_user(number='0509998800')
        user, number = self.add_batch_messages(owner_id=current_user.id, n=50)
        response, status_code = self.get_messages(number=number, limit=limit)
        assert status_code == 200
        assert len(response['result']) == limit

    def get_messages(self, number=None, last_id=None, limit=10):
        response = self.client.get('/api/messages/{}'.format(number), headers=self.get_headers(),
                                   data=dict(last_id=last_id, limit=limit),
                                   follow_redirects=True)
        return json.loads(response.data), response.status_code

    def add_message(self, message, number):
        response = self.client.post('/api/messages/{}'.format(number), headers=self.get_headers(),
                                    data=dict(message=message),
                                    follow_redirects=True)
        return json.loads(response.data), response.status_code


if __name__ == '__main__':
    unittest.main()