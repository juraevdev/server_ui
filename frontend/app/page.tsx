"use client";

import Link from "next/link";
import { Suspense, useCallback, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { PanelLayout } from "@/components/PanelLayout";
import { Message } from "@/components/Messages";
import {
  Container,
  Image,
  containerAction,
  deleteImage,
  fetchDashboard,
} from "@/lib/api";

function DashboardContent() {
  const searchParams = useSearchParams();
  const [containers, setContainers] = useState<Container[]>([]);
  const [images, setImages] = useState<Image[]>([]);
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    setLoading(true);
    const result = await fetchDashboard();
    if (!result.ok) {
      setMessages([{ type: "error", text: result.error }]);
      setContainers([]);
      setImages([]);
    } else {
      const errors = (result.data?.errors || []).map((text) => ({
        type: "error" as const,
        text,
      }));
      setMessages(errors);
      setContainers(result.data?.containers || []);
      setImages(result.data?.images || []);
    }
    setLoading(false);
  }, []);

  useEffect(() => {
    const msg = searchParams.get("message");
    const type = searchParams.get("type");
    if (msg) {
      setMessages([{ type: type === "error" ? "error" : "success", text: msg }]);
    }
    load();
  }, [load, searchParams]);

  async function handleContainerAction(containerId: string, action: string) {
    const result = await containerAction(containerId, action);
    if (!result.ok) {
      setMessages([{ type: "error", text: result.error }]);
      return;
    }
    setMessages([
      { type: "success", text: result.message || `Container ${action} succeeded.` },
    ]);
    await load();
  }

  async function handleDeleteImage(imageId: string) {
    const result = await deleteImage(imageId);
    if (!result.ok) {
      setMessages([{ type: "error", text: result.error }]);
      return;
    }
    setMessages([{ type: "success", text: result.message || "Image deleted." }]);
    await load();
  }

  return (
    <PanelLayout title="Dashboard · Docker Panel" heading="Dashboard" messages={messages}>
      <h2 className="section-title">Containers</h2>
      <div className="card">
        {loading ? (
          <p className="empty">Loading...</p>
        ) : containers.length ? (
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Image</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {containers.map((container) => (
                <tr key={container.id}>
                  <td>
                    <code>{container.id}</code>
                  </td>
                  <td>{container.name}</td>
                  <td>{container.image}</td>
                  <td className="status">{container.status}</td>
                  <td>
                    <div className="btn-group">
                      <button
                        className="btn"
                        type="button"
                        onClick={() => handleContainerAction(container.id, "start")}
                      >
                        Start
                      </button>
                      <button
                        className="btn"
                        type="button"
                        onClick={() => handleContainerAction(container.id, "stop")}
                      >
                        Stop
                      </button>
                      <button
                        className="btn"
                        type="button"
                        onClick={() => handleContainerAction(container.id, "restart")}
                      >
                        Restart
                      </button>
                      <Link
                        className="btn"
                        href={`/containers/${encodeURIComponent(container.id)}/logs`}
                      >
                        Logs
                      </Link>
                      <button
                        className="btn btn-danger"
                        type="button"
                        onClick={() => handleContainerAction(container.id, "delete")}
                      >
                        Delete
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p className="empty">No containers found. Create one to get started.</p>
        )}
      </div>

      <h2 className="section-title">Images</h2>
      <div className="card">
        {loading ? (
          <p className="empty">Loading...</p>
        ) : images.length ? (
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Tags</th>
                <th>Size</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {images.map((image) => (
                <tr key={image.id}>
                  <td>
                    <code>{image.id}</code>
                  </td>
                  <td>{image.tags}</td>
                  <td>{image.size}</td>
                  <td>
                    <button
                      className="btn btn-danger"
                      type="button"
                      onClick={() => handleDeleteImage(image.id)}
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p className="empty">No images found. Pull or build one to get started.</p>
        )}
      </div>
    </PanelLayout>
  );
}

export default function DashboardPage() {
  return (
    <Suspense fallback={<p className="empty wrap">Loading...</p>}>
      <DashboardContent />
    </Suspense>
  );
}
