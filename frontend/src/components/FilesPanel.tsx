import { useCallback, useEffect, useState } from "react";
import { api, errorMessage } from "../api";
import type { Plan, Workspace } from "../types";
/** The backend journal is authoritative; UI state only selects and displays plans. */
export function FilesPanel({ session }: { session: string }) {
  const [workspace, setWorkspace] = useState<Workspace>();
  const [history, setHistory] = useState<Plan[]>([]);
  const [plan, setPlan] = useState<Plan>();
  const [selected, setSelected] = useState("");
  const [preference, setPreference] = useState("file_type");
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [busy, setBusy] = useState(false);
  const [exported, setExported] = useState("");
  const refresh = useCallback(async () => {
    const [w, h] = await Promise.all([
      api<Workspace>("/workspace", session),
      api<Plan[]>("/plans", session),
    ]);
    setWorkspace(w);
    setHistory(h);
    setPreference(w.preferences.sort_by);
  }, [session]);
  useEffect(() => {
    refresh().catch((e) => setError(e.message));
  }, [refresh]);
  // Poll receipts only while this screen owns an active operation.
  const planId = plan?.id;
  useEffect(() => {
    if (!busy || !planId) return;
    let active = true;
    const controller = new AbortController();
    const timer = window.setInterval(() => {
      api<Plan>(
        `/plans/${planId}`,
        session,
        "GET",
        undefined,
        controller.signal,
      )
        .then((receipt) => {
          if (active) setPlan(receipt);
        })
        .catch((error) => {
          if (active) setError(errorMessage(error));
        });
    }, 350);
    return () => {
      // Prevent an old poll from replacing a final receipt or an unmounted view.
      active = false;
      controller.abort();
      window.clearInterval(timer);
    };
  }, [busy, planId, session]);
  async function action(operation: () => Promise<void>) {
    setBusy(true);
    setError("");
    setNotice("");
    try {
      await operation();
      await refresh();
    } catch (e) {
      setError(
        e instanceof Error ? e.message : "Action failed. Inspect receipts.",
      );
    } finally {
      setBusy(false);
    }
  }
  async function allow(granted: boolean) {
    await api("/permission", session, "POST", {
      root_id: granted ? selected : workspace?.root_id,
      granted,
    });
    setPlan(undefined);
    setNotice(
      granted
        ? "Sample folder allowed. Preview before any move."
        : "Permission revoked. Waiting approvals are cancelled.",
    );
  }
  async function execute() {
    if (!plan) return;
    // Approval binds the displayed hash; execution never accepts replacement paths.
    const approval = await api<{ approval_token: string }>(
      `/plans/${plan.id}/approve`,
      session,
      "POST",
      { plan_hash: plan.hash },
    );
    const result = await api<Plan>(
      `/plans/${plan.id}/execute`,
      session,
      "POST",
      { approval_token: approval.approval_token },
    );
    setPlan(result);
    setNotice(
      result.state === "done"
        ? result.direction === "undo"
          ? "Undo completed. Original files restored; empty sorting folders remain."
          : "Approved sample files moved. Review receipts or preview undo."
        : (result.error ?? "Inspect action receipts."),
    );
  }
  return (
    <>
      <section className="workspace" aria-label="Folder permissions">
        <div className="panel-heading">
          <h2>Folder permissions</h2>
          <span className="pill">SAMPLE FILES ONLY</span>
        </div>
        <p>
          Veto starts with no folder access. Only its generated inbox is
          offered; personal folders cannot be added.
        </p>
        <p className="folder-path">
          {workspace?.relative_folder ?? "Loading sample folder…"}
        </p>
        {workspace?.granted ? (
          <div className="row">
            <span className="allowed">✓ Veto Demo Inbox is allowed</span>
            <button
              type="button"
              className="secondary"
              onClick={() => action(() => allow(false))}
            >
              Revoke sample permission
            </button>
          </div>
        ) : (
          <div className="row">
            <div>
              <label htmlFor="sample-root">Choose a sample folder</label>
              <select
                id="sample-root"
                value={selected}
                onChange={(e) => setSelected(e.target.value)}
                disabled={busy}
              >
                <option value="">Select a folder…</option>
                <option value="sample-inbox">
                  Veto Demo Inbox (generated samples)
                </option>
              </select>
            </div>
            <button
              type="button"
              disabled={busy || !selected}
              onClick={() => action(() => allow(true))}
            >
              Allow selected sample folder
            </button>
          </div>
        )}
        <p className="disclosure">
          Permission allows local filename metadata and approved sample moves.
          No file contents or filenames are sent to Nebius. Revoke permission at
          any time.
        </p>
      </section>
      <section className="workspace spaced" aria-label="Sorting preferences">
        <h2>Sorting preference</h2>
        <p>This choice stays on your laptop and survives a restart.</p>
        <div className="row">
          <div>
            <label htmlFor="sort-by">Group documents into</label>
            <select
              id="sort-by"
              value={preference}
              onChange={(e) => setPreference(e.target.value)}
              disabled={busy}
            >
              <option value="file_type">Documents · by file type</option>
              <option value="study">Notes · study grouping</option>
            </select>
          </div>
          <button
            type="button"
            disabled={busy}
            onClick={() =>
              action(async () => {
                await api("/preferences", session, "PUT", {
                  sort_by: preference,
                });
                setNotice("Sorting preference saved locally.");
              })
            }
          >
            Save preference
          </button>
          <button
            type="button"
            className="secondary"
            disabled={busy}
            onClick={() =>
              action(async () => {
                await api("/preferences", session, "DELETE");
                setNotice("Stored preference removed; default restored.");
              })
            }
          >
            Reset preference
          </button>
          <button
            type="button"
            className="secondary"
            disabled={busy}
            onClick={() =>
              action(async () => {
                setExported(
                  JSON.stringify(
                    await api("/preferences/export", session),
                    null,
                    2,
                  ),
                );
              })
            }
          >
            Export preference
          </button>
        </div>
        <p className="disclosure">
          Source: {workspace?.preferences.source ?? "loading"} · Last saved:{" "}
          {workspace?.preferences.updated_at
            ? new Date(workspace.preferences.updated_at).toLocaleString()
            : "default, not saved"}
        </p>
        {exported && <pre className="export">{exported}</pre>}
      </section>
      <section className="workspace spaced" aria-label="Sample files">
        <div className="panel-heading">
          <h2>Sample files</h2>
          <div className="row">
            <button
              type="button"
              className="secondary"
              disabled={busy}
              onClick={() => action(refresh)}
            >
              Refresh files
            </button>
            <button
              type="button"
              disabled={busy || !workspace?.granted}
              onClick={() =>
                action(async () => {
                  setPlan(
                    await api<Plan>("/plans/preview", session, "POST", {
                      root_id: workspace?.root_id,
                    }),
                  );
                })
              }
            >
              Preview sorting
            </button>
          </div>
        </div>
        {!workspace?.granted ? (
          <p>Allow the sample folder above to view files.</p>
        ) : (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th scope="col">Current relative path</th>
                  <th scope="col">Size</th>
                </tr>
              </thead>
              <tbody>
                {workspace.files.map((file) => (
                  <tr key={file.path}>
                    <td>{file.path}</td>
                    <td>{file.size} bytes</td>
                  </tr>
                ))}
              </tbody>
            </table>
            {workspace.files.length === 0 && <p>No eligible sample files.</p>}
          </div>
        )}
        {!!workspace?.skipped.length && (
          <p className="disclosure">
            Skipped unsafe or inaccessible entries:{" "}
            {workspace.skipped.join(", ")}
          </p>
        )}
      </section>
      {error && (
        <div className="error" role="alert">
          {error}
        </div>
      )}
      {notice && (
        <p className="notice" role="status">
          {notice}
        </p>
      )}
      {plan && (
        <section className="workspace spaced" aria-label="Exact action preview">
          <div className="panel-heading">
            <h2>
              {plan.direction === "undo" ? "Undo preview" : "Sorting preview"}
            </h2>
            <span className="pill">{plan.state.toUpperCase()}</span>
          </div>
          <p>
            {plan.items.length} real sample moves ·{" "}
            {plan.items.reduce((n, i) => n + i.identity[2], 0)} bytes · Veto
            Demo Inbox · rule: {plan.preference}
          </p>
          <p className="disclosure">
            Fixed local rules, not an AI-generated plan.{" "}
            {plan.create_folders.length
              ? `Create/use folders: ${plan.create_folders.join(", ")}.`
              : ""}{" "}
            No overwrite or deletion.
          </p>
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th scope="col">From</th>
                  <th scope="col">To</th>
                  <th scope="col">Receipt</th>
                </tr>
              </thead>
              <tbody>
                {plan.actions.map((item) => (
                  <tr key={item.source}>
                    <td>{item.source}</td>
                    <td>{item.destination}</td>
                    <td>{item.state}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {plan.skipped.length > 0 && (
            <p className="disclosure">Left alone: {plan.skipped.join(", ")}</p>
          )}
          {plan.conflicts.length > 0 && (
            <div className="error" role="alert">
              Approval blocked: {plan.conflicts.map((c) => c.reason).join(" ")}
            </div>
          )}
          {plan.error && <p className="error">{plan.error}</p>}
          <p className="plan-hash">Exact plan: {plan.hash}</p>
          <div className="row">
            {plan.state === "previewed" && (
              <>
                <button
                  type="button"
                  disabled={busy || !!plan.conflicts.length}
                  onClick={() => action(execute)}
                >
                  Approve exact {plan.direction === "undo" ? "undo" : "moves"}
                </button>
                <button
                  type="button"
                  className="secondary"
                  disabled={busy}
                  onClick={() =>
                    action(async () => {
                      setPlan(
                        await api<Plan>(
                          `/plans/${plan.id}/cancel`,
                          session,
                          "POST",
                        ),
                      );
                      setNotice("Plan cancelled. No moves will run.");
                    })
                  }
                >
                  Cancel plan
                </button>
              </>
            )}
            {busy && (
              <button
                type="button"
                className="secondary"
                onClick={async () => {
                  try {
                    await api(`/plans/${plan.id}/stop`, session, "POST");
                    setNotice(
                      "Stop requested. An in-flight move may finish; inspect receipts.",
                    );
                  } catch (e) {
                    setError(e instanceof Error ? e.message : "Stop failed.");
                  }
                }}
              >
                Stop remaining moves
              </button>
            )}
          </div>
        </section>
      )}
      <section className="workspace spaced" aria-label="Action history">
        <h2>Activity and undo</h2>
        <p>
          Receipts are saved locally. Undo also needs an exact preview and
          approval.
        </p>
        {history.length === 0 && <p>No plans yet.</p>}
        {history.map((item) => (
          <article className="history-row" key={item.id}>
            <div>
              <strong>
                {item.direction === "undo" ? "Undo" : "Sort"} · {item.state}
              </strong>
              <small>
                {new Date(item.created_at).toLocaleString()} ·{" "}
                {
                  item.actions.filter(
                    (a) => a.state === "done" || a.state === "undone",
                  ).length
                }
                /{item.actions.length} confirmed steps
              </small>
            </div>
            <div className="row">
              <button
                type="button"
                className="secondary"
                disabled={busy}
                onClick={() =>
                  action(async () => {
                    setPlan(await api<Plan>(`/plans/${item.id}`, session));
                  })
                }
              >
                View plan
              </button>
              {item.direction === "sort" &&
                ["done", "failed", "cancelled", "interrupted"].includes(
                  item.state,
                ) &&
                item.actions.some((a) => a.state === "done") && (
                  <button
                    type="button"
                    disabled={busy || !workspace?.granted}
                    onClick={() =>
                      action(async () => {
                        setPlan(
                          await api<Plan>(
                            `/plans/${item.id}/undo-preview`,
                            session,
                            "POST",
                          ),
                        );
                      })
                    }
                  >
                    Preview undo
                  </button>
                )}
            </div>
          </article>
        ))}
      </section>
    </>
  );
}
