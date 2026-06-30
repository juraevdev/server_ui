from rest_framework import serializers


class ApiErrorSerializer(serializers.Serializer):
    ok = serializers.BooleanField(default=False)
    error = serializers.CharField()


class HealthDataSerializer(serializers.Serializer):
    status = serializers.CharField()


class HealthResponseSerializer(serializers.Serializer):
    ok = serializers.BooleanField(default=True)
    data = HealthDataSerializer()


class ContainerSerializer(serializers.Serializer):
    id = serializers.CharField()
    name = serializers.CharField()
    image = serializers.CharField()
    status = serializers.CharField()
    managed = serializers.BooleanField(required=False)


class ImageSerializer(serializers.Serializer):
    id = serializers.CharField()
    tags = serializers.CharField()
    size = serializers.CharField()


class DashboardDataSerializer(serializers.Serializer):
    containers = ContainerSerializer(many=True)
    images = ImageSerializer(many=True)
    errors = serializers.ListField(child=serializers.CharField())
    docker_mode = serializers.ChoiceField(choices=["host", "isolated"])


class DashboardResponseSerializer(serializers.Serializer):
    ok = serializers.BooleanField(default=True)
    data = DashboardDataSerializer()


class CreateContainerRequestSerializer(serializers.Serializer):
    image = serializers.CharField(help_text="Docker image name, e.g. nginx:latest")
    name = serializers.CharField(help_text="Container name")
    port_mapping = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Port mapping, e.g. 8080:80",
    )


class CreateContainerDataSerializer(serializers.Serializer):
    id = serializers.CharField()


class CreateContainerResponseSerializer(serializers.Serializer):
    ok = serializers.BooleanField(default=True)
    data = CreateContainerDataSerializer()
    message = serializers.CharField()


class ContainerLogsDataSerializer(serializers.Serializer):
    container_id = serializers.CharField()
    container_name = serializers.CharField()
    logs = serializers.CharField()


class ContainerLogsResponseSerializer(serializers.Serializer):
    ok = serializers.BooleanField(default=True)
    data = ContainerLogsDataSerializer()


class ActionResponseSerializer(serializers.Serializer):
    ok = serializers.BooleanField(default=True)
    message = serializers.CharField()


class CreateImageRequestSerializer(serializers.Serializer):
    mode = serializers.ChoiceField(
        choices=["pull", "build"],
        help_text="pull: download from registry; build: build from Dockerfile",
    )
    pull_name = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Required when mode=pull",
    )
    build_tag = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Required when mode=build",
    )
    build_path = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Required when mode=build",
    )


class CreateImageDataSerializer(serializers.Serializer):
    id = serializers.CharField()


class CreateImageResponseSerializer(serializers.Serializer):
    ok = serializers.BooleanField(default=True)
    data = CreateImageDataSerializer()
    message = serializers.CharField()
