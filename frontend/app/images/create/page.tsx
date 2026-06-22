"use client";

import Link from "next/link";
import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { PanelLayout } from "@/components/PanelLayout";
import { Message } from "@/components/Messages";
import { createImage } from "@/lib/api";

export default function CreateImagePage() {
  const router = useRouter();
  const [messages, setMessages] = useState<Message[]>([]);
  const [mode, setMode] = useState<"pull" | "build">("pull");
  const [pullName, setPullName] = useState("");
  const [buildTag, setBuildTag] = useState("");
  const [buildPath, setBuildPath] = useState("");
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setSubmitting(true);

    const result = await createImage({
      mode,
      pull_name: pullName,
      build_tag: buildTag,
      build_path: buildPath,
    });

    if (!result.ok) {
      setMessages([{ type: "error", text: result.error }]);
      setSubmitting(false);
      return;
    }

    const msg = encodeURIComponent(result.message || "Image created.");
    router.push(`/?message=${msg}&type=success`);
  }

  return (
    <PanelLayout
      title="Create image · Docker Panel"
      heading="Create image"
      messages={messages}
    >
      <div className="card form-narrow-wide">
        <form onSubmit={handleSubmit}>
          <p className="hint" style={{ marginTop: 0 }}>
            <strong>Pull</strong> — internetdan tayyor image yuklaydi (nginx:latest).
            <br />
            <strong>Build</strong> — kompyuteringizdagi Dockerfile dan yangi image
            yasaydi (test:latest).
          </p>

          <div className="btn-group" style={{ marginBottom: 16 }}>
            <label className="radio-label">
              <input
                type="radio"
                name="mode"
                value="pull"
                checked={mode === "pull"}
                onChange={() => setMode("pull")}
              />
              Pull from registry
            </label>
            <label className="radio-label">
              <input
                type="radio"
                name="mode"
                value="build"
                checked={mode === "build"}
                onChange={() => setMode("build")}
              />
              Build from Dockerfile
            </label>
          </div>

          {mode === "pull" ? (
            <label>
              Image name
              <span className="hint">
                {" "}
                faqat Docker Hub dagi image: nginx:latest, alpine:3.19
              </span>
              <input
                type="text"
                name="pull_name"
                value={pullName}
                onChange={(e) => setPullName(e.target.value)}
                placeholder="nginx:latest"
              />
            </label>
          ) : (
            <>
              <label>
                Image tag
                <span className="hint">
                  {" "}
                  o&apos;zingiz o&apos;ylab topgan nom: test:1.0, myapp:latest
                </span>
                <input
                  type="text"
                  name="build_tag"
                  value={buildTag}
                  onChange={(e) => setBuildTag(e.target.value)}
                  placeholder="myapp:1.0"
                />
              </label>

              <label>
                Build path
                <span className="hint"> folder containing Dockerfile</span>
                <input
                  type="text"
                  name="build_path"
                  value={buildPath}
                  onChange={(e) => setBuildPath(e.target.value)}
                  placeholder="C:\projects\myapp"
                />
              </label>
            </>
          )}

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
