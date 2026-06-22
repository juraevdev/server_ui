import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from panel.services import docker_service
from panel.services.docker_service import DockerServiceError


def _json_error(message: str, status: int = 400) -> JsonResponse:
    return JsonResponse({"ok": False, "error": message}, status=status)


def _json_ok(data=None, message: str | None = None, status: int = 200) -> JsonResponse:
    payload: dict = {"ok": True}
    if data is not None:
        payload["data"] = data
    if message:
        payload["message"] = message
    return JsonResponse(payload, status=status)


def _parse_json(request) -> dict:
    if not request.body:
        return {}
    try:
        return json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return {}


@require_GET
def health(request):
    return _json_ok({"status": "ok"})


@require_GET
def dashboard(request):
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

    return _json_ok(
        {
            "containers": containers,
            "images": images,
            "errors": errors,
            "docker_mode": "host" if docker_service.LIST_ALL_CONTAINERS else "isolated",
        }
    )


@csrf_exempt
@require_http_methods(["POST"])
def create_container(request):
    body = _parse_json(request)
    image = str(body.get("image", "")).strip()
    name = str(body.get("name", "")).strip()
    port_mapping = str(body.get("port_mapping", "")).strip()

    if not image or not name:
        return _json_error("Image and container name are required.")

    try:
        container_id = docker_service.create_container(
            image=image,
            name=name,
            port_mapping=port_mapping,
        )
        return _json_ok(
            {"id": container_id},
            message=f"Container created ({container_id}).",
            status=201,
        )
    except DockerServiceError as exc:
        return _json_error(str(exc))


@require_GET
def container_logs(request, container_id):
    try:
        logs = docker_service.get_logs(container_id)
        name = container_id
        for container in docker_service.list_containers():
            if container["id"] == container_id or container_id in container["id"]:
                name = container["name"]
                break
        return _json_ok(
            {
                "container_id": container_id,
                "container_name": name,
                "logs": logs,
            }
        )
    except DockerServiceError as exc:
        return _json_error(str(exc))


@csrf_exempt
@require_POST
def container_action(request, container_id, action):
    actions = {
        "start": docker_service.start_container,
        "stop": docker_service.stop_container,
        "restart": docker_service.restart_container,
        "delete": docker_service.remove_container,
    }

    handler = actions.get(action)
    if handler is None:
        return _json_error(f"Unknown action: {action}", status=404)

    try:
        handler(container_id)
        return _json_ok(message=f"Container {action} succeeded.")
    except DockerServiceError as exc:
        return _json_error(str(exc))


@csrf_exempt
@require_http_methods(["POST"])
def create_image(request):
    body = _parse_json(request)
    mode = str(body.get("mode", "pull")).strip()

    try:
        if mode == "pull":
            name = str(body.get("pull_name", "")).strip()
            if not name:
                return _json_error("Image name is required.")
            image_id = docker_service.pull_image(name)
            return _json_ok(
                {"id": image_id},
                message=f"Image pulled ({image_id}).",
                status=201,
            )

        if mode == "build":
            tag = str(body.get("build_tag", "")).strip()
            path = str(body.get("build_path", "")).strip()
            if not tag or not path:
                return _json_error("Tag and build path are required.")
            image_id = docker_service.build_image(tag, path)
            return _json_ok(
                {"id": image_id},
                message=f"Image built ({image_id}).",
                status=201,
            )

        return _json_error(f"Unknown mode: {mode}")
    except DockerServiceError as exc:
        return _json_error(str(exc))


@csrf_exempt
@require_POST
def image_action(request, image_id, action):
    if action != "delete":
        return _json_error(f"Unknown action: {action}", status=404)

    try:
        docker_service.remove_image(image_id)
        return _json_ok(message="Image deleted.")
    except DockerServiceError as exc:
        return _json_error(str(exc))
