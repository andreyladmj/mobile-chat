import unittest

from tests import api_test


class UserTest(api_test.ApiTest):
    def test_delete_user(self):
        response, status_code = self.create_user('Morgun', 'Bezglazov', '0508971234')
        self.set_phone('0508971234')
        response, status_code = self.delete_user('0508971234')
        assert status_code == 200
        response, status_code = self.get_user('0508971234')
        assert status_code == 404

    def test_delete_wrong_user(self):
        response, status_code = self.create_user('Morgun', 'Bezglazov', '0508971234')
        user_id = response['result']['id']
        response, status_code = self.delete_user(user_id)
        assert status_code == 401
        assert response['errors']['message'] == 'Phone number is required!'

    def test_create_user_success(self):
        response, status_code = self.create_user('Stepan', 'Sraka', '0508971234')
        phones = response['result']['phones']
        assert status_code == 200
        assert len(phones) == 1
        assert phones[0]['is_active'] is False

    def test_create_user_fail(self):
        response, status_code = self.create_user(None, None, None)
        assert status_code == 500
        assert 'This field is required.' in response['errors']['first_name']
        assert 'This field is required.' in response['errors']['last_name']
        assert 'This field is required.' in response['errors']['phone']

    def test_get_list_users(self):
        self.create_user('Stepan 1', 'Sraka 1', '0508971231')
        self.create_user('Stepan 2', 'Sraka 2', '0508971232')
        self.create_user('Stepan 3', 'Sraka 3', '0508971233')
        response, status_code = self.get_users()
        assert len(response['result']) == 3

    def test_fail_validation_number(self):
        response, status_code = self.create_user('Morgun', 'Bezglazov', '0508971234')
        self.set_phone('0508971234')
        response, status_code = self.validate_phone('1230', '123123123')
        assert status_code == 401
        assert response['errors']['message'] == 'Number is wrong'

    def test_fail_pin(self):
        response, status_code = self.create_user('Morgun', 'Bezglazov', '0508971234')
        self.set_phone('0508971234')
        response, status_code = self.validate_phone('1230', '0508971234')
        assert status_code == 401
        assert response['errors']['message'] == 'Wrong pin'


    def test_duplicate_phone_number(self):
        response, status_code = self.create_user('Stepan 1', 'Sraka 1', '0508971231')
        assert status_code == 200

        response, status_code = self.create_user('Stepan 1', 'Sraka 1', '0508971231')
        assert status_code == 500 # maybe would be better to send 409 code

    def test_success_validate_number(self):
        response, status_code = self.create_user('Otrjad', 'Plebeev', '0508971234')
        assert response['success'] == 1
        assert status_code == 200
        user = response['result']

        self.set_phone('0508971234')
        response, status_code = self.validate_phone('1234', '0508971234')
        response, status_code = self.get_user('0508971234')
        assert status_code == 200

        user = response['result']
        phone = user['phones'][0]

        assert phone['is_active'] == True

    def test_unauth_update_user(self):
        self.token = None
        response, status_code = self.create_user('Ovrag', 'Bizonov', '0508971234')
        response, status_code = self.update_user('0508971234', None, 'Beznogov')
        assert status_code == 401
        assert response['errors']['message'] == 'Phone number is required!'

    def test_update_user(self):
        response, status_code = self.create_user('Ovrag', 'Bizonov', '0508971234')
        self.set_phone('0508971234')
        response, status_code = self.update_user('0508971234', None, 'Beznogov')
        assert status_code == 200
        assert response['result']['last_name'] == 'Beznogov'

    def test_update_wrong_user(self):
        user1 = self.login_by_user(number='0509998877')
        user2 = self.login_by_user(number='0509998878')
        response, status_code = self.update_user('0509998877', None, 'Beznogov')
        assert status_code == 403
        assert response['errors']['message'] == 'Forbidden'


if __name__ == '__main__':
    unittest.main()