import json

from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from panel.serializers import (
    ActionResponseSerializer,
    ApiErrorSerializer,
    ContainerLogsResponseSerializer,
    CreateContainerRequestSerializer,
    CreateContainerResponseSerializer,
    CreateImageRequestSerializer,
    CreateImageResponseSerializer,
    DashboardResponseSerializer,
    HealthResponseSerializer,
)
from panel.services import docker_service
from panel.services.docker_service import DockerServiceError


def _error(message: str, status_code: int = 400) -> Response:
    return Response({"ok": False, "error": message}, status=status_code)


def _ok(data=None, message: str | None = None, status_code: int = 200) -> Response:
    payload: dict = {"ok": True}
    if data is not None:
        payload["data"] = data
    if message:
        payload["message"] = message
    return Response(payload, status=status_code)


def _parse_json(request) -> dict:
    if not request.body:
        return {}
    try:
        return json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return {}


class HealthView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["System"],
        summary="Health check",
        responses={200: HealthResponseSerializer},
    )
    def get(self, request):
        return _ok({"status": "ok"})


class DashboardView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["Dashboard"],
        summary="Dashboard overview",
        description="Returns Docker containers, images, and any service errors.",
        responses={200: DashboardResponseSerializer},
    )
    def get(self, request):
        errors: list[str] = []
        containers: list[dict[str, str]] = []
        images: list[dict[str, str]] = []

        try:
            containers = docker_service.list_containers()
        except DockerServiceError as exc:
            errors.append(str(exc))

        try:
            images = docker_service.list_images()
        except DockerServiceError as exc:
            errors.append(str(exc))

        return _ok(
            {
                "containers": containers,
                "images": images,
                "errors": errors,
                "docker_mode": "host" if docker_service.LIST_ALL_CONTAINERS else "isolated",
            }
        )


class CreateContainerView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["Containers"],
        summary="Create container",
        operation_id="container_create",
        request=CreateContainerRequestSerializer,
        responses={
            201: CreateContainerResponseSerializer,
            400: ApiErrorSerializer,
        },
    )
    def post(self, request):
        body = _parse_json(request)
        image = str(body.get("image", "")).strip()
        name = str(body.get("name", "")).strip()
        port_mapping = str(body.get("port_mapping", "")).strip()

        if not image or not name:
            return _error("Image and container name are required.")

        try:
            container_id = docker_service.create_container(
                image=image,
                name=name,
                port_mapping=port_mapping,
            )
            return _ok(
                {"id": container_id},
                message=f"Container created ({container_id}).",
                status_code=status.HTTP_201_CREATED,
            )
        except DockerServiceError as exc:
            return _error(str(exc))


class ContainerLogsView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["Containers"],
        summary="Container logs",
        parameters=[
            OpenApiParameter(
                name="container_id",
                type=str,
                location=OpenApiParameter.PATH,
                description="Docker container ID or prefix",
            ),
        ],
        responses={
            200: ContainerLogsResponseSerializer,
            400: ApiErrorSerializer,
        },
    )
    def get(self, request, container_id):
        try:
            logs = docker_service.get_logs(container_id)
            name = container_id
            for container in docker_service.list_containers():
                if container["id"] == container_id or container_id in container["id"]:
                    name = container["name"]
                    break
            return _ok(
                {
                    "container_id": container_id,
                    "container_name": name,
                    "logs": logs,
                }
            )
        except DockerServiceError as exc:
            return _error(str(exc))


class ContainerActionView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["Containers"],
        summary="Container action",
        operation_id="container_action",
        description="Run start, stop, restart, or delete on a container.",
        request=None,
        parameters=[
            OpenApiParameter(
                name="container_id",
                type=str,
                location=OpenApiParameter.PATH,
            ),
            OpenApiParameter(
                name="action",
                type=str,
                location=OpenApiParameter.PATH,
                enum=["start", "stop", "restart", "delete"],
            ),
        ],
        responses={
            200: ActionResponseSerializer,
            400: ApiErrorSerializer,
            404: ApiErrorSerializer,
        },
    )
    def post(self, request, container_id, action):
        actions = {
            "start": docker_service.start_container,
            "stop": docker_service.stop_container,
            "restart": docker_service.restart_container,
            "delete": docker_service.remove_container,
        }

        handler = actions.get(action)
        if handler is None:
            return _error(f"Unknown action: {action}", status_code=status.HTTP_404_NOT_FOUND)

        try:
            handler(container_id)
            return _ok(message=f"Container {action} succeeded.")
        except DockerServiceError as exc:
            return _error(str(exc))


class CreateImageView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["Images"],
        summary="Pull or build image",
        operation_id="image_create",
        request=CreateImageRequestSerializer,
        responses={
            201: CreateImageResponseSerializer,
            400: ApiErrorSerializer,
        },
    )
    def post(self, request):
        body = _parse_json(request)
        mode = str(body.get("mode", "pull")).strip()

        try:
            if mode == "pull":
                name = str(body.get("pull_name", "")).strip()
                if not name:
                    return _error("Image name is required.")
                image_id = docker_service.pull_image(name)
                return _ok(
                    {"id": image_id},
                    message=f"Image pulled ({image_id}).",
                    status_code=status.HTTP_201_CREATED,
                )

            if mode == "build":
                tag = str(body.get("build_tag", "")).strip()
                path = str(body.get("build_path", "")).strip()
                if not tag or not path:
                    return _error("Tag and build path are required.")
                image_id = docker_service.build_image(tag, path)
                return _ok(
                    {"id": image_id},
                    message=f"Image built ({image_id}).",
                    status_code=status.HTTP_201_CREATED,
                )

            return _error(f"Unknown mode: {mode}")
        except DockerServiceError as exc:
            return _error(str(exc))


class ImageActionView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["Images"],
        summary="Image action",
        operation_id="image_action",
        request=None,
        parameters=[
            OpenApiParameter(
                name="image_id",
                type=str,
                location=OpenApiParameter.PATH,
            ),
            OpenApiParameter(
                name="action",
                type=str,
                location=OpenApiParameter.PATH,
                enum=["delete"],
            ),
        ],
        responses={
            200: ActionResponseSerializer,
            400: ApiErrorSerializer,
            404: ApiErrorSerializer,
        },
    )
    def post(self, request, image_id, action):
        if action != "delete":
            return _error(f"Unknown action: {action}", status_code=status.HTTP_404_NOT_FOUND)

        try:
            docker_service.remove_image(image_id)
            return _ok(message="Image deleted.")
        except DockerServiceError as exc:
            return _error(str(exc))
