"use client";

import Link from "next/link";
import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { PanelLayout } from "@/components/PanelLayout";
import { Message } from "@/components/Messages";
import { createContainer } from "@/lib/api";

export default function CreateContainerPage() {
  const router = useRouter();
  const [messages, setMessages] = useState<Message[]>([]);
  const [image, setImage] = useState("");
  const [name, setName] = useState("");
  const [portMapping, setPortMapping] = useState("");
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setSubmitting(true);

    const result = await createContainer({
      image,
      name,
      port_mapping: portMapping,
    });

    if (!result.ok) {
      setMessages([{ type: "error", text: result.error }]);
      setSubmitting(false);
      return;
    }

    const msg = encodeURIComponent(
      result.message || `Container created (${result.data?.id}).`,
    );
    router.push(`/?message=${msg}&type=success`);
  }

  return (
    <PanelLayout
      title="Create container · Docker Panel"
      heading="Create container"
      messages={messages}
    >
      <div className="card form-narrow">
        <form onSubmit={handleSubmit}>
          <label>
            Image
            <span className="hint"> e.g. nginx:latest</span>
            <input
              type="text"
              name="image"
              value={image}
              onChange={(e) => setImage(e.target.value)}
              placeholder="nginx:latest"
              required
            />
          </label>

          <label>
            Container name
        <span className="hint"> will be prefixed with panel- on server</span>
            <input
              type="text"
              name="name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="my-nginx"
              required
            />
          </label>

          <label>
            Port mapping
            <span className="hint"> optional, host:container — e.g. 8081:80</span>
            <input
              type="text"
              name="port_mapping"
              value={portMapping}
              onChange={(e) => setPortMapping(e.target.value)}
              placeholder="8081:80"
            />
          </label>

          <div className="btn-group">
            <button className="btn btn-primary" type="submit" disabled={submitting}>
              {submitting ? "Creating..." : "Create"}
            </button>
            <Link className="btn" href="/">
              Cancel
            </Link>
          </div>
        </form>
      </div>
    </PanelLayout>
  );
}
