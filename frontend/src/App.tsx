import { useEffect, useState } from "react";
import { ChatPanel } from "./components/ChatPanel";
import { FilesPanel } from "./components/FilesPanel";
import type { Status } from "./types";
export function App() {
  const [status, setStatus] = useState<Status>();
  const [tab, setTab] = useState<"chat" | "files">("chat");
  const [error, setError] = useState("");
  useEffect(() => {
    fetch("/api/status")
      .then(async (r) => {
        if (!r.ok)
          throw new Error("Backend unavailable. Restart Veto and refresh.");
        setStatus(await r.json());
      })
      .catch((e) => setError(e.message));
  }, []);
  return (
    <main>
      <header>
        <a className="brand" href="/" aria-label="Veto home">
          veto<span>●</span>
        </a>
        <span className="pill">LOCAL SAMPLE WORKSPACE</span>
      </header>
      <section className="intro">
        <p className="eyebrow">YOUR LAPTOP. YOUR CALL.</p>
        <h1>
          A little clarity.
          <br />
          Every move, your choice.
        </h1>
        <p className="description">
          Explore Veto with sample files.
          <br />
          Preview first. Approve once. Keep an undo path.
        </p>
      </section>
      <aside
        className={status?.mode === "nebius" ? "live-banner" : "mode-banner"}
      >
        <strong>
          {!status
            ? "Loading local configuration…"
            : status.mode === "mock"
              ? "MOCK MODE · sample replies · no API calls"
              : "NEBIUS MODE · questions use cloud inference"}
        </strong>
        <p>
          Live NVIDIA/Nebius testing is still pending.{" "}
          {status?.mode === "mock"
            ? "Sorting moves real sample files after approval. No key or credits needed."
            : "Sorting stays local and uses fixed rules."}{" "}
          Voice is off.
        </p>
      </aside>
      <nav className="tabs" aria-label="Veto sections">
        <button
          type="button"
          aria-pressed={tab === "chat"}
          onClick={() => setTab("chat")}
        >
          Sample chat
        </button>
        <button
          type="button"
          aria-pressed={tab === "files"}
          onClick={() => setTab("files")}
        >
          Sample files & memory
        </button>
      </nav>
      {error && (
        <div className="error" role="alert">
          {error}
        </div>
      )}
      {status &&
        (tab === "chat" ? (
          <ChatPanel status={status} />
        ) : (
          <FilesPanel session={status.session} />
        ))}
      <section className="boundaries">
        <article>
          <span>01 / MODEL</span>
          <h3>{status?.provider ?? "Loading…"}</h3>
          <p>
            {status?.model ?? "Loading configuration…"} · live milestone pending
          </p>
        </article>
        <article>
          <span>02 / ACCESS</span>
          <h3>Generated samples only</h3>
          <p>Folder permission, exact approval, local receipts and undo.</p>
        </article>
        <article>
          <span>03 / MICROPHONE</span>
          <h3>Voice is off</h3>
          <p>No listener, settings control, or startup service.</p>
        </article>
      </section>
      <footer>
        <span>Small steps. Clear permissions.</span>
        <span>Mock development · live integration pending</span>
      </footer>
    </main>
  );
}
