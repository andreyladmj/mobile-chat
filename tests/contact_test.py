import unittest

from flask import json

from tests import api_test
from mob.models import User, Phone


class ContactTest(api_test.ApiTest):
    def test_add_contacts(self):
        self.create_random_user('0509998870', valid=True)
        self.create_random_user('0509998871', valid=True)
        self.create_random_user('0509998872', valid=True)
        self.create_random_user('0509998873', valid=True)
        self.create_random_user('0509998874', valid=False)

        current_user = self.login_by_user(number='0509998800')

        users, http_code = self.get_users()
        for user in users['result']:
            if user['id'] != current_user.id:
                phone = user['phones'][0]
                response, status_code = self.add_contact(phone['number'])

                if phone['is_active']:
                    assert status_code == 200
                else:
                    assert status_code == 404

    def test_add_unauth_contacts(self):
        self.create_random_user('0509998870')
        response, status_code = self.add_contact('0509998871')
        assert status_code == 401
        assert response['errors']['message'] == 'Phone number is required!'

    def test_get_contacts(self):
        self.create_random_user('0509998870')
        self.create_random_user('0509998871')
        self.create_random_user('0509998872')
        current_user = self.login_by_user(number='0509998800')
        self.add_contact('0509998870')
        self.add_contact('0509998871')
        self.add_contact('0509998872')

        response, status_code = self.get_contacts()
        assert len(response['result']) == 3

    def test_paginate_contacts(self):
        limit = 20
        current_user = self.login_by_user(number='0509998800')
        for user, number in self.create_batch_users(50):
            self.add_contact(str(number))

        response, status_code = self.get_contacts(limit=limit)
        assert len(response['result']) == limit

        last_id = None
        ids = []

        for user in response['result']:
            ids.append(user['id'])
            last_id = user['id']

        response, status_code = self.get_contacts(last_id=last_id, limit=limit)
        assert len(response['result']) == limit
        for user in response['result']:
            assert user['id'] not in ids

    def test_delete_contact(self):
        self.create_random_user('0509998870')
        self.create_random_user('0509998871')
        current_user = self.login_by_user(number='0509998800')
        self.add_contact('0509998870')
        self.add_contact('0509998871')
        response, status_code = self.delete_contact('0509998871')
        response, status_code = self.get_contacts()
        assert len(response['result']) == 1

    def delete_contact(self, number):
        response = self.client.delete('/api/contacts/{}'.format(number), headers=self.get_headers(),
                                      follow_redirects=True)
        return json.loads(response.data), response.status_code

    def get_contacts(self, last_id=None, limit=10):
        response = self.client.get('/api/contacts', headers=self.get_headers(),
                                   data=dict(
                                       last_id=last_id,
                                       limit=limit,
                                   ), follow_redirects=True)
        return json.loads(response.data), response.status_code


if __name__ == '__main__':
    unittest.main()