import logging
from unittest.mock import patch

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from users.models import FeedBack, User
from users.service import AccountService

logger = logging.getLogger(__name__)


class UserModelTests(TestCase):
    """
    Tests the custom User model and authentication-related behavior.
    """

    def test_user_password_is_hashed(self):
        try:
            user = User.objects.create_user(
                username="testuser",
                email="test@example.com",
                password="StrongPassword123!",
            )

            self.assertNotEqual(
                user.password,
                "StrongPassword123!",
            )

            self.assertTrue(
                user.check_password("StrongPassword123!"),
            )

            logger.info(
                "SUCCESS | UserModelTests.test_user_password_is_hashed",
            )

        except Exception:
            logger.exception(
                "FAILURE | UserModelTests.test_user_password_is_hashed",
            )
            raise

    def test_user_has_uuid_primary_key(self):
        try:
            user = User.objects.create_user(
                username="testuser",
                email="test@example.com",
                password="StrongPassword123!",
            )

            self.assertIsNotNone(user.id)

            logger.info(
                "SUCCESS | UserModelTests.test_user_has_uuid_primary_key",
            )

        except Exception:
            logger.exception(
                "FAILURE | UserModelTests.test_user_has_uuid_primary_key",
            )
            raise

    def test_user_email_is_unique(self):
        try:
            User.objects.create_user(
                username="testuser",
                email="test@example.com",
                password="StrongPassword123!",
            )

            with self.assertRaises(Exception):
                User.objects.create_user(
                    username="anotheruser",
                    email="test@example.com",
                    password="StrongPassword123!",
                )

            logger.info(
                "SUCCESS | UserModelTests.test_user_email_is_unique",
            )

        except Exception:
            logger.exception(
                "FAILURE | UserModelTests.test_user_email_is_unique",
            )
            raise


class AccountServiceTests(TestCase):
    """
    Tests business rules implemented by AccountService.
    """

    def test_register_creates_user(self):
        try:
            user = AccountService.register(
                username="testuser",
                email="test@example.com",
                password="StrongPassword123!",
                first_name="Test",
                last_name="User",
            )

            self.assertEqual(user.username, "testuser")
            self.assertEqual(user.email, "test@example.com")
            self.assertTrue(
                user.check_password("StrongPassword123!"),
            )
            self.assertTrue(user.is_active)
            self.assertFalse(user.is_verified)

            logger.info(
                "SUCCESS | AccountServiceTests.test_register_creates_user",
            )

        except Exception:
            logger.exception(
                "FAILURE | AccountServiceTests.test_register_creates_user",
            )
            raise

    def test_register_normalizes_email(self):
        try:
            user = AccountService.register(
                username="testuser",
                email="  TEST@EXAMPLE.COM ",
                password="StrongPassword123!",
            )

            self.assertEqual(
                user.email,
                "test@example.com",
            )

            logger.info(
                "SUCCESS | AccountServiceTests.test_register_normalizes_email",
            )

        except Exception:
            logger.exception(
                "FAILURE | AccountServiceTests.test_register_normalizes_email",
            )
            raise

    def test_register_rejects_duplicate_username(self):
        try:
            AccountService.register(
                username="testuser",
                email="first@example.com",
                password="StrongPassword123!",
            )

            with self.assertRaises(Exception):
                AccountService.register(
                    username="TESTUSER",
                    email="second@example.com",
                    password="StrongPassword123!",
                )

            logger.info(
                "SUCCESS | AccountServiceTests.test_register_rejects_duplicate_username",
            )

        except Exception:
            logger.exception(
                "FAILURE | AccountServiceTests.test_register_rejects_duplicate_username",
            )
            raise

    def test_register_rejects_duplicate_email(self):
        try:
            AccountService.register(
                username="testuser",
                email="test@example.com",
                password="StrongPassword123!",
            )

            with self.assertRaises(Exception):
                AccountService.register(
                    username="anotheruser",
                    email="TEST@EXAMPLE.COM",
                    password="StrongPassword123!",
                )

            logger.info(
                "SUCCESS | AccountServiceTests.test_register_rejects_duplicate_email",
            )

        except Exception:
            logger.exception(
                "FAILURE | AccountServiceTests.test_register_rejects_duplicate_email",
            )
            raise

    def test_login_returns_user_and_tokens(self):
        try:
            user = AccountService.register(
                username="testuser",
                email="test@example.com",
                password="StrongPassword123!",
            )

            authenticated_user, tokens = AccountService.login(
                username="testuser",
                password="StrongPassword123!",
            )

            self.assertEqual(
                authenticated_user.pk,
                user.pk,
            )

            self.assertIn("access", tokens)
            self.assertIn("refresh", tokens)

            logger.info(
                "SUCCESS | AccountServiceTests.test_login_returns_user_and_tokens",
            )

        except Exception:
            logger.exception(
                "FAILURE | AccountServiceTests.test_login_returns_user_and_tokens",
            )
            raise

    def test_login_updates_last_login(self):
        try:
            user = AccountService.register(
                username="testuser",
                email="test@example.com",
                password="StrongPassword123!",
            )

            self.assertIsNone(user.last_login)

            AccountService.login(
                username="testuser",
                password="StrongPassword123!",
            )

            user.refresh_from_db()

            self.assertIsNotNone(user.last_login)

            logger.info(
                "SUCCESS | AccountServiceTests.test_login_updates_last_login",
            )

        except Exception:
            logger.exception(
                "FAILURE | AccountServiceTests.test_login_updates_last_login",
            )
            raise

    def test_change_password(self):
        try:
            user = AccountService.register(
                username="testuser",
                email="test@example.com",
                password="OldPassword123!",
            )

            AccountService.change_password(
                user=user,
                old_password="OldPassword123!",
                new_password="NewPassword123!",
            )

            user.refresh_from_db()

            self.assertTrue(
                user.check_password("NewPassword123!"),
            )

            self.assertFalse(
                user.check_password("OldPassword123!"),
            )

            logger.info(
                "SUCCESS | AccountServiceTests.test_change_password",
            )

        except Exception:
            logger.exception(
                "FAILURE | AccountServiceTests.test_change_password",
            )
            raise

    def test_verify_email(self):
        try:
            user = AccountService.register(
                username="testuser",
                email="test@example.com",
                password="StrongPassword123!",
            )

            self.assertFalse(user.is_verified)

            AccountService.verify_email(user=user)

            user.refresh_from_db()

            self.assertTrue(user.is_verified)

            logger.info(
                "SUCCESS | AccountServiceTests.test_verify_email",
            )

        except Exception:
            logger.exception(
                "FAILURE | AccountServiceTests.test_verify_email",
            )
            raise

    def test_deactivate_account(self):
        try:
            user = AccountService.register(
                username="testuser",
                email="test@example.com",
                password="StrongPassword123!",
            )

            AccountService.deactivate_account(user=user)

            user.refresh_from_db()

            self.assertFalse(user.is_active)

            logger.info(
                "SUCCESS | AccountServiceTests.test_deactivate_account",
            )

        except Exception:
            logger.exception(
                "FAILURE | AccountServiceTests.test_deactivate_account",
            )
            raise


class UserAPITests(TestCase):
    """
    Tests the User HTTP API endpoints.
    """

    def setUp(self):
        self.client = APIClient()

        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="StrongPassword123!",
        )

    def test_register_endpoint(self):
        try:
            response = self.client.post(
                "/api/v1/users/register/",
                {
                    "username": "newuser",
                    "email": "new@example.com",
                    "first_name": "New",
                    "last_name": "User",
                    "password": "StrongPassword123!",
                    "password_confirm": "StrongPassword123!",
                },
                format="json",
            )

            self.assertEqual(response.status_code, 201)

            self.assertTrue(
                User.objects.filter(
                    username="newuser",
                ).exists(),
            )

            logger.info(
                "SUCCESS | UserAPITests.test_register_endpoint",
            )

        except Exception:
            logger.exception(
                "FAILURE | UserAPITests.test_register_endpoint",
            )
            raise

    def test_login_endpoint(self):
        try:
            response = self.client.post(
                "/api/v1/users/login/",
                {
                    "username": "testuser",
                    "password": "StrongPassword123!",
                },
                format="json",
            )

            self.assertEqual(response.status_code, 200)
            self.assertIn("access", response.data)
            self.assertIn("user", response.data)
            self.assertIn("refresh_token", response.cookies)

            logger.info(
                "SUCCESS | UserAPITests.test_login_endpoint",
            )

        except Exception:
            logger.exception(
                "FAILURE | UserAPITests.test_login_endpoint",
            )
            raise

    def test_login_rejects_invalid_password(self):
        try:
            response = self.client.post(
                "/api/v1/users/login/",
                {
                    "username": "testuser",
                    "password": "WrongPassword123!",
                },
                format="json",
            )

            self.assertEqual(response.status_code, 400)

            logger.info(
                "SUCCESS | UserAPITests.test_login_rejects_invalid_password",
            )

        except Exception:
            logger.exception(
                "FAILURE | UserAPITests.test_login_rejects_invalid_password",
            )
            raise

    def test_current_user_requires_authentication(self):
        try:
            response = self.client.get(
                "/api/v1/users/me/",
            )

            self.assertEqual(response.status_code, 401)

            logger.info(
                "SUCCESS | UserAPITests.test_current_user_requires_authentication",
            )

        except Exception:
            logger.exception(
                "FAILURE | UserAPITests.test_current_user_requires_authentication",
            )
            raise

    def test_current_user_endpoint(self):
        try:
            self.client.force_authenticate(
                user=self.user,
            )

            response = self.client.get(
                "/api/v1/users/me/",
            )

            self.assertEqual(response.status_code, 200)
            self.assertEqual(
                response.data["username"],
                "testuser",
            )

            logger.info(
                "SUCCESS | UserAPITests.test_current_user_endpoint",
            )

        except Exception:
            logger.exception(
                "FAILURE | UserAPITests.test_current_user_endpoint",
            )
            raise

    def test_update_user_endpoint(self):
        try:
            self.client.force_authenticate(
                user=self.user,
            )

            response = self.client.patch(
                "/api/v1/users/me/update/",
                {
                    "first_name": "Updated",
                    "last_name": "User",
                },
                format="json",
            )

            self.assertEqual(response.status_code, 200)

            self.user.refresh_from_db()

            self.assertEqual(
                self.user.first_name,
                "Updated",
            )

            logger.info(
                "SUCCESS | UserAPITests.test_update_user_endpoint",
            )

        except Exception:
            logger.exception(
                "FAILURE | UserAPITests.test_update_user_endpoint",
            )
            raise

    def test_change_password_endpoint(self):
        try:
            self.client.force_authenticate(
                user=self.user,
            )

            response = self.client.post(
                "/api/v1/users/me/change-password/",
                {
                    "old_password": "StrongPassword123!",
                    "new_password": "NewPassword123!",
                    "new_password_confirm": "NewPassword123!",
                },
                format="json",
            )

            self.assertEqual(response.status_code, 200)

            self.user.refresh_from_db()

            self.assertTrue(
                self.user.check_password("NewPassword123!"),
            )

            logger.info(
                "SUCCESS | UserAPITests.test_change_password_endpoint",
            )

        except Exception:
            logger.exception(
                "FAILURE | UserAPITests.test_change_password_endpoint",
            )
            raise

    def test_verify_email_endpoint(self):
        try:
            self.client.force_authenticate(
                user=self.user,
            )

            response = self.client.post(
                "/api/v1/users/me/verify-email/",
            )

            self.assertEqual(response.status_code, 200)

            self.user.refresh_from_db()

            self.assertTrue(self.user.is_verified)

            logger.info(
                "SUCCESS | UserAPITests.test_verify_email_endpoint",
            )

        except Exception:
            logger.exception(
                "FAILURE | UserAPITests.test_verify_email_endpoint",
            )
            raise

    def test_deactivate_account_endpoint(self):
        try:
            self.client.force_authenticate(
                user=self.user,
            )

            response = self.client.post(
                "/api/v1/users/me/deactivate/",
            )

            self.assertEqual(response.status_code, 200)

            self.user.refresh_from_db()

            self.assertFalse(self.user.is_active)

            logger.info(
                "SUCCESS | UserAPITests.test_deactivate_account_endpoint",
            )

        except Exception:
            logger.exception(
                "FAILURE | UserAPITests.test_deactivate_account_endpoint",
            )
            raise


class FeedBackApiTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="feedbackowner",
            email="owner@example.com",
            password="StrongPassword123",
        )
        self.url = "/api/v1/users/feedback/new/"

    @patch("users.service.TelegramService.send_ticket_notification")
    def test_create_feedback(self, mock_telegram):
        self.client.force_authenticate(user=self.user)

        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.post(
                self.url,
                {
                    "title": "Hello",
                    "description": "Need help",
                    "steps_to_reproduce": "steps_to_reproduce1,2,3,4",
                    "actual_behavior": "actual_behavior,2,3,4,4",
                    "type_of_feedback": FeedBack.Types.BUG_REPORT,
                },
                format="json",
            )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        feedback = FeedBack.objects.get()

        self.assertEqual(feedback.created_by, self.user)
        self.assertEqual(feedback.title, "Hello")
        self.assertEqual(feedback.description, "Need help")
        self.assertEqual(
            feedback.steps_to_reproduce,
            "steps_to_reproduce1,2,3,4",
        )
        self.assertEqual(
            feedback.actual_behavior,
            "actual_behavior,2,3,4,4",
        )
        self.assertEqual(
            feedback.type_of_feedback,
            FeedBack.Types.BUG_REPORT,
        )
        self.assertTrue(feedback.ticket.startswith("MOK-"))

        mock_telegram.assert_called_once_with(feedback)
