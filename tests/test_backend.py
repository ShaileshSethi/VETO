import asyncio
import json

import httpx
import pytest
from fastapi.testclient import TestClient

from backend.main import create_app
from backend.provider import NebiusProvider, ProviderError, Settings
from scripts.generate_samples import SAMPLES, generate


def client():
    return TestClient(create_app(Settings(mode='nebius')), base_url="http://127.0.0.1:8765")


def headers(c):
    return {"Origin": "http://127.0.0.1:8765", "X-Veto-Session": c.get('/api/status').json()['session']}


def test_missing_key_and_no_runtime_tools():
    c = client()
    status = c.get('/api/status').json()
    assert not status['ready'] and not status['voice_enabled'] and status['tools'] == []
    r = c.post('/api/chat', headers=headers(c), json={"prompt": "hello"})
    assert r.status_code == 503 and '.env' in r.json()['detail']
    assert c.post('/api/move', headers=headers(c), json={}).status_code == 404


def test_reject_foreign_site_wrong_host_and_missing_session():
    c = client()
    assert c.get('/api/status', headers={"Origin": "https://evil.example"}).status_code == 403
    assert c.get('/api/status', headers={"Host": "evil.example"}).status_code == 400
    assert c.post('/api/chat', headers={"Origin": "http://127.0.0.1:8765"}, json={"prompt": "hi"}).status_code == 403
    h = headers(c); h['Origin'] = 'https://evil.example'
    assert c.post('/api/chat', headers=h, json={"prompt": "hi"}).status_code == 403
    assert c.post('/api/chat', headers={"X-Veto-Session": headers(c)['X-Veto-Session']}, json={"prompt": "hi"}).status_code == 403


@pytest.mark.parametrize('body', [{"prompt": " "}, {"prompt": "x" * 2001}, {"prompt": "hi", "tool": "shell"}])
def test_input_bounds(body):
    c = client()
    assert c.post('/api/chat', headers=headers(c), json=body).status_code == 422


def test_provider_contract_with_test_only_transport():
    calls = []
    def transport(request):
        calls.append(request)
        if request.url.path.endswith('/models'):
            return httpx.Response(200, json={"data": [{"id": Settings.model}]})
        return httpx.Response(200, json={"id": "test-request", "choices": [{"message": {"content": "Test answer"}}], "usage": {"prompt_tokens": 10}})
    provider = NebiusProvider(Settings(key="test-secret"), httpx.MockTransport(transport))
    answer = asyncio.run(provider.answer('Explain functions'))
    assert answer['model'] == Settings.model and answer['request_id'] == 'test-request'
    assert len(calls) == 2 and calls[1].url.path == '/v1/chat/completions'
    assert 'tools' not in json.loads(calls[1].content) and 'test-secret' not in str(answer)


@pytest.mark.parametrize('status,expected', [(401,502),(403,502),(429,429),(500,502)])
def test_provider_errors_are_sanitized(status, expected):
    provider = NebiusProvider(Settings(key="test-secret"), httpx.MockTransport(lambda r: httpx.Response(status, text='test-secret private upstream body')))
    with pytest.raises(ProviderError) as error:
        asyncio.run(provider.answer('hi'))
    assert error.value.status == expected and 'test-secret' not in error.value.message


def test_unavailable_model_prevents_inference():
    calls = []
    def transport(request):
        calls.append(request)
        return httpx.Response(200, json={"data": []})
    with pytest.raises(ProviderError):
        asyncio.run(NebiusProvider(Settings(key='test-key'), httpx.MockTransport(transport)).answer('hi'))
    assert len(calls) == 1


def test_timeout_no_retry():
    calls = []
    def transport(request):
        calls.append(request)
        raise httpx.ReadTimeout('secret', request=request)
    with pytest.raises(ProviderError) as error:
        asyncio.run(NebiusProvider(Settings(key='test-key'), httpx.MockTransport(transport)).answer('hi'))
    assert error.value.status == 504 and len(calls) == 1


def test_endpoint_cannot_exfiltrate_key():
    with pytest.raises(ProviderError) as error:
        asyncio.run(NebiusProvider(Settings(key='test-key', base_url='https://evil.example/v1/')).answer('hi'))
    assert error.value.status == 503


def test_sample_generator_preserves_existing_bytes(tmp_path):
    assert generate(tmp_path) == len(SAMPLES)
    file = tmp_path / 'data/demo/Veto Demo Inbox/lecture-notes.txt'
    file.write_bytes(b'keep me')
    assert generate(tmp_path) == 0 and file.read_bytes() == b'keep me'


def test_sample_generator_denies_junction(tmp_path):
    # Windows junction creation needs no administrator privileges.
    import subprocess
    if __import__('os').name != 'nt':
        pytest.skip('Windows junction test')
    outside = tmp_path / 'outside'; outside.mkdir()
    linked = tmp_path / 'data'
    result = subprocess.run(['cmd', '/c', 'mklink', '/J', str(linked), str(outside)], capture_output=True)
    assert result.returncode == 0
    with pytest.raises(RuntimeError):
        generate(tmp_path)
    assert list(outside.iterdir()) == []
