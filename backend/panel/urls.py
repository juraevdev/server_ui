from django.urls import path

from panel import views

app_name = "panel"

urlpatterns = [
    path("health/", views.health, name="health"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("containers/", views.create_container, name="create_container"),
    path(
        "containers/<str:container_id>/logs/",
        views.container_logs,
        name="container_logs",
    ),
    path(
        "containers/<str:container_id>/<str:action>/",
        views.container_action,
        name="container_action",
    ),
    path("images/", views.create_image, name="create_image"),
    path(
        "images/<str:image_id>/<str:action>/",
        views.image_action,
        name="image_action",
    ),
]
