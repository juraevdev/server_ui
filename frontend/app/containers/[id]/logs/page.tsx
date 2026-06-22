"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { PanelLayout } from "@/components/PanelLayout";
import { Message } from "@/components/Messages";
import { fetchContainerLogs } from "@/lib/api";

export default function ContainerLogsPage() {
  const params = useParams<{ id: string }>();
  const containerId = decodeURIComponent(params.id);
  const [messages, setMessages] = useState<Message[]>([]);
  const [containerName, setContainerName] = useState(containerId);
  const [logs, setLogs] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      const result = await fetchContainerLogs(containerId);
      if (!result.ok) {
        setMessages([{ type: "error", text: result.error }]);
        setLoading(false);
        return;
      }
      setContainerName(result.data?.container_name || containerId);
      setLogs(result.data?.logs || "");
      setLoading(false);
    }
    load();
  }, [containerId]);

  return (
    <PanelLayout
      title={`Logs · ${containerName}`}
      heading={`Logs: ${containerName}`}
      messages={messages}
      headerActions={
        <Link className="btn" href="/">
          Back to dashboard
        </Link>
      }
    >
      <div className="card">
        <p className="hint" style={{ marginTop: 0 }}>
          Container <code>{containerId}</code> — recent log output
        </p>
        <pre className="logs">
          {loading ? "Loading..." : logs || "(no logs)"}
        </pre>
      </div>
    </PanelLayout>
  );
}
