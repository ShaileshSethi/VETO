// Shared local API contracts. Credentials and file contents never enter these types.
export type Status = {
  ready: boolean;
  provider: string;
  model: string;
  session: string;
  mode: "mock" | "nebius";
};
export type Answer = {
  answer: string;
  model: string;
  mode: string;
  latency_ms: number;
  request_id?: string;
  usage: { prompt_tokens?: number; completion_tokens?: number };
};
export type Preference = {
  sort_by: string;
  source: string;
  updated_at: string | null;
};
export type Workspace = {
  root_id: string;
  relative_folder: string;
  granted: boolean;
  files: { path: string; size: number }[];
  skipped: string[];
  preferences: Preference;
};
export type Plan = {
  id: string;
  hash: string;
  state: string;
  direction: string;
  preference: string;
  error: string | null;
  created_at: string;
  create_folders: string[];
  skipped: string[];
  items: { source: string; destination: string; identity: number[] }[];
  conflicts: { reason: string }[];
  actions: { source: string; destination: string; state: string }[];
};
