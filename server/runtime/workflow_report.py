import csv
import json
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from uuid import UUID

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from projects.models import Projects
from resources.models import Fields, Resources
from users.models import User

REPORT_DIR = Path("test_reports/runtime_workflow")

WORKFLOW_CSV_FILE = REPORT_DIR / "runtime_workflow_report.csv"
WORKFLOW_JSON_FILE = REPORT_DIR / "runtime_workflow_report.json"
API_RESPONSE_JSON_FILE = REPORT_DIR / "runtime_api_response.json"


def serialize_value(value):
    if isinstance(value, (date, datetime)):
        return value.isoformat()

    if isinstance(value, Decimal):
        return float(value)

    if isinstance(value, UUID):
        return str(value)

    return value


def serialize_record(record):
    return {key: serialize_value(value) for key, value in record.items()}


class RuntimeWorkflowReportTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.user = User.objects.create_user(
            username="workflow-user",
            email="workflow@example.com",
            password="TestPassword123!",
        )

        self.project = Projects.objects.create(
            owner=self.user,
            name="Workflow Demo Project",
            slug="workflow-demo",
            is_published=True,
            created_by=self.user,
        )

        self.resource = Resources.objects.create(
            project=self.project,
            name="Products",
            slug="products",
            is_published=True,
            get_method=True,
            post_method=True,
            patch_method=True,
            delete_method=True,
            created_by=self.user,
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

    def test_generate_complete_runtime_workflow_report(self):
        workflow_steps = []
        fields_report = []

        workflow_steps.append(
            {
                "step": 1,
                "stage": "User Creation",
                "status": "PASS",
                "details": {
                    "username": self.user.username,
                    "email": self.user.email,
                    "user_id": str(self.user.pk),
                },
            }
        )

        workflow_steps.append(
            {
                "step": 2,
                "stage": "Project Creation",
                "status": "PASS",
                "details": {
                    "project": self.project.name,
                    "slug": self.project.slug,
                    "published": self.project.is_published,
                    "project_id": str(self.project.pk),
                },
            }
        )

        workflow_steps.append(
            {
                "step": 3,
                "stage": "Resource Creation",
                "status": "PASS",
                "details": {
                    "resource": self.resource.name,
                    "slug": self.resource.slug,
                    "published": self.resource.is_published,
                    "resource_id": str(self.resource.pk),
                    "methods": {
                        "GET": self.resource.get_method,
                        "POST": self.resource.post_method,
                        "PATCH": self.resource.patch_method,
                        "DELETE": self.resource.delete_method,
                    },
                },
            }
        )

        self.create_field(
            name="ID",
            slug="id",
            data_type="uuid",
            generator_key="uuid.v4",
            display_order=1,
        )

        self.create_field(
            name="Name",
            slug="name",
            data_type="string",
            generator_key="person.full_name",
            display_order=2,
        )

        self.create_field(
            name="Email",
            slug="email",
            data_type="string",
            generator_key="internet.email",
            generator_options={
                "domain": "example.com",
            },
            display_order=3,
        )

        self.create_field(
            name="Price",
            slug="price",
            data_type="decimal",
            generator_key="commerce.price",
            generator_options={
                "minimum": 10,
                "maximum": 100,
                "decimal_places": 2,
            },
            display_order=4,
        )

        self.create_field(
            name="Active",
            slug="active",
            data_type="boolean",
            generator_key="random.boolean",
            generator_options={
                "true_probability": 50,
            },
            display_order=5,
        )

        self.create_field(
            name="Created At",
            slug="created-at",
            data_type="datetime",
            generator_key="datetime.datetime",
            display_order=6,
        )

        fields = list(
            self.resource.fields.filter(
                deleted_at__isnull=True,
            ).order_by(
                "display_order",
            )
        )

        for field in fields:
            fields_report.append(
                {
                    "field": field.name,
                    "slug": field.slug,
                    "data_type": field.data_type,
                    "generator": field.generator_key,
                    "options": field.generator_options,
                    "display_order": field.display_order,
                    "status": "PASS",
                }
            )

        self.assertEqual(
            len(fields),
            6,
        )

        workflow_steps.append(
            {
                "step": 4,
                "stage": "Field Creation",
                "status": "PASS",
                "details": {
                    "field_count": len(fields_report),
                    "fields": fields_report,
                },
            }
        )

        url = reverse(
            "runtime-resource",
            kwargs={
                "project_slug": self.project.slug,
                "resource_slug": self.resource.slug,
            },
        )

        response = self.client.get(
            url,
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

        workflow_steps.append(
            {
                "step": 5,
                "stage": "Public API Request",
                "status": "PASS",
                "details": {
                    "method": "GET",
                    "url": url,
                    "count": 5,
                    "status_code": response.status_code,
                    "method_enabled": self.resource.get_method,
                },
            }
        )

        api_records = [serialize_record(record) for record in response.data]

        self.assertEqual(
            len(api_records),
            5,
        )

        expected_fields = [
            "id",
            "name",
            "email",
            "price",
            "active",
            "created-at",
        ]

        for record in api_records:
            self.assertEqual(
                list(record.keys()),
                expected_fields,
            )

            self.assertIsInstance(
                record["id"],
                str,
            )

            parsed_uuid = UUID(
                record["id"],
            )

            self.assertEqual(
                parsed_uuid.version,
                4,
            )

            self.assertIsInstance(
                record["name"],
                str,
            )

            self.assertTrue(
                record["name"].strip(),
            )

            self.assertIsInstance(
                record["email"],
                str,
            )

            self.assertIn(
                "@example.com",
                record["email"],
            )

            self.assertIsInstance(
                record["price"],
                (int, float),
            )

            self.assertGreaterEqual(
                record["price"],
                10,
            )

            self.assertLessEqual(
                record["price"],
                100,
            )

            self.assertIsInstance(
                record["active"],
                bool,
            )

            self.assertIsInstance(
                record["created-at"],
                str,
            )

            datetime.fromisoformat(
                record["created-at"],
            )

        workflow_steps.append(
            {
                "step": 6,
                "stage": "Mock Data Generation",
                "status": "PASS",
                "details": {
                    "records_generated": len(api_records),
                    "fields_returned": list(api_records[0].keys()),
                    "json_safe": True,
                    "decimal_serialized_as": "number",
                    "uuid_serialized_as": "string",
                    "datetime_serialized_as": "string",
                },
            }
        )

        REPORT_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        with API_RESPONSE_JSON_FILE.open(
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                api_records,
                file,
                indent=4,
            )

        workflow_steps.append(
            {
                "step": 7,
                "stage": "JSON Response Export",
                "status": "PASS",
                "details": {
                    "file": str(API_RESPONSE_JSON_FILE),
                    "records": len(api_records),
                    "format": "JSON",
                },
            }
        )

        report_rows = []

        for step in workflow_steps:
            report_rows.append(
                {
                    "step": step["step"],
                    "stage": step["stage"],
                    "status": step["status"],
                    "details": json.dumps(
                        step["details"],
                        default=str,
                        sort_keys=True,
                    ),
                }
            )

        with WORKFLOW_CSV_FILE.open(
            "w",
            newline="",
            encoding="utf-8",
        ) as file:
            writer = csv.DictWriter(
                file,
                fieldnames=[
                    "step",
                    "stage",
                    "status",
                    "details",
                ],
            )

            writer.writeheader()
            writer.writerows(
                report_rows,
            )

        report = {
            "report": "Mokvio Runtime Workflow",
            "version": "1.1",
            "status": "PASS",
            "workflow": {
                "user": {
                    "id": str(self.user.pk),
                    "username": self.user.username,
                    "email": self.user.email,
                },
                "project": {
                    "id": str(self.project.pk),
                    "name": self.project.name,
                    "slug": self.project.slug,
                    "is_published": self.project.is_published,
                },
                "resource": {
                    "id": str(self.resource.pk),
                    "name": self.resource.name,
                    "slug": self.resource.slug,
                    "is_published": self.resource.is_published,
                    "methods": {
                        "GET": self.resource.get_method,
                        "POST": self.resource.post_method,
                        "PATCH": self.resource.patch_method,
                        "DELETE": self.resource.delete_method,
                    },
                },
                "fields": fields_report,
                "endpoint": {
                    "method": "GET",
                    "url": url,
                    "count": 5,
                    "status_code": response.status_code,
                },
                "generated_records": api_records,
            },
            "steps": workflow_steps,
            "artifacts": {
                "workflow_csv": str(WORKFLOW_CSV_FILE),
                "workflow_json": str(WORKFLOW_JSON_FILE),
                "api_response_json": str(API_RESPONSE_JSON_FILE),
            },
        }

        with WORKFLOW_JSON_FILE.open(
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                report,
                file,
                indent=4,
                default=str,
            )

        self.assertTrue(
            WORKFLOW_CSV_FILE.exists(),
        )

        self.assertTrue(
            WORKFLOW_JSON_FILE.exists(),
        )

        self.assertTrue(
            API_RESPONSE_JSON_FILE.exists(),
        )

        with WORKFLOW_JSON_FILE.open(
            "r",
            encoding="utf-8",
        ) as file:
            generated_report = json.load(
                file,
            )

        self.assertEqual(
            generated_report["status"],
            "PASS",
        )

        self.assertEqual(
            len(generated_report["workflow"]["generated_records"]),
            5,
        )

        self.assertTrue(
            generated_report["workflow"]["resource"]["methods"]["GET"],
        )
