from django.urls import path

from panel import views

app_name = "panel"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("create/", views.create_container, name="create"),
    path("images/create/", views.create_image, name="create_image"),
    path(
        "images/<str:image_id>/<str:action>/",
        views.image_action,
        name="image_action",
    ),
    path(
        "containers/<str:container_id>/logs/",
        views.container_logs,
        name="logs",
    ),
    path(
        "containers/<str:container_id>/<str:action>/",
        views.container_action,
        name="action",
    ),
]
