import asyncio
import logging
import os
import secrets
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, Field, StrictBool, field_validator
from starlette.middleware.trustedhost import TrustedHostMiddleware

from backend.provider import ModelProvider, MockProvider, NebiusProvider, ProviderError, Settings
from backend.files import SampleFiles, FilePolicyError

ROOT = Path(__file__).resolve().parents[1]
ORIGINS = {"http://127.0.0.1:8765", "http://localhost:8765"}
logger = logging.getLogger("veto")
logger.setLevel(logging.INFO)
if not logger.handlers:
    logger.addHandler(logging.StreamHandler())


class ChatInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    prompt: str = Field(min_length=1, max_length=2000)

    @field_validator("prompt")
    @classmethod
    def nonblank(cls, value):
        if not value.strip():
            raise ValueError("Enter a question")
        return value.strip()


class PermissionInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    root_id: str = Field(max_length=40)
    granted: StrictBool


class RootInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    root_id: str = Field(max_length=40)


class ApprovalInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    plan_hash: str = Field(min_length=64, max_length=64)


class ExecuteInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    approval_token: str = Field(min_length=1, max_length=128)


class PreferenceInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    sort_by: str = Field(max_length=20)


def create_app(settings: Settings | None = None, provider: ModelProvider | None = None, file_store: SampleFiles | None = None):
    if settings is None:
        load_dotenv(ROOT / ".env", override=False)
        settings = Settings(os.getenv("NEBIUS_API_KEY", ""), os.getenv("NEBIUS_MODEL", Settings.model),
                            os.getenv("NEBIUS_BASE_URL", Settings.base_url), os.getenv("VETO_MODE", "mock").lower())
    if settings.mode not in ('mock', 'nebius'):
        raise ValueError('VETO_MODE must be mock or nebius. No automatic fallback is permitted.')
    model = provider or (MockProvider() if settings.mode == 'mock' else NebiusProvider(settings))
    files = file_store or SampleFiles(ROOT)
    session = secrets.token_urlsafe(32)
    lock = asyncio.Lock()
    app = FastAPI(title="Veto local API", docs_url=None, redoc_url=None, openapi_url=None)
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=["127.0.0.1", "localhost"])

    @app.exception_handler(FilePolicyError)
    async def file_error(request, exc):
        return JSONResponse({'detail': exc.message}, status_code=exc.status)

    @app.middleware("http")
    async def local_guard(request: Request, call_next):
        if request.url.path.startswith("/api/"):
            origin = request.headers.get("origin")
            if origin is not None and origin not in ORIGINS:
                return JSONResponse({"detail": "Only the local Veto page can use this API."}, status_code=403)
            if request.method not in ("GET", "HEAD"):
                if origin not in ORIGINS or not secrets.compare_digest(request.headers.get("x-veto-session", ""), session):
                    return JSONResponse({"detail": "Refresh the local Veto page before submitting."}, status_code=403)
            if request.headers.get("sec-fetch-site") == "cross-site":
                return JSONResponse({"detail": "Cross-site access denied."}, status_code=403)
            try:
                length = int(request.headers.get("content-length", "0") or "0")
            except ValueError:
                return JSONResponse({"detail": "Invalid request length."}, status_code=400)
            if length > 16384:
                return JSONResponse({"detail": "Request too large."}, status_code=413)
        response = await call_next(request)
        response.headers["Cache-Control"] = "no-store"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Content-Security-Policy"] = "default-src 'self'; connect-src 'self'; style-src 'self'; img-src 'self' data:; frame-ancestors 'none'; base-uri 'self'; form-action 'self'"
        return response

    @app.get("/api/status")
    async def status():
        return {"ready": settings.mode == 'mock' or bool(settings.key.strip()),
                "provider": "Local mock (no API)" if settings.mode == 'mock' else "Nebius Token Factory",
                "model": "sample-replies-v1" if settings.mode == 'mock' else settings.model, "mode": settings.mode,
                "live_testing": "pending", "milestone": "Sample-only M2 development; live M1 pending",
                "voice_enabled": False, "tools": [], "session": session}

    @app.post("/api/chat")
    async def chat(body: ChatInput):
        if lock.locked():
            return JSONResponse({"detail": "One request is already running. Please wait."}, status_code=429)
        async with lock:
            try:
                result = await model.answer(body.prompt)
                logger.info("Answer mode=%s model=%s latency_ms=%s", settings.mode, result['model'], result["latency_ms"])
                return result
            except ProviderError as exc:
                return JSONResponse({"detail": exc.message}, status_code=exc.status)

    @app.get('/api/workspace')
    def workspace():
        return files.workspace()

    @app.post('/api/permission')
    def permission(body: PermissionInput):
        return files.set_permission(body.root_id, body.granted)

    @app.get('/api/preferences')
    def preferences():
        return files.preferences()

    @app.put('/api/preferences')
    def set_preferences(body: PreferenceInput):
        return files.set_preference(body.sort_by)

    @app.delete('/api/preferences')
    def reset_preferences():
        return files.set_preference(None)

    @app.get('/api/preferences/export')
    def export_preferences():
        return {'schema_version': 1, 'preferences': files.preferences()}

    @app.post('/api/plans/preview')
    def preview(body: RootInput):
        return files.preview(body.root_id)

    @app.get('/api/plans')
    def history():
        return files.history()

    @app.get('/api/plans/{plan_id}')
    def plan(plan_id: str):
        return files.get_plan(plan_id)

    @app.post('/api/plans/{plan_id}/approve')
    def approve(plan_id: str, body: ApprovalInput):
        return files.approve(plan_id, body.plan_hash)

    @app.post('/api/plans/{plan_id}/execute')
    def execute(plan_id: str, body: ExecuteInput):
        return files.execute(plan_id, body.approval_token)

    @app.post('/api/plans/{plan_id}/cancel')
    def cancel(plan_id: str):
        return files.cancel(plan_id)

    @app.post('/api/plans/{plan_id}/stop')
    def stop(plan_id: str):
        return files.stop(plan_id)

    @app.post('/api/plans/{plan_id}/undo-preview')
    def undo_preview(plan_id: str):
        return files.preview_undo(plan_id)

    # Same origin for UI/API: no CORS, no browser key, no separate exposed dev server.
    @app.api_route("/api/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
    async def unknown_api(path: str):
        return JSONResponse({"detail": "This capability is not available in this milestone."}, status_code=404)

    dist = ROOT / "frontend" / "dist"
    if dist.is_dir():
        app.mount("/", StaticFiles(directory=dist, html=True), name="ui")
    return app
