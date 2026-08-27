from django.http import Http404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from projects.models import Projects
from resources.service import ResourceService

from .serializers import (
    RuntimePatchSerializer,
    RuntimeQuerySerializer,
    RuntimeRequestSerializer,
    RuntimeResponseSerializer,
)
from .service import RuntimeService


class RuntimeAPIView(APIView):
    """
    Public runtime endpoint for generating mock API responses.
    """

    authentication_classes = []
    permission_classes = []

    @staticmethod
    def _get_project(project_slug):
        try:
            return Projects.objects.get(
                slug=project_slug,
                deleted_at__isnull=True,
                is_published=True,
            )
        except Projects.DoesNotExist as exc:
            raise Http404("Project not found.") from exc

    @staticmethod
    def _get_resource(project, resource_slug):
        resource = ResourceService.get_resource(
            project=project,
            resource_slug=resource_slug,
        )

        if resource.deleted_at is not None:
            raise Http404("Resource not found.")

        if not resource.is_published:
            raise Http404("Resource not published.")

        return resource

    def _get_published_resource(self, project_slug, resource_slug):
        project = self._get_project(project_slug)

        if not project.is_published:
            raise Http404("Project not published.")

        return self._get_resource(
            project=project,
            resource_slug=resource_slug,
        )

    def get(self, request, project_slug, resource_slug):
        query_serializer = RuntimeQuerySerializer(
            data=request.query_params,
        )

        query_serializer.is_valid(
            raise_exception=True,
        )

        count = query_serializer.validated_data["count"]

        resource = self._get_published_resource(
            project_slug=project_slug,
            resource_slug=resource_slug,
        )
        if not resource.get_method:
            return Response(
                {"message": "You didn't allowed this method on this resource."}, status=status.HTTP_400_BAD_REQUEST
            )

        if count == 1:
            record = RuntimeService.generate_record(
                resource,
            )

            return Response(
                RuntimeResponseSerializer.serialize(
                    record,
                )
            )

        records = RuntimeService.generate_records(
            resource=resource,
            count=count,
        )

        return Response(
            RuntimeResponseSerializer.serialize(
                records,
            )
        )

    def post(self, request, project_slug, resource_slug):
        resource = self._get_published_resource(
            project_slug=project_slug,
            resource_slug=resource_slug,
        )

        if not resource.post_method:
            return Response(
                {"message": "You didn't allowed this method on this resource."}, status=status.HTTP_400_BAD_REQUEST
            )

        serializer = RuntimeRequestSerializer(
            resource=resource,
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        return Response(
            {
                "success": True,
                "data": serializer.validated_data,
            }
        )

    def patch(self, request, project_slug, resource_slug):
        resource = self._get_published_resource(
            project_slug=project_slug,
            resource_slug=resource_slug,
        )
        if not resource.patch_method:
            return Response(
                {"message": "You didn't allowed this method on this resource."}, status=status.HTTP_400_BAD_REQUEST
            )

        serializer = RuntimePatchSerializer(
            resource=resource,
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        return Response(
            {
                "success": True,
                "data": serializer.validated_data,
            }
        )

    def delete(self, request, project_slug, resource_slug):
        record_id = request.query_params.get("id")

        resource = self._get_published_resource(
            project_slug=project_slug,
            resource_slug=resource_slug,
        )
        if not resource.delete_method:
            return Response(
                {"message": "You didn't allowed this method on this resource."}, status=status.HTTP_400_BAD_REQUEST
            )

        if record_id:
            return Response(
                {
                    "success": True,
                    "message": "Mock record deleted successfully.",
                    "id": record_id,
                }
            )

        return Response(
            {
                "success": True,
                "message": "All mock records deleted successfully.",
                "resource": resource.name,
            }
        )
