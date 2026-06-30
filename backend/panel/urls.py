from django.urls import path

from panel import views

app_name = "panel"

urlpatterns = [
    path("health/", views.HealthView.as_view(), name="health"),
    path("dashboard/", views.DashboardView.as_view(), name="dashboard"),
    path("containers/", views.CreateContainerView.as_view(), name="create_container"),
    path(
        "containers/<str:container_id>/logs/",
        views.ContainerLogsView.as_view(),
        name="container_logs",
    ),
    path(
        "containers/<str:container_id>/<str:action>/",
        views.ContainerActionView.as_view(),
        name="container_action",
    ),
    path("images/", views.CreateImageView.as_view(), name="create_image"),
    path(
        "images/<str:image_id>/<str:action>/",
        views.ImageActionView.as_view(),
        name="image_action",
    ),
]
