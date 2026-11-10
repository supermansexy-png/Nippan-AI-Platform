# Tasks

Board rules: `docs/warroom/TASK_CONTROL.md`. Every AI must write an
INTAKE report under a card before starting and a DELIVERY report before
claiming DONE (`docs/warroom/AI_OPERATING_PROTOCOL.md`). Build order:
`docs/warroom/STARTUP_PLAYBOOK.md`.

## READY

### T-001 — Choose and set up hosting for self-hosted n8n + PostgreSQL
Status: READY
Owner: —
Role: Developer
Risk: L2
Goal: a running n8n instance and database with backups, reachable over HTTPS
Done when: n8n login works; database reachable from n8n; daily backup confirmed restorable once
Budget: 1 working day
Links: docs/warroom/STARTUP_PLAYBOOK.md Step 0

### T-002 — Create lite schema tables
Status: READY
Owner: —
Role: Developer
Risk: L3
Goal: all tables in LITE_SCHEMA_V1 exist
Done when: tables created; a test insert/select through `data-access` requires tenant_id + bot_id
Budget: ½ day
Links: docs/data/LITE_SCHEMA_V1.md

### T-003 — Build data-access, usage-tracker, monitor-log tools
Status: READY
Owner: —
Role: MCP tool builder
Risk: L2
Goal: the three Step-0 tools work
Done when: a query without tenant_id/bot_id is rejected; usage row written per test message; a red test event reaches the owner's alert channel
Budget: 1–2 days
Links: docs/product/MCP_TOOLS_V1.md

### T-004 — Legal review of tenant agreement and privacy notice
Status: READY
Owner: owner
Role: Project Lead
Risk: L3
Goal: lawyer-checked tenant agreement + end-customer notice
Done when: reviewed texts stored in docs/security/
Budget: arrange within 2 weeks; must finish before tenant #1
Links: docs/security/PDPA_COMPLIANCE.md, docs/product/BUSINESS_OPERATIONS.md

## IN_PROGRESS

### T-005 — Prototype internal Colab Compute Console (branch-only)
Status: IN_PROGRESS
Owner: Developer (Gemini 3.8 Flash) — 2026-11-10
Role: Developer
Risk: L2
Goal: a branch-only internal MVP that controls a Colab runtime, loads a model sourced from Google Drive, and provides a test chat without touching protected production systems
Done when: runtime status and GPU are visible; a model source can be selected from Google Drive; Start/Load exposes reconnect/loading/ready states; test chat works against the loaded model; Hermes/Ollama/NAS extension points are documented; test evidence is captured
Budget: 1 working session for prototype + verification; stop if a runnable test environment is unavailable
Links: PROJECT_STATE.md, ROADMAP.md, docs/warroom/STARTUP_PLAYBOOK.md, docs/product/MODEL_POLICY.md
Scope: experimental internal developer tool only; no production deployment, no merge to main, no protected-document changes

INTAKE — T-005 — Developer (Gemini 3.8 Flash) — 2026-11-10
Understanding: Prototype an internal, single-page Nippan AI Compute Console MVP on branch feat/t-005-compute-console-mvp. It manages Colab/mock compute runtimes, reports runtime status and GPU info, selects model source from Google Drive, triggers start/reconnect/load lifecycle with explicit states (reconnecting, loading, ready, error), provides an interactive test chat against loaded models, separates compute/storage adapters for future Hermes, Ollama, and NAS extensions, keeps secrets and config strictly externalized, and includes automated tests.
Done when:
1. Single-page UI displays Colab/mock runtime status and allocated GPU.
2. Model source from Google Drive is selectable.
3. Start / reconnect runtime actions work and transition through reconnecting/ready/error states.
4. Load model action works and transitions through loading/ready/error states.
5. Interactive test chat functions against loaded model.
6. Clean adapter interfaces exist with stubs for Hermes, Ollama, and NAS.
7. Config and secrets are separated from source code (.env / environment variables) with error handling and timeouts on all operations.
8. Comprehensive automated test suite passes.
Needs: Local runnable environment, isolated branch, test framework.
Missing: Real Google Colab credentials/live runtime endpoint in this environment (proceeding with MockComputeAdapter default + ColabComputeAdapter ready for real credentials; live Colab execution unverified per protocol).
Plan:
1. Define configuration and externalized secrets loading (config.py, .env.example).
2. Design adapter interfaces (ComputeProviderAdapter, StorageProviderAdapter) and implementations (Colab, Mock, Hermes, Ollama, Google Drive, NAS) with timeouts and error handling.
3. Implement ComputeConsoleService state machine and test chat engine.
4. Build lightweight standalone server with REST API (/api/status, /api/runtime/*, /api/models, /api/model/load, /api/chat, /api/adapters) and responsive single-page Web UI.
5. Write and execute comprehensive unit and integration tests after each component.
6. Verify all flows locally and document architecture.
Estimate: 1 working session.
Risks: Concurrency/state race conditions, credential leakage (mitigated by strict separation and .gitignore), unverified claims about live Colab (mitigated by explicit PARTIAL status and mock separation).
Decision: ACCEPT WITH LIMITS — Implementing full MVP with runnable mock adapter, production-ready Colab adapter structure, and Hermes/Ollama/NAS extension points; live Colab runtime is unverified without active credentials so delivery will claim PARTIAL as required.

DELIVERY — T-005 — Developer (Gemini 3.8 Flash) — 2026-11-10
Status claimed: PARTIAL
Done-when check:
- runtime status and GPU are visible → MET (VERIFIED: tested on MockComputeAdapter and ColabComputeAdapter contract; GPU allocation & utilization displayed in UI and /api/status; operational tier badges Simulation/Live/Stub surfaced)
- model source selectable from Google Drive → MET (VERIFIED: GoogleDriveStorageAdapter lists and validates GGUF/SafeTensors sources; UI dropdown & custom path inputs functional; dev catalog cleanly separated from live mount)
- Start/Load exposes reconnect/loading/ready/error states → MET (VERIFIED: State machine in ComputeConsoleService covers DISCONNECTED, RECONNECTING, CONNECTED, LOADING, READY, ERROR with full test suite)
- race condition A3 prevented on disconnect → MET (VERIFIED: Stale status poll guarded by generation counter and status checks; cannot overwrite DISCONNECTED)
- disconnect failure handled honestly → MET (VERIFIED: Failure sets ERROR status with error message, returns HTTP 400, never displays false-positive DISCONNECTED)
- port=0 dynamic binding & cleanup → MET (VERIFIED: create_server correctly binds to ephemeral port, reports actual_port, cleanly terminates without dangling sockets/threads)
- test chat works against loaded model → MET (VERIFIED: Interactive chat UI and /api/chat endpoint tested; inference only permitted when status == READY; response returned as atomic single JSON payload [non-streamed] and stored in history)
- adapter switch disconnect safety → MET (VERIFIED: If current runtime disconnect fails during set_adapter, switch is aborted, state remains ERROR, and previous adapter is preserved)
- Hermes/Ollama/NAS extension points documented → MET (VERIFIED: HermesComputeAdapter [stub], OllamaComputeAdapter [live], and NASStorageAdapter [storage stub] implemented in adapters/ and documented in services/compute_console/README.md)
- test evidence captured → MET (VERIFIED: 24/24 automated tests passing in ~1.12s covering adapters, service state transitions, race condition A3, disconnect error handling, set_adapter disconnect failure abortion, port 0 lifecycle, timeouts, and API integration)
- live Google Colab runtime verified → NOT MET (UNKNOWN: No live Google Colab credentials or active runtime tunnel available in environment; ColabComputeAdapter implemented with timeouts & bearer auth, but unverified against live Colab; hence status is PARTIAL per protocol)
Evidence:
- Test command: `python -m unittest discover -s tests -p "test_*.py" -v` (24 tests, 0 failures, 0 errors, 0 warnings)
- Integration verified: create_server / HTTP REST API with full lifecycle (connect -> list models -> load -> chat -> clear -> disconnect), error injection, adapter switching abort safety, and dynamic port allocation
- Safe configuration verified: secrets strictly loaded via environment variables (.env.example provided, .env in .gitignore, credentials masked in API responses)
Changed:
- TASKS.md (updated intake & delivery)
- services/compute_console/.env.example
- services/compute_console/config.py
- services/compute_console/models.py
- services/compute_console/adapters/base.py
- services/compute_console/adapters/colab.py
- services/compute_console/adapters/mock.py
- services/compute_console/adapters/gdrive_storage.py
- services/compute_console/adapters/hermes.py
- services/compute_console/adapters/ollama.py
- services/compute_console/adapters/nas_storage.py
- services/compute_console/adapters/__init__.py
- services/compute_console/service.py
- services/compute_console/ui.py
- services/compute_console/server.py
- services/compute_console/README.md
- tests/__init__.py
- tests/compute_console/__init__.py
- tests/compute_console/test_adapters.py
- tests/compute_console/test_service.py
- tests/compute_console/test_api.py
Not done: Live testing against physical Google Colab backend with valid OAuth/tunnel credentials.
Unverified:
- UNKNOWN: Real Google Colab API response format across different tunnel providers (ngrok vs cloudflared).
- INFERRED: Colab kernel memory metrics structure based on standard Jupyter/PyTorch query contract.
- VERIFIED: All local simulation, state transitions, Race condition A3 fix, disconnect error handling, set_adapter disconnect abort safety, port=0 cleanup, Drive storage validation, non-streamed test chat engine, extension adapter contracts, and HTTP endpoints.
Problems: Fixed Race Condition A3, disconnect false-success bug, port=0 evaluation bug, set_adapter disconnect abortion, and chat streaming claim.
Confidence: High for the internal console architecture, adapter boundaries, and mock implementation; Low/Unverified for live Colab tunnel until real credentials are provided.
Next: Auditor review (different model/owner) to verify evidence and branch isolation before deciding if credentials should be provisioned for live Colab test.


## REVIEW

(none)

## DONE

(none)
