const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000/api";

export type Container = {
  id: string;
  name: string;
  image: string;
  status: string;
};

export type Image = {
  id: string;
  tags: string;
  size: string;
};

type ApiSuccess<T> = { ok: true; data?: T; message?: string };
type ApiError = { ok: false; error: string };

async function request<T>(
  path: string,
  options?: RequestInit,
): Promise<ApiSuccess<T> | ApiError> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options?.headers || {}),
    },
  });

  const payload = await response.json();
  if (!response.ok || !payload.ok) {
    return { ok: false, error: payload.error || "Request failed." };
  }
  return payload;
}

export async function fetchDashboard() {
  return request<{
    containers: Container[];
    images: Image[];
    errors: string[];
  }>("/dashboard/");
}

export async function createContainer(body: {
  image: string;
  name: string;
  port_mapping?: string;
}) {
  return request<{ id: string }>("/containers/", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export async function containerAction(containerId: string, action: string) {
  return request(`/containers/${encodeURIComponent(containerId)}/${action}/`, {
    method: "POST",
  });
}

export async function fetchContainerLogs(containerId: string) {
  return request<{
    container_id: string;
    container_name: string;
    logs: string;
  }>(`/containers/${encodeURIComponent(containerId)}/logs/`);
}

export async function createImage(body: {
  mode: "pull" | "build";
  pull_name?: string;
  build_tag?: string;
  build_path?: string;
}) {
  return request<{ id: string }>("/images/", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export async function deleteImage(imageId: string) {
  return request(`/images/${encodeURIComponent(imageId)}/delete/`, {
    method: "POST",
  });
}
