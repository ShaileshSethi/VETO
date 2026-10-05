import { type FormEvent, useState } from "react";
import { api } from "../api";
import type { Answer, Status } from "../types";
/** Text replies have no authority to approve or execute file operations. */
export function ChatPanel({ status }: { status: Status }) {
  const [prompt, setPrompt] = useState("");
  const [answer, setAnswer] = useState<Answer>();
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  async function submit(event: FormEvent) {
    event.preventDefault();
    if (busy) return;
    setBusy(true);
    setError("");
    setAnswer(undefined);
    try {
      setAnswer(await api<Answer>("/chat", status.session, "POST", { prompt }));
    } catch (e) {
      setError(e instanceof Error ? e.message : "Request failed.");
    } finally {
      setBusy(false);
    }
  }
  const mock = status.mode === "mock";
  return (
    <section className="workspace" aria-label="Ask Veto">
      <div className="panel-heading">
        <h2>Ask Veto</h2>
        <span className="state">
          {busy
            ? "Waiting…"
            : mock
              ? "Mock ready · no credits needed"
              : status.ready
                ? "Key configured · live testing pending"
                : "Key setup needed"}
        </span>
      </div>
      <form onSubmit={submit}>
        <label htmlFor="question">Your question</label>
        <textarea
          id="question"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          maxLength={2000}
          placeholder="How do I sort the sample files?"
          rows={3}
          required
          disabled={busy}
        />
        <p className="disclosure">
          {mock
            ? "Mock mode returns fixed sample replies locally. No API calls or charges. This question cannot execute file actions."
            : "Send transmits this question to Nebius. Use sample text only. File sorting uses the separate local preview and approval controls."}
        </p>
        <div className="form-bottom">
          <span>{prompt.length} / 2,000</span>
          <button disabled={busy || !prompt.trim()} type="submit">
            {busy ? "Waiting…" : mock ? "Get sample reply" : "Send to Nebius ↗"}
          </button>
        </div>
      </form>
      {!status.ready && (
        <aside className="setup">
          Enter your key only in the local .env file, then restart Veto. Never
          paste it into chat.
        </aside>
      )}
      {error && (
        <div className="error" role="alert">
          {error}
        </div>
      )}
      {answer && (
        <section className="answer" aria-live="polite">
          <h3>
            {answer.mode === "mock"
              ? "MOCK · sample reply — no API call"
              : "Live Nebius response"}
          </h3>
          <p>{answer.answer}</p>
          <small>
            {answer.model}
            {answer.mode !== "mock" && (
              <>
                {" "}
                · {answer.latency_ms} ms
                <br />
                Request: {answer.request_id ?? "unreported"}
                <br />
                Tokens: {answer.usage?.prompt_tokens ?? "unreported"} in /{" "}
                {answer.usage?.completion_tokens ?? "unreported"} out
              </>
            )}
          </small>
        </section>
      )}
    </section>
  );
}
