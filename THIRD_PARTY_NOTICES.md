# Third-party dependencies

Checked 5 October 2026 against the installed package LICENSE files, not README badges. Original Veto source uses MIT; dependencies retain their own terms. No Blinky code, external assets, fonts, or voice assets were copied.

| Dependency | License | Upstream |
| --- | --- | --- |
| FastAPI | MIT | https://github.com/fastapi/fastapi |
| Uvicorn | BSD-3-Clause | https://github.com/encode/uvicorn |
| HTTPX | BSD-3-Clause | https://github.com/encode/httpx |
| python-dotenv | BSD-3-Clause | https://github.com/theskumar/python-dotenv |
| pytest | MIT | https://github.com/pytest-dev/pytest |
| React / React DOM | MIT | https://github.com/facebook/react |
| TypeScript | Apache-2.0 | https://github.com/microsoft/TypeScript |
| Vite | MIT plus bundled dependency notices | https://github.com/vitejs/vite |
| Ruff (development only, 0.16.10) | MIT | https://github.com/astral-sh/ruff |
| Biome (development only, 2.5.15) | MIT OR Apache-2.0 | https://github.com/biomejs/biome |

Exact Python versions are pinned in `backend/requirements-lock.txt`; npm versions, transitive packages, and license metadata are in `frontend/package-lock.json`. Full Python notices remain in installed `.dist-info/licenses` directories. JavaScript notices remain in each installed package's LICENSE file; Vite's `LICENSE.md` includes its bundled dependency notices, and its build preserves React license comments. Keep these notices when distributing a later packaged build and review transitive distribution obligations at M5; this slice does not produce a distributable installer.
