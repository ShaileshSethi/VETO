"""Text-only Nebius adapter. No tools, shell, file access or automatic retries."""
from dataclasses import dataclass
from time import perf_counter
from typing import Protocol
from urllib.parse import urlsplit

import httpx


class ProviderError(Exception):
    def __init__(self, status: int, message: str):
        self.status = status
        self.message = message


@dataclass(frozen=True)
class Settings:
    key: str = ""
    model: str = "nvidia/Nemotron-3_5-Lightning"
    base_url: str = "https://api.tokenfactory.nebius.com/v1/"
    mode: str = "mock"


class ModelProvider(Protocol):
    async def answer(self, prompt: str) -> dict: ...


class MockProvider:
    """Explicit development fixture; never constructs an HTTP client."""
    async def answer(self, prompt: str) -> dict:
        text = prompt.casefold()
        if any(word in text for word in ("sort", "organize", "folder", "file")):
            reply = "Open Sample files, select Veto Demo Inbox, and allow that folder. Preview the fixed sorting rules, review each destination, then approve the exact moves. You can preview and approve undo afterward. This reply itself changes nothing."
        elif "python" in text:
            reply = "A Python function is a named block of code you can reuse. It can take inputs and return a result, like a small recipe."
        elif "study" in text:
            reply = "Try a short study session, one clear goal, and a break afterward. This is sample advice; I have not changed your laptop."
        else:
            reply = "I’m ready for a sample question. Try asking about Python, study tips, or sorting the demo folder. My replies are fixed examples while your Nebius credits are pending."
        return {"answer": "[MOCK — sample reply, no API call]\n" + reply,
                "provider": "Local mock (no API)", "model": "sample-replies-v1",
                "mode": "mock", "request_id": None, "latency_ms": 0, "usage": {}}


class NebiusProvider:
    def __init__(self, settings: Settings, transport=None):
        self.settings = settings
        self.transport = transport

    async def answer(self, prompt: str) -> dict:
        s = self.settings
        if not s.key.strip():
            raise ProviderError(503, "Add your Nebius API key to the local .env file, then restart Veto.")
        url = urlsplit(s.base_url)
        if (url.scheme != "https" or url.hostname not in {
            "api.tokenfactory.nebius.com", "api.tokenfactory.us-central1.nebius.com"
        } or url.username or url.password or url.port not in (None, 443)
            or url.query or url.fragment or url.path.rstrip("/") != "/v1"):
            raise ProviderError(503, "NEBIUS_BASE_URL must be a supported official Nebius HTTPS /v1/ endpoint.")
        if not s.model.startswith("nvidia/"):
            raise ProviderError(503, "Choose an NVIDIA model ID from the Nebius catalog in .env.")
        started = perf_counter()
        try:
            async with httpx.AsyncClient(
                base_url=s.base_url.rstrip("/") + "/", timeout=45,
                headers={"Authorization": f"Bearer {s.key}"},
                follow_redirects=False, transport=self.transport, trust_env=False,
            ) as client:
                # Verify availability for this key; never silently substitute a model.
                catalog = await client.get("models")
                self.check_status(catalog)
                if s.model not in {m["id"] for m in catalog.json()["data"]}:
                    raise ProviderError(503, "Configured NVIDIA model is unavailable to this account. Check Nebius's catalog and update NEBIUS_MODEL locally.")
                response = await client.post("chat/completions", json={
                    "model": s.model,
                    "messages": [
                        {"role": "system", "content": "You are Veto, a calm, concise Windows assistant. This early version answers text questions only. You have no tools, file access, memory, microphone or Windows controls. Never claim to have performed an action. Use simple language."},
                        {"role": "user", "content": prompt},
                    ],
                    "max_tokens": 1024,
                    "stream": False,
                })
                self.check_status(response)
                payload = response.json()
                answer = payload["choices"][0]["message"].get("content")
                if not isinstance(answer, str) or not answer.strip():
                    raise ProviderError(502, "Nebius returned no answer text. Try a shorter question; no action was performed.")
                # Do not persist prompts, answers, credentials or raw provider errors.
                return {"answer": answer, "provider": "Nebius Token Factory", "model": s.model,
                        "mode": "nebius",
                        "request_id": payload.get("id"), "latency_ms": round((perf_counter() - started) * 1000),
                        "usage": payload.get("usage", {})}
        except httpx.TimeoutException:
            raise ProviderError(504, "Nebius timed out. Nothing was changed; you can try again.") from None
        except httpx.RequestError:
            raise ProviderError(502, "Cannot reach Nebius. Check your internet connection and try again.") from None
        except (ValueError, KeyError, TypeError, IndexError):
            raise ProviderError(502, "Nebius returned an unexpected response. Nothing was changed.") from None

    @staticmethod
    def check_status(response):
        if response.status_code in (401, 403):
            raise ProviderError(502, "Nebius rejected the key or account access. Check your key locally and account permissions.")
        if response.status_code == 429:
            raise ProviderError(429, "Nebius rate or credit limit reached. Check account credits; no automatic retry was made.")
        if not response.is_success:
            raise ProviderError(502, "Nebius request failed. Check model access and account status; no action was performed.")
