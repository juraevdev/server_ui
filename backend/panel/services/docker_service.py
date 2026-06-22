from __future__ import annotations

import os
from pathlib import Path

import docker
from docker.errors import APIError, BuildError, DockerException, ImageNotFound, NotFound

DEFAULT_LOG_TAIL = 200
CONTAINER_PREFIX = os.environ.get("DOCKER_CONTAINER_PREFIX", "panel-")
LIST_ALL_CONTAINERS = os.environ.get("DOCKER_LIST_ALL", "false").lower() in (
    "1",
    "true",
    "yes",
)


class DockerServiceError(Exception):
    pass


def _client() -> docker.DockerClient:
    try:
        return docker.from_env()
    except DockerException as exc:
        raise DockerServiceError(
            "Cannot connect to Docker. Is the Docker engine running?"
        ) from exc


def _managed_name(name: str) -> str:
    clean = name.strip().lstrip("/")
    if not CONTAINER_PREFIX:
        return clean
    if clean.startswith(CONTAINER_PREFIX):
        return clean
    return f"{CONTAINER_PREFIX}{clean}"


def _is_managed(name: str) -> bool:
    if not CONTAINER_PREFIX:
        return True
    return name.lstrip("/").startswith(CONTAINER_PREFIX)


def _get_managed_container(container_id: str):
    client = _client()
    try:
        container = client.containers.get(container_id)
    except NotFound as exc:
        raise DockerServiceError(f"Container not found: {container_id}") from exc

    if not _is_managed(container.name):
        raise DockerServiceError(
            "This container is outside Docker Panel scope and cannot be modified."
        )
    return container


def _image_label(container: docker.models.containers.Container) -> str:
    tags = container.image.tags
    if tags:
        return tags[0]
    return container.image.short_id


def list_containers() -> list[dict[str, str]]:
    client = _client()
    try:
        containers = client.containers.list(all=True)
    except APIError as exc:
        raise DockerServiceError(str(exc)) from exc

    return [
        {
            "id": container.short_id,
            "name": container.name.lstrip("/"),
            "image": _image_label(container),
            "status": container.status,
            "managed": _is_managed(container.name),
        }
        for container in containers
        if LIST_ALL_CONTAINERS or _is_managed(container.name)
    ]


def start_container(container_id: str) -> None:
    _run_action(container_id, "start")


def stop_container(container_id: str) -> None:
    _run_action(container_id, "stop")


def restart_container(container_id: str) -> None:
    _run_action(container_id, "restart")


def remove_container(container_id: str) -> None:
    container = _get_managed_container(container_id)
    try:
        container.remove(force=True)
    except APIError as exc:
        raise DockerServiceError(str(exc)) from exc


def get_logs(container_id: str, tail: int = DEFAULT_LOG_TAIL) -> str:
    if LIST_ALL_CONTAINERS:
        client = _client()
        try:
            container = client.containers.get(container_id)
        except NotFound as exc:
            raise DockerServiceError(f"Container not found: {container_id}") from exc
    else:
        container = _get_managed_container(container_id)
    try:
        raw = container.logs(tail=tail, timestamps=True)
        return raw.decode("utf-8", errors="replace")
    except APIError as exc:
        raise DockerServiceError(str(exc)) from exc


def create_container(
    image: str,
    name: str,
    port_mapping: str = "",
) -> str:
    client = _client()
    ports: dict[str, int] | None = None
    managed_name = _managed_name(name)

    if port_mapping.strip():
        try:
            host_port, container_port = port_mapping.strip().split(":", 1)
            ports = {f"{container_port.strip()}/tcp": int(host_port.strip())}
        except ValueError as exc:
            raise DockerServiceError(
                "Port mapping must look like 8081:80 (host:container)."
            ) from exc

    try:
        container = client.containers.run(
            image=image.strip(),
            name=managed_name,
            ports=ports,
            detach=True,
            labels={"managed_by": "docker-panel"},
        )
        return container.short_id
    except ImageNotFound as exc:
        raise DockerServiceError(f"Image not found: {image}") from exc
    except APIError as exc:
        raise DockerServiceError(str(exc)) from exc


def _format_size(size_bytes: int) -> str:
    if size_bytes < 1024:
        return f"{size_bytes} B"
    if size_bytes < 1024**2:
        return f"{size_bytes / 1024:.1f} KB"
    if size_bytes < 1024**3:
        return f"{size_bytes / 1024**2:.1f} MB"
    return f"{size_bytes / 1024**3:.1f} GB"


def list_images() -> list[dict[str, str]]:
    client = _client()
    try:
        images = client.images.list()
    except APIError as exc:
        raise DockerServiceError(str(exc)) from exc

    return [
        {
            "id": image.short_id,
            "tags": ", ".join(image.tags) if image.tags else "(untagged)",
            "size": _format_size(image.attrs.get("Size", 0)),
        }
        for image in images
    ]


def pull_image(name: str) -> str:
    client = _client()
    tag = name.strip()
    try:
        image = client.images.pull(tag)
    except APIError as exc:
        detail = getattr(exc, "explanation", None) or str(exc)
        if "not found" in detail.lower() or "pull access denied" in detail.lower():
            raise DockerServiceError(
                f'Image "{tag}" Docker Hub\'da topilmadi. '
                "Pull uchun nginx:latest kabi mavjud image yozing, "
                "yoki o'zingizniki uchun Build from Dockerfile tanlang."
            ) from exc
        raise DockerServiceError(detail) from exc

    return image.tags[0] if image.tags else image.short_id


def build_image(tag: str, path: str) -> str:
    build_path = Path(path.strip()).expanduser().resolve()
    if not build_path.is_dir():
        raise DockerServiceError(f"Build path not found: {path}")
    if not (build_path / "Dockerfile").is_file():
        raise DockerServiceError(f"No Dockerfile found in {build_path}")

    client = _client()
    try:
        image, _ = client.images.build(path=str(build_path), tag=tag.strip(), rm=True)
    except BuildError as exc:
        raise DockerServiceError(str(exc)) from exc
    except APIError as exc:
        raise DockerServiceError(str(exc)) from exc

    return image.tags[0] if image.tags else image.short_id


def remove_image(image_id: str) -> None:
    client = _client()
    try:
        client.images.remove(image_id, force=True)
    except ImageNotFound as exc:
        raise DockerServiceError(f"Image not found: {image_id}") from exc
    except APIError as exc:
        raise DockerServiceError(str(exc)) from exc


def _run_action(container_id: str, action: str) -> None:
    container = _get_managed_container(container_id)
    try:
        getattr(container, action)()
    except APIError as exc:
        raise DockerServiceError(str(exc)) from exc
