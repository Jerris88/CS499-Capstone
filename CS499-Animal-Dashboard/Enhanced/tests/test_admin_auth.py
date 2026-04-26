import unittest

from config.app_config import AppConfig
from database.admin_auth import AdminAuth


# tests for admin auth
class TestAdminAuth(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # use a test collection so real admin users are not touched
        cls.admin_auth = AdminAuth(
            user=AppConfig.USERNAME,
            pwd=AppConfig.PASSWORD,
            host=AppConfig.HOST,
            port=AppConfig.PORT,
            db=AppConfig.DB_NAME,
            collection="test_admin_users",
        )

    def setUp(self):
        # start each test with a clean test user
        self.username = "test_admin_user"
        self.password = "TestPass123!"
        self.new_password = "NewTestPass456!"

        self.admin_auth.delete_admin_user(self.username)

    def tearDown(self):
        # clean up test user after each test
        self.admin_auth.delete_admin_user(self.username)

    # admin user should be created
    def test_create_admin_user(self):
        created = self.admin_auth.create_admin_user(
            self.username,
            self.password,
        )

        self.assertTrue(created)

    # duplicate usernames should not be allowed
    def test_duplicate_admin_user_fails(self):
        self.admin_auth.create_admin_user(self.username, self.password)

        created_again = self.admin_auth.create_admin_user(
            self.username,
            self.password,
        )

        self.assertFalse(created_again)

    # correct password should verify
    def test_verify_correct_password(self):
        self.admin_auth.create_admin_user(self.username, self.password)

        is_valid = self.admin_auth.verify_admin_user(
            self.username,
            self.password,
        )

        self.assertTrue(is_valid)

    # wrong password should fail
    def test_verify_wrong_password_fails(self):
        self.admin_auth.create_admin_user(self.username, self.password)

        is_valid = self.admin_auth.verify_admin_user(
            self.username,
            "WrongPassword",
        )

        self.assertFalse(is_valid)

    # password update should let new password work
    def test_update_admin_password(self):
        self.admin_auth.create_admin_user(self.username, self.password)

        updated = self.admin_auth.update_admin_password(
            self.username,
            self.new_password,
        )

        is_valid = self.admin_auth.verify_admin_user(
            self.username,
            self.new_password,
        )

        self.assertTrue(updated)
        self.assertTrue(is_valid)

    # delete should remove the admin user
    def test_delete_admin_user(self):
        self.admin_auth.create_admin_user(self.username, self.password)

        deleted = self.admin_auth.delete_admin_user(self.username)
        user_record = self.admin_auth.find_user(self.username)

        self.assertTrue(deleted)
        self.assertIsNone(user_record)


if __name__ == "__main__":
    unittest.main()