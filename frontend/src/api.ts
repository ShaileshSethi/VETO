/** Same-origin requests carry the per-process token, never the Nebius API key. */
export function errorMessage(error: unknown): string {
  return error instanceof Error
    ? error.message
    : "Request failed. Inspect receipts before retrying.";
}
export async function api<T>(
  path: string,
  session: string,
  method = "GET",
  body?: unknown,
  signal?: AbortSignal,
): Promise<T> {
  const response = await fetch(`/api${path}`, {
    method,
    signal,
    headers: { "Content-Type": "application/json", "X-Veto-Session": session },
    ...(body === undefined ? {} : { body: JSON.stringify(body) }),
  });
  // A stopped backend or proxy can return non-JSON; keep the message actionable.
  let data;
  try {
    data = await response.json();
  } catch {
    throw new Error(
      "Backend returned an unreadable response. Restart Veto and refresh.",
    );
  }
  if (!response.ok)
    throw new Error(
      typeof data?.detail === "string"
        ? data.detail
        : "Request rejected. Review the input and try again.",
    );
  return data;
}
