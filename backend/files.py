"""Sample-only permission/preview/approval/move/undo journal. No model authority."""

import hashlib
import json
import os
import secrets
import sqlite3
import stat
import threading
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path, PureWindowsPath


class FilePolicyError(Exception):
    def __init__(self, message: str, status: int = 409):
        self.message, self.status = message, status


def now():
    return datetime.now(UTC).isoformat()


def canonical_json(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def digest(value):
    return hashlib.sha256(canonical_json(value).encode()).hexdigest()


def reject_link(path: Path):
    # Covers symlinks, junctions and all other Windows reparse points.
    try:
        attributes = getattr(path.lstat(), "st_file_attributes", 0)
    except FileNotFoundError:
        attributes = 0
    if path.is_symlink() or attributes & 0x400:
        raise FilePolicyError("Links and Windows reparse points are not allowed.", 403)


class SampleFiles:
    """Bounded sample workspace with persisted permission and write-ahead receipts.

    The model never calls this service. Every move starts from a stored exact plan,
    and permission, source identity and destination are checked again at execution.
    """

    ROOT_ID = "sample-inbox"
    MAX_FILES = 50
    MAX_BYTES = 10 * 1024 * 1024

    def __init__(self, project: Path):
        self.project = project.resolve()
        self.root = self.project / "data/demo/Veto Demo Inbox"
        self.db = self.project / "data/veto.sqlite3"
        self.lock = threading.RLock()
        self.stops: dict[str, threading.Event] = {}
        for path in (self.project, self.project / "data"):
            reject_link(path)
        self.db.parent.mkdir(exist_ok=True)
        reject_link(self.db)
        with self.connect() as conn:
            version = conn.execute("PRAGMA user_version").fetchone()[0]
            if version not in (0, 1):
                raise FilePolicyError(
                    "Unsupported memory database version. Keep it and report the error.",
                    503,
                )
            if version == 0:
                conn.executescript("""
                    CREATE TABLE permission (id INTEGER PRIMARY KEY CHECK(id=1), granted INTEGER NOT NULL, version INTEGER NOT NULL, identity TEXT);
                    INSERT INTO permission VALUES(1,0,0,NULL);
                    CREATE TABLE preference (id INTEGER PRIMARY KEY CHECK(id=1), value TEXT NOT NULL, updated_at TEXT NOT NULL);
                    CREATE TABLE plans (id TEXT PRIMARY KEY, payload TEXT NOT NULL, hash TEXT NOT NULL, state TEXT NOT NULL, token_hash TEXT, created_at TEXT NOT NULL, error TEXT);
                    CREATE TABLE actions (plan_id TEXT NOT NULL, ordinal INTEGER NOT NULL, source TEXT NOT NULL, destination TEXT NOT NULL, identity TEXT NOT NULL, state TEXT NOT NULL, original_plan TEXT, original_ordinal INTEGER, PRIMARY KEY(plan_id,ordinal));
                    PRAGMA user_version=1;
                """)
            # Journal a crash truthfully. Never auto-resume a filesystem operation.
            for row in conn.execute(
                "SELECT * FROM actions WHERE state='moving'"
            ).fetchall():
                state = "failed"
                try:
                    source = self.path(row["source"])
                    dest = self.path(row["destination"])
                    if (
                        not source.exists()
                        and dest.exists()
                        and self.identity(dest) == json.loads(row["identity"])
                    ):
                        state = "done"
                        if row["original_plan"]:
                            conn.execute(
                                "UPDATE actions SET state='undone' WHERE plan_id=? AND ordinal=?",
                                (row["original_plan"], row["original_ordinal"]),
                            )
                except (FilePolicyError, OSError):
                    pass
                conn.execute(
                    "UPDATE actions SET state=? WHERE plan_id=? AND ordinal=?",
                    (state, row["plan_id"], row["ordinal"]),
                )
            conn.execute(
                "UPDATE plans SET state='interrupted',error='Process stopped. Inspect receipts and preview a fresh plan; no automatic retry.' WHERE state='executing'"
            )

    @contextmanager
    def connect(self):
        reject_link(self.db.parent)
        reject_link(self.db)
        conn = sqlite3.connect(self.db, timeout=5)
        conn.row_factory = sqlite3.Row
        try:
            with conn:
                yield conn
        finally:
            conn.close()

    def root_guard(self):
        """Reject redirected or replaced roots before inspecting descendants."""
        current = self.project
        for part in ("data", "demo", "Veto Demo Inbox"):
            current = current / part
            reject_link(current)
        if not self.root.is_dir() or self.root.resolve() != self.root:
            raise FilePolicyError(
                "Sample folder missing or changed. Restore the sample setup.", 403
            )

    def path(self, relative: str) -> Path:
        """Resolve a bounded relative Windows path without following reparse points."""
        self.root_guard()
        windows = PureWindowsPath(relative)
        parts = relative.split("/")
        if (
            not relative
            or windows.is_absolute()
            or windows.drive
            or "\\" in relative
            or len(parts) > 2
            or any(
                p in ("", ".", "..")
                or p.startswith(".")
                or ":" in p
                or p.endswith((" ", "."))
                for p in parts
            )
        ):
            raise FilePolicyError("Only safe relative sample paths are allowed.", 403)
        for part in parts:
            if any(c in part for c in '<>"|?*') or any(ord(c) < 32 for c in part):
                raise FilePolicyError("Unsafe Windows filename.", 403)
            if part.split(".")[0].upper() in {
                "CON",
                "PRN",
                "AUX",
                "NUL",
                *(f"COM{i}" for i in range(1, 10)),
                *(f"LPT{i}" for i in range(1, 10)),
            }:
                raise FilePolicyError("Reserved Windows filename.", 403)
        candidate = self.root
        for part in parts:
            candidate /= part
            reject_link(candidate)
        resolved = candidate.resolve()
        if not resolved.is_relative_to(self.root):
            raise FilePolicyError("Path escapes the sample folder.", 403)
        return candidate

    def identity(self, path: Path):
        """Capture metadata for stale-file detection; this is not a content hash."""
        reject_link(path)
        info = path.stat()
        if not stat.S_ISREG(info.st_mode):
            raise FilePolicyError("Only ordinary sample files may be moved.")
        if getattr(info, "st_file_attributes", 0) & (0x2 | 0x4):
            raise FilePolicyError("Hidden and system files are unavailable.", 403)
        if info.st_size > self.MAX_BYTES:
            raise FilePolicyError("File exceeds the 10 MB sample limit.")
        # Metadata only: file contents are not read for planning or sent to a model.
        return [info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns]

    def root_identity(self):
        self.root_guard()
        info = self.root.stat()
        return [info.st_dev, info.st_ino]

    def permission(self, conn, required=True):
        row = conn.execute("SELECT * FROM permission WHERE id=1").fetchone()
        if required and (
            not row["granted"] or json.loads(row["identity"]) != self.root_identity()
        ):
            raise FilePolicyError(
                "Select and allow the sample folder first. Changed folders require a new grant.",
                403,
            )
        return row

    def set_permission(self, root_id: str, granted: bool):
        """Invalidate older approvals whenever the permission version changes."""
        if root_id != self.ROOT_ID:
            raise FilePolicyError(
                "Only Veto Demo Inbox is available in this build.", 403
            )
        with self.lock, self.connect() as conn:
            identity = canonical_json(self.root_identity()) if granted else None
            conn.execute(
                "UPDATE permission SET granted=?,version=version+1,identity=? WHERE id=1",
                (int(granted), identity),
            )
            conn.execute(
                "UPDATE plans SET state='cancelled',error='Folder permission changed; preview again.' WHERE state IN ('previewed','approved')"
            )
        # Revocation takes effect at the next step; a completed step stays journalled.
        if not granted:
            for event in list(self.stops.values()):
                event.set()
        return self.workspace()

    def preferences(self):
        with self.connect() as conn:
            row = conn.execute("SELECT * FROM preference WHERE id=1").fetchone()
        return {
            "sort_by": row["value"] if row else "file_type",
            "source": "owner" if row else "default",
            "updated_at": row["updated_at"] if row else None,
        }

    def set_preference(self, value: str | None):
        if value not in (None, "file_type", "study"):
            raise FilePolicyError("Unknown sorting preference.", 422)
        with self.lock, self.connect() as conn:
            if value is None:
                conn.execute("DELETE FROM preference WHERE id=1")
            else:
                conn.execute(
                    "INSERT OR REPLACE INTO preference VALUES(1,?,?)", (value, now())
                )
        return self.preferences()

    def workspace(self):
        """List eligible metadata only; do not read file contents or recurse freely."""
        with self.lock, self.connect() as conn:
            granted = bool(self.permission(conn, required=False)["granted"])
            files, skipped = [], []
            if granted:
                self.permission(conn)
                # Flat inbox + one level of known output folders, never arbitrary recursion.
                parents = [self.root]
                for name in ("Documents", "Notes", "Images", "Data"):
                    folder = self.path(name)
                    if folder.is_dir():
                        parents.append(folder)
                seen = 0
                for folder in parents:
                    for file in sorted(
                        folder.iterdir(), key=lambda p: p.name.casefold()
                    ):
                        seen += 1
                        if seen > 200:
                            raise FilePolicyError(
                                "Sample folder listing exceeds 200 entries."
                            )
                        relative = file.relative_to(self.root).as_posix()
                        try:
                            checked = self.path(relative)
                            if checked.is_dir():
                                continue
                            identity = self.identity(checked)
                            files.append({"path": relative, "size": identity[2]})
                        except (FilePolicyError, OSError):
                            skipped.append(relative)
            return {
                "root_id": self.ROOT_ID,
                "label": "Veto Demo Inbox",
                "relative_folder": "data/demo/Veto Demo Inbox",
                "granted": granted,
                "files": files,
                "skipped": skipped,
                "preferences": self.preferences(),
                "sample_only": True,
            }

    @staticmethod
    def category(name: str, preference: str):
        ext = Path(name).suffix.casefold()
        if ext in (".txt", ".md", ".pdf", ".docx"):
            return "Notes" if preference == "study" else "Documents"
        if ext in (".svg", ".png", ".jpg", ".jpeg"):
            return "Images"
        if ext in (".json", ".csv"):
            return "Data"
        return None

    def validate_items(self, payload, conn):
        """Recheck the permission version and every path before approval or movement."""
        permission = self.permission(conn)
        if (
            permission["version"] != payload["permission_version"]
            or self.root_identity() != payload["root_identity"]
        ):
            raise FilePolicyError(
                "Folder permission changed. Create a fresh preview.", 403
            )
        conflicts = []
        for item in payload["items"]:
            try:
                source, dest = self.path(item["source"]), self.path(item["destination"])
                if self.identity(source) != item["identity"]:
                    raise FilePolicyError("Source changed since preview.")
                if dest.exists():
                    raise FilePolicyError(
                        "Destination exists; no overwrite is allowed."
                    )
                if dest.parent.exists() and not dest.parent.is_dir():
                    raise FilePolicyError("Destination parent is not a folder.")
            except (FilePolicyError, OSError) as error:
                conflicts.append(
                    {
                        "source": item["source"],
                        "destination": item["destination"],
                        "reason": error.message
                        if isinstance(error, FilePolicyError)
                        else "File is missing or inaccessible.",
                    }
                )
        return conflicts

    def save_plan(
        self,
        conn,
        items,
        direction,
        permission,
        preference,
        original=None,
        skipped=None,
    ):
        if not items:
            raise FilePolicyError(
                "No eligible moves. Files may already be sorted, unknown, or already undone."
            )
        if (
            len(items) > self.MAX_FILES
            or sum(i["identity"][2] for i in items) > self.MAX_BYTES
        ):
            raise FilePolicyError(
                "Batch exceeds 50 files or 10 MB. No moves were performed."
            )
        payload = {
            "root_id": self.ROOT_ID,
            "root_identity": self.root_identity(),
            "permission_version": permission["version"],
            "direction": direction,
            "preference": preference,
            "original": original,
            "items": items,
            "create_folders": sorted(
                {str(Path(i["destination"]).parent).replace("\\", "/") for i in items}
                - {"."}
            ),
            "skipped": skipped or [],
        }
        plan_id = secrets.token_hex(12)
        conn.execute(
            "INSERT INTO plans VALUES(?,?,?,'previewed',NULL,?,NULL)",
            (plan_id, canonical_json(payload), digest(payload), now()),
        )
        for ordinal, item in enumerate(items):
            conn.execute(
                "INSERT INTO actions VALUES(?,?,?,?,?,'pending',?,?)",
                (
                    plan_id,
                    ordinal,
                    item["source"],
                    item["destination"],
                    canonical_json(item["identity"]),
                    original,
                    item.get("original_ordinal"),
                ),
            )
        conn.commit()
        return self.get_plan(plan_id)

    def preview(self, root_id: str):
        """Persist a deterministic proposal without creating folders or moving files."""
        if root_id != self.ROOT_ID:
            raise FilePolicyError("Unknown sample root.", 403)
        with self.lock, self.connect() as conn:
            permission = self.permission(conn)
            preference = self.preferences()["sort_by"]
            workspace = self.workspace()
            items, skipped = [], list(workspace["skipped"])
            for file in workspace["files"]:
                if "/" in file["path"]:
                    continue
                category = self.category(file["path"], preference)
                if category:
                    items.append(
                        {
                            "source": file["path"],
                            "destination": f"{category}/{file['path']}",
                            "identity": self.identity(self.path(file["path"])),
                        }
                    )
                else:
                    skipped.append(file["path"])
            return self.save_plan(
                conn, items, "sort", permission, preference, skipped=skipped
            )

    def get_plan(self, plan_id: str):
        with self.lock, self.connect() as conn:
            row = conn.execute("SELECT * FROM plans WHERE id=?", (plan_id,)).fetchone()
            if row is None:
                raise FilePolicyError("Plan not found.", 404)
            payload = json.loads(row["payload"])
            conflicts = []
            if row["state"] in ("previewed", "approved"):
                try:
                    conflicts = self.validate_items(payload, conn)
                except FilePolicyError as error:
                    conflicts = [{"reason": error.message}]
            actions = [
                dict(a)
                for a in conn.execute(
                    "SELECT ordinal,source,destination,state FROM actions WHERE plan_id=? ORDER BY ordinal",
                    (plan_id,),
                )
            ]
            return {
                "id": plan_id,
                "hash": row["hash"],
                "state": row["state"],
                "created_at": row["created_at"],
                "error": row["error"],
                **payload,
                "conflicts": conflicts,
                "actions": actions,
            }

    def history(self):
        with self.connect() as conn:
            ids = [
                r[0]
                for r in conn.execute(
                    "SELECT id FROM plans ORDER BY created_at DESC LIMIT 20"
                )
            ]
        return [self.get_plan(i) for i in ids]

    def approve(self, plan_id: str, plan_hash: str):
        """Bind a single-use capability to the stored plan hash, never client paths."""
        with self.lock, self.connect() as conn:
            row = conn.execute("SELECT * FROM plans WHERE id=?", (plan_id,)).fetchone()
            if row is None:
                raise FilePolicyError("Plan not found.", 404)
            payload = json.loads(row["payload"])
            if (
                row["state"] != "previewed"
                or not secrets.compare_digest(row["hash"], plan_hash)
                or digest(payload) != row["hash"]
            ):
                raise FilePolicyError("Approval does not match this current preview.")
            if self.validate_items(payload, conn):
                raise FilePolicyError(
                    "Files changed or a destination is occupied. Review a fresh preview."
                )
            token = secrets.token_urlsafe(32)
            conn.execute(
                "UPDATE plans SET state='approved',token_hash=? WHERE id=?",
                (digest(token), plan_id),
            )
            return {"approval_token": token}

    def cancel(self, plan_id: str):
        with self.lock, self.connect() as conn:
            row = conn.execute(
                "SELECT state FROM plans WHERE id=?", (plan_id,)
            ).fetchone()
            if row is None:
                raise FilePolicyError("Plan not found.", 404)
            if row["state"] not in ("previewed", "approved"):
                raise FilePolicyError("This plan is no longer waiting for approval.")
            conn.execute("UPDATE plans SET state='cancelled' WHERE id=?", (plan_id,))
        return self.get_plan(plan_id)

    def stop(self, plan_id: str):
        event = self.stops.get(plan_id)
        if event is None:
            return self.cancel(plan_id)
        event.set()
        return {"id": plan_id, "state": "stop_requested"}

    def execute(self, plan_id: str, token: str, before_step=None):
        """Execute journalled steps with no overwrite, bounded stop and retry receipts."""
        if os.name != "nt":
            raise FilePolicyError(
                "Real sample moves currently require native Windows.", 503
            )
        with self.lock, self.connect() as conn:
            row = conn.execute("SELECT * FROM plans WHERE id=?", (plan_id,)).fetchone()
            if row is None:
                raise FilePolicyError("Plan not found.", 404)
            if not row["token_hash"] or not secrets.compare_digest(
                row["token_hash"], digest(token)
            ):
                raise FilePolicyError(
                    "A matching exact-plan approval is required.", 403
                )
            if row["state"] in ("done", "failed", "cancelled", "interrupted", "undone"):
                return self.get_plan(
                    plan_id
                )  # Identical retry returns receipts, never moves twice.
            if row["state"] != "approved":
                raise FilePolicyError("This plan is already executing or not approved.")
            payload = json.loads(row["payload"])
            if digest(payload) != row["hash"] or self.validate_items(payload, conn):
                raise FilePolicyError("Preview is stale. No moves were started.")
            event = self.stops[plan_id] = threading.Event()
            conn.execute("UPDATE plans SET state='executing' WHERE id=?", (plan_id,))
        final_state, message = "done", None
        try:
            for ordinal, item in enumerate(payload["items"]):
                if before_step:
                    before_step(ordinal)  # Test hook only; not exposed to API/model.
                with self.lock, self.connect() as conn:
                    if event.is_set():
                        final_state = "cancelled"
                        message = "Stopped between steps. Completed moves remain available for undo."
                        break
                    subset = {**payload, "items": [item]}
                    if self.validate_items(subset, conn):
                        raise FilePolicyError(
                            "A file changed or a destination is occupied. Remaining moves stopped."
                        )
                    source, dest = (
                        self.path(item["source"]),
                        self.path(item["destination"]),
                    )
                    if not dest.parent.exists():
                        dest.parent.mkdir()  # Exactly the folder included in the approved plan.
                    source, dest = (
                        self.path(item["source"]),
                        self.path(item["destination"]),
                    )
                    if self.identity(source) != item["identity"] or dest.exists():
                        raise FilePolicyError(
                            "Files changed immediately before execution; move denied."
                        )
                    conn.execute(
                        "UPDATE actions SET state='moving' WHERE plan_id=? AND ordinal=?",
                        (plan_id, ordinal),
                    )
                    conn.commit()  # Write-ahead receipt permits crash reconciliation.
                    os.rename(
                        source, dest
                    )  # Windows atomically refuses an existing destination.
                    conn.execute(
                        "UPDATE actions SET state='done' WHERE plan_id=? AND ordinal=?",
                        (plan_id, ordinal),
                    )
                    if payload["direction"] == "undo":
                        conn.execute(
                            "UPDATE actions SET state='undone' WHERE plan_id=? AND ordinal=?",
                            (payload["original"], item["original_ordinal"]),
                        )
        except (FilePolicyError, OSError):
            final_state = "failed"
            message = "Move blocked or inaccessible. Inspect receipts; no overwrite or automatic retry was performed."
            # The attempted rename failed, or its journal needs startup reconciliation.
            with self.connect() as conn:
                for action in conn.execute(
                    "SELECT * FROM actions WHERE plan_id=? AND state='moving'",
                    (plan_id,),
                ).fetchall():
                    state = "failed"
                    try:
                        src, dst = (
                            self.path(action["source"]),
                            self.path(action["destination"]),
                        )
                        if (
                            not src.exists()
                            and dst.exists()
                            and self.identity(dst) == json.loads(action["identity"])
                        ):
                            state = "done"
                    except (OSError, FilePolicyError):
                        pass
                    conn.execute(
                        "UPDATE actions SET state=? WHERE plan_id=? AND ordinal=?",
                        (state, plan_id, action["ordinal"]),
                    )
        finally:
            with self.lock, self.connect() as conn:
                conn.execute(
                    "UPDATE plans SET state=?,error=? WHERE id=?",
                    (final_state, message, plan_id),
                )
                if payload["original"]:
                    remaining = conn.execute(
                        "SELECT count(*) FROM actions WHERE plan_id=? AND state='done'",
                        (payload["original"],),
                    ).fetchone()[0]
                    if remaining == 0:
                        conn.execute(
                            "UPDATE plans SET state='undone' WHERE id=?",
                            (payload["original"],),
                        )
                self.stops.pop(plan_id, None)
        return self.get_plan(plan_id)

    def preview_undo(self, plan_id: str):
        """Propose inverse moves only for confirmed steps whose files remain unchanged."""
        with self.lock, self.connect() as conn:
            permission = self.permission(conn)
            plan = conn.execute(
                "SELECT payload,state FROM plans WHERE id=?", (plan_id,)
            ).fetchone()
            if plan is None:
                raise FilePolicyError("Plan not found.", 404)
            if json.loads(plan["payload"])["direction"] != "sort" or plan[
                "state"
            ] not in ("done", "cancelled", "failed", "interrupted"):
                raise FilePolicyError("Only completed sorting steps can be undone.")
            items = []
            for row in conn.execute(
                "SELECT * FROM actions WHERE plan_id=? AND state='done' ORDER BY ordinal DESC",
                (plan_id,),
            ):
                items.append(
                    {
                        "source": row["destination"],
                        "destination": row["source"],
                        "identity": json.loads(row["identity"]),
                        "original_ordinal": row["ordinal"],
                    }
                )
            return self.save_plan(
                conn,
                items,
                "undo",
                permission,
                self.preferences()["sort_by"],
                original=plan_id,
            )
