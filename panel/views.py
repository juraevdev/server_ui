from django.contrib import messages
from django.shortcuts import redirect, render
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from panel.services import docker_service
from panel.services.docker_service import DockerServiceError


@require_GET
def dashboard(request):
    containers = []
    images = []

    try:
        containers = docker_service.list_containers()
    except DockerServiceError as exc:
        messages.error(request, str(exc))

    try:
        images = docker_service.list_images()
    except DockerServiceError as exc:
        messages.error(request, str(exc))

    return render(
        request,
        "panel/dashboard.html",
        {"containers": containers, "images": images},
    )


@require_http_methods(["GET", "POST"])
def create_container(request):
    form_data = {
        "image": request.POST.get("image", "") if request.method == "POST" else "",
        "name": request.POST.get("name", "") if request.method == "POST" else "",
        "port_mapping": request.POST.get("port_mapping", "")
        if request.method == "POST"
        else "",
    }

    if request.method == "POST":
        image = form_data["image"].strip()
        name = form_data["name"].strip()

        if not image or not name:
            messages.error(request, "Image and container name are required.")
        else:
            try:
                container_id = docker_service.create_container(
                    image=image,
                    name=name,
                    port_mapping=form_data["port_mapping"],
                )
                messages.success(request, f"Container created ({container_id}).")
                return redirect("panel:dashboard")
            except DockerServiceError as exc:
                messages.error(request, str(exc))

    return render(request, "panel/create.html", {"form_data": form_data})


@require_GET
def container_logs(request, container_id):
    try:
        logs = docker_service.get_logs(container_id)
        name = container_id
        for container in docker_service.list_containers():
            if container["id"] == container_id or container_id in container["id"]:
                name = container["name"]
                break
    except DockerServiceError as exc:
        messages.error(request, str(exc))
        return redirect("panel:dashboard")

    return render(
        request,
        "panel/logs.html",
        {"container_id": container_id, "container_name": name, "logs": logs},
    )


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
        messages.error(request, f"Unknown action: {action}")
        return redirect("panel:dashboard")

    try:
        handler(container_id)
        messages.success(request, f"Container {action} succeeded.")
    except DockerServiceError as exc:
        messages.error(request, str(exc))

    return redirect("panel:dashboard")


@require_http_methods(["GET", "POST"])
def create_image(request):
    form_data = {
        "mode": request.POST.get("mode", "pull")
        if request.method == "POST"
        else "pull",
        "pull_name": request.POST.get("pull_name", "")
        if request.method == "POST"
        else "",
        "build_tag": request.POST.get("build_tag", "")
        if request.method == "POST"
        else "",
        "build_path": request.POST.get("build_path", "")
        if request.method == "POST"
        else "",
    }

    if request.method == "POST":
        mode = form_data["mode"]
        try:
            if mode == "pull":
                name = form_data["pull_name"].strip()
                if not name:
                    messages.error(request, "Image name is required.")
                else:
                    image_id = docker_service.pull_image(name)
                    messages.success(request, f"Image pulled ({image_id}).")
                    return redirect("panel:dashboard")
            elif mode == "build":
                tag = form_data["build_tag"].strip()
                path = form_data["build_path"].strip()
                if not tag or not path:
                    messages.error(request, "Tag and build path are required.")
                else:
                    image_id = docker_service.build_image(tag, path)
                    messages.success(request, f"Image built ({image_id}).")
                    return redirect("panel:dashboard")
            else:
                messages.error(request, f"Unknown mode: {mode}")
        except DockerServiceError as exc:
            messages.error(request, str(exc))

    return render(request, "panel/create_image.html", {"form_data": form_data})


@require_POST
def image_action(request, image_id, action):
    if action != "delete":
        messages.error(request, f"Unknown action: {action}")
        return redirect("panel:dashboard")

    try:
        docker_service.remove_image(image_id)
        messages.success(request, "Image deleted.")
    except DockerServiceError as exc:
        messages.error(request, str(exc))

    return redirect("panel:dashboard")
