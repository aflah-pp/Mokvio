from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from projects.models import Projects
from resources.models import Fields, Resources
from users.models import User

from .service import RuntimeService


class RuntimeServiceTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="runtime-user",
            email="runtime@example.com",
            password="TestPassword123!",
        )

        self.project = Projects.objects.create(
            owner=self.user,
            name="Runtime Project",
            slug="runtime-project",
            is_published=True,
            created_by=self.user,
        )

        self.resource = Resources.objects.create(
            project=self.project,
            name="Products",
            slug="products",
            is_published=True,
            created_by=self.user,
        )

    def test_generate_record_generates_values_for_all_active_fields(self):
        Fields.objects.create(
            resource=self.resource,
            name="Name",
            slug="name",
            data_type="string",
            generator_key="person.full_name",
            generator_options={},
            display_order=1,
            created_by=self.user,
        )

        Fields.objects.create(
            resource=self.resource,
            name="Price",
            slug="price",
            data_type="decimal",
            generator_key="commerce.price",
            generator_options={
                "minimum": 10,
                "maximum": 100,
                "decimal_places": 2,
            },
            display_order=2,
            created_by=self.user,
        )

        Fields.objects.create(
            resource=self.resource,
            name="Active",
            slug="active",
            data_type="boolean",
            generator_key="random.boolean",
            generator_options={
                "true_probability": 100,
            },
            display_order=3,
            created_by=self.user,
        )

        record = RuntimeService.generate_record(self.resource)

        self.assertIn("name", record)
        self.assertIn("price", record)
        self.assertIn("active", record)

        self.assertIsInstance(record["name"], str)

        self.assertIsInstance(record["price"], Decimal)

        self.assertGreaterEqual(
            record["price"],
            Decimal("10"),
        )

        self.assertLessEqual(
            record["price"],
            Decimal("100"),
        )

        self.assertIs(
            record["active"],
            True,
        )

    def test_generate_record_generates_uuid(self):
        Fields.objects.create(
            resource=self.resource,
            name="ID",
            slug="id",
            data_type="uuid",
            generator_key="uuid.v4",
            generator_options={},
            display_order=1,
            created_by=self.user,
        )

        record = RuntimeService.generate_record(self.resource)

        self.assertIn("id", record)

        self.assertIsInstance(
            record["id"],
            UUID,
        )

        self.assertEqual(
            record["id"].version,
            4,
        )

    def test_generate_record_generates_date(self):
        Fields.objects.create(
            resource=self.resource,
            name="Date",
            slug="date",
            data_type="date",
            generator_key="datetime.date",
            generator_options={},
            display_order=1,
            created_by=self.user,
        )

        record = RuntimeService.generate_record(self.resource)

        self.assertIsInstance(
            record["date"],
            date,
        )

        self.assertNotIsInstance(
            record["date"],
            datetime,
        )

    def test_generate_record_generates_datetime(self):
        Fields.objects.create(
            resource=self.resource,
            name="Created At",
            slug="created-at",
            data_type="datetime",
            generator_key="datetime.datetime",
            generator_options={},
            display_order=1,
            created_by=self.user,
        )

        record = RuntimeService.generate_record(self.resource)

        self.assertIsInstance(
            record["created-at"],
            datetime,
        )

    def test_generate_record_respects_field_display_order(self):
        first = Fields.objects.create(
            resource=self.resource,
            name="First",
            slug="first",
            data_type="string",
            generator_key="person.first_name",
            generator_options={},
            display_order=2,
            created_by=self.user,
        )

        second = Fields.objects.create(
            resource=self.resource,
            name="Second",
            slug="second",
            data_type="string",
            generator_key="person.last_name",
            generator_options={},
            display_order=1,
            created_by=self.user,
        )

        record = RuntimeService.generate_record(self.resource)

        self.assertEqual(
            list(record.keys()),
            [
                second.slug,
                first.slug,
            ],
        )

    def test_generate_record_excludes_deleted_fields(self):
        active_field = Fields.objects.create(
            resource=self.resource,
            name="Name",
            slug="name",
            data_type="string",
            generator_key="person.full_name",
            generator_options={},
            display_order=1,
            created_by=self.user,
        )

        deleted_field = Fields.objects.create(
            resource=self.resource,
            name="Deleted",
            slug="deleted",
            data_type="string",
            generator_key="person.full_name",
            generator_options={},
            display_order=2,
            created_by=self.user,
        )

        deleted_field.deleted_at = timezone.now()
        deleted_field.deleted_by = self.user
        deleted_field.updated_by = self.user

        deleted_field.save(
            update_fields=[
                "deleted_at",
                "deleted_by",
                "updated_by",
                "updated_at",
            ],
        )

        record = RuntimeService.generate_record(self.resource)

        self.assertIn(
            active_field.slug,
            record,
        )

        self.assertNotIn(
            deleted_field.slug,
            record,
        )

    def test_generate_records_returns_requested_number_of_records(self):
        Fields.objects.create(
            resource=self.resource,
            name="Name",
            slug="name",
            data_type="string",
            generator_key="person.full_name",
            generator_options={},
            display_order=1,
            created_by=self.user,
        )

        records = RuntimeService.generate_records(
            resource=self.resource,
            count=10,
        )

        self.assertEqual(
            len(records),
            10,
        )

        for record in records:
            self.assertIn(
                "name",
                record,
            )

            self.assertIsInstance(
                record["name"],
                str,
            )

    def test_generate_records_default_count_is_one(self):
        Fields.objects.create(
            resource=self.resource,
            name="Name",
            slug="name",
            data_type="string",
            generator_key="person.full_name",
            generator_options={},
            display_order=1,
            created_by=self.user,
        )

        records = RuntimeService.generate_records(
            resource=self.resource,
        )

        self.assertEqual(
            len(records),
            1,
        )

    def test_generate_records_return_independent_records(self):
        Fields.objects.create(
            resource=self.resource,
            name="Name",
            slug="name",
            data_type="string",
            generator_key="person.full_name",
            generator_options={},
            display_order=1,
            created_by=self.user,
        )

        records = RuntimeService.generate_records(
            resource=self.resource,
            count=5,
        )

        self.assertEqual(
            len(records),
            5,
        )

        for record in records:
            self.assertIsInstance(
                record,
                dict,
            )

            self.assertIn(
                "name",
                record,
            )

    def test_generate_record_with_no_active_fields_returns_empty_record(self):
        field = Fields.objects.create(
            resource=self.resource,
            name="Deleted",
            slug="deleted",
            data_type="string",
            generator_key="person.full_name",
            generator_options={},
            display_order=1,
            created_by=self.user,
        )

        field.deleted_at = timezone.now()
        field.deleted_by = self.user
        field.updated_by = self.user

        field.save(
            update_fields=[
                "deleted_at",
                "deleted_by",
                "updated_by",
                "updated_at",
            ],
        )

        record = RuntimeService.generate_record(self.resource)

        self.assertEqual(
            record,
            {},
        )


class RuntimeAPIViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.user = User.objects.create_user(
            username="runtime-api-user",
            email="runtime-api@example.com",
            password="TestPassword123!",
        )

        self.project = Projects.objects.create(
            owner=self.user,
            name="Runtime API Project",
            slug="runtime-api-project",
            is_published=True,
            created_by=self.user,
        )

        self.resource = Resources.objects.create(
            project=self.project,
            name="Products",
            slug="products",
            is_published=True,
            created_by=self.user,
            get_method=True,
            post_method=True,
            patch_method=True,
            delete_method=True,
        )

        self.url = reverse(
            "runtime-resource",
            kwargs={
                "project_slug": self.project.slug,
                "resource_slug": self.resource.slug,
            },
        )

    def create_field(
        self,
        name,
        slug,
        data_type,
        generator_key,
        generator_options=None,
        display_order=1,
    ):
        return Fields.objects.create(
            resource=self.resource,
            name=name,
            slug=slug,
            data_type=data_type,
            generator_key=generator_key,
            generator_options=generator_options or {},
            display_order=display_order,
            created_by=self.user,
        )

    def disable_method(self, method):
        setattr(
            self.resource,
            f"{method}_method",
            False,
        )

        self.resource.save(
            update_fields=[f"{method}_method"],
        )

    def test_public_endpoint_generates_single_record(self):
        self.create_field(
            name="Name",
            slug="name",
            data_type="string",
            generator_key="person.full_name",
        )

        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertIsInstance(
            response.data,
            dict,
        )

        self.assertIn(
            "name",
            response.data,
        )

        self.assertIsInstance(
            response.data["name"],
            str,
        )

    def test_public_endpoint_generates_multiple_records(self):
        self.create_field(
            name="Name",
            slug="name",
            data_type="string",
            generator_key="person.full_name",
        )

        response = self.client.get(
            self.url,
            {
                "count": 5,
            },
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertIsInstance(
            response.data,
            list,
        )

        self.assertEqual(
            len(response.data),
            5,
        )

        for record in response.data:
            self.assertIn(
                "name",
                record,
            )

            self.assertIsInstance(
                record["name"],
                str,
            )

    def test_default_count_is_one(self):
        self.create_field(
            name="Name",
            slug="name",
            data_type="string",
            generator_key="person.full_name",
        )

        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertIsInstance(
            response.data,
            dict,
        )

    def test_count_one_returns_object(self):
        self.create_field(
            name="Name",
            slug="name",
            data_type="string",
            generator_key="person.full_name",
        )

        response = self.client.get(
            self.url,
            {
                "count": 1,
            },
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertIsInstance(
            response.data,
            dict,
        )

    def test_count_greater_than_one_returns_list(self):
        self.create_field(
            name="Name",
            slug="name",
            data_type="string",
            generator_key="person.full_name",
        )

        response = self.client.get(
            self.url,
            {
                "count": 10,
            },
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertIsInstance(
            response.data,
            list,
        )

        self.assertEqual(
            len(response.data),
            10,
        )

    def test_get_method_lock_returns_400_when_disabled(self):
        self.disable_method("get")

        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            400,
        )

        self.assertEqual(
            response.data["message"],
            "You didn't allowed this method on this resource.",
        )

    def test_post_method_lock_returns_400_when_disabled(self):
        self.disable_method("post")

        response = self.client.post(
            self.url,
            {
                "name": "Test Product",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            400,
        )

        self.assertEqual(
            response.data["message"],
            "You didn't allowed this method on this resource.",
        )

    def test_patch_method_lock_returns_400_when_disabled(self):
        self.disable_method("patch")

        response = self.client.patch(
            self.url,
            {
                "name": "Updated Product",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            400,
        )

        self.assertEqual(
            response.data["message"],
            "You didn't allowed this method on this resource.",
        )

    def test_delete_method_lock_returns_400_when_disabled(self):
        self.disable_method("delete")

        response = self.client.delete(
            self.url,
            {
                "id": "123",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            400,
        )

        self.assertEqual(
            response.data["message"],
            "You didn't allowed this method on this resource.",
        )

    def test_post_method_returns_success_when_enabled(self):
        response = self.client.post(
            self.url,
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertTrue(
            response.data["success"],
        )

        self.assertIn(
            "data",
            response.data,
        )

    def test_patch_method_returns_success_when_enabled(self):
        self.create_field(
            name="Name",
            slug="name",
            data_type="string",
            generator_key="person.full_name",
        )

        response = self.client.patch(
            self.url,
            {
                "name": "Updated Product",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertTrue(
            response.data["success"],
        )

        self.assertEqual(
            response.data["data"]["name"],
            "Updated Product",
        )

    def test_delete_method_returns_success_with_id(self):
        response = self.client.delete(
            f"{self.url}?id=123",
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertTrue(
            response.data["success"],
        )

        self.assertEqual(
            response.data["message"],
            "Mock record deleted successfully.",
        )

        self.assertEqual(
            response.data["id"],
            "123",
        )

    def test_delete_method_returns_success_without_id(self):
        response = self.client.delete(self.url)

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertTrue(
            response.data["success"],
        )

        self.assertEqual(
            response.data["message"],
            "All mock records deleted successfully.",
        )

        self.assertEqual(
            response.data["resource"],
            self.resource.name,
        )

    def test_unpublished_project_returns_404(self):
        self.project.is_published = False

        self.project.save(
            update_fields=["is_published"],
        )

        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            404,
        )

    def test_deleted_project_returns_404(self):
        self.project.deleted_at = timezone.now()
        self.project.deleted_by = self.user

        self.project.save(
            update_fields=[
                "deleted_at",
                "deleted_by",
            ],
        )

        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            404,
        )

    def test_unpublished_resource_returns_404(self):
        self.resource.is_published = False

        self.resource.save(
            update_fields=["is_published"],
        )

        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            404,
        )

    def test_deleted_resource_returns_404(self):
        self.resource.deleted_at = timezone.now()
        self.resource.deleted_by = self.user

        self.resource.save(
            update_fields=[
                "deleted_at",
                "deleted_by",
            ],
        )

        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            404,
        )

    def test_nonexistent_project_returns_404(self):
        url = reverse(
            "runtime-resource",
            kwargs={
                "project_slug": "does-not-exist",
                "resource_slug": self.resource.slug,
            },
        )

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            404,
        )

    def test_nonexistent_resource_returns_404(self):
        url = reverse(
            "runtime-resource",
            kwargs={
                "project_slug": self.project.slug,
                "resource_slug": "does-not-exist",
            },
        )

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            404,
        )

    def test_resource_from_another_project_cannot_be_accessed(self):
        other_project = Projects.objects.create(
            owner=self.user,
            name="Other Project",
            slug="other-project",
            is_published=True,
            created_by=self.user,
        )

        other_resource = Resources.objects.create(
            project=other_project,
            name="Other Products",
            slug="other-products",
            is_published=True,
            created_by=self.user,
        )

        url = reverse(
            "runtime-resource",
            kwargs={
                "project_slug": self.project.slug,
                "resource_slug": other_resource.slug,
            },
        )

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            404,
        )

    def test_deleted_fields_are_not_returned(self):
        self.create_field(
            name="Name",
            slug="name",
            data_type="string",
            generator_key="person.full_name",
        )

        deleted_field = self.create_field(
            name="Deleted",
            slug="deleted",
            data_type="string",
            generator_key="person.full_name",
            display_order=2,
        )

        deleted_field.deleted_at = timezone.now()
        deleted_field.deleted_by = self.user
        deleted_field.updated_by = self.user

        deleted_field.save(
            update_fields=[
                "deleted_at",
                "deleted_by",
                "updated_by",
                "updated_at",
            ],
        )

        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertIn(
            "name",
            response.data,
        )

        self.assertNotIn(
            "deleted",
            response.data,
        )

    def test_no_active_fields_returns_empty_object(self):
        field = self.create_field(
            name="Deleted",
            slug="deleted",
            data_type="string",
            generator_key="person.full_name",
        )

        field.deleted_at = timezone.now()
        field.deleted_by = self.user
        field.updated_by = self.user

        field.save(
            update_fields=[
                "deleted_at",
                "deleted_by",
                "updated_by",
                "updated_at",
            ],
        )

        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            response.data,
            {},
        )

    def test_decimal_value_is_returned_as_json_number(self):
        self.create_field(
            name="Price",
            slug="price",
            data_type="decimal",
            generator_key="commerce.price",
            generator_options={
                "minimum": 50,
                "maximum": 50,
                "decimal_places": 2,
            },
        )

        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            response.data["price"],
            50.0,
        )

    def test_uuid_value_is_returned_as_string(self):
        self.create_field(
            name="ID",
            slug="id",
            data_type="uuid",
            generator_key="uuid.v4",
        )

        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertIsInstance(
            response.data["id"],
            str,
        )

        parsed_uuid = UUID(
            response.data["id"],
        )

        self.assertEqual(
            parsed_uuid.version,
            4,
        )

    def test_generator_configuration_is_respected(self):
        self.create_field(
            name="Active",
            slug="active",
            data_type="boolean",
            generator_key="random.boolean",
            generator_options={
                "true_probability": 100,
            },
        )

        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertIs(
            response.data["active"],
            True,
        )

    def test_fields_are_returned_using_display_order(self):
        first = self.create_field(
            name="First",
            slug="first",
            data_type="string",
            generator_key="person.first_name",
            display_order=2,
        )

        second = self.create_field(
            name="Second",
            slug="second",
            data_type="string",
            generator_key="person.last_name",
            display_order=1,
        )

        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            list(response.data.keys()),
            [
                second.slug,
                first.slug,
            ],
        )

    def test_public_endpoint_does_not_require_authentication(self):
        self.create_field(
            name="Name",
            slug="name",
            data_type="string",
            generator_key="person.full_name",
        )

        self.client.force_authenticate(user=None)

        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            200,
        )
