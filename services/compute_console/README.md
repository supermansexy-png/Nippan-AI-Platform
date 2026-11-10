# Nippan AI Compute Console MVP (Internal Developer Tool)

Branch: `feat/t-005-compute-console-mvp`  
Task: `T-005` (Risk: L2)

## Overview

The **Nippan AI Compute Console** is an internal prototype enabling developers and operators to monitor compute runtime state, inspect GPU allocation, load models from Google Drive repositories, and run interactive test chats against the loaded model.

This is strictly an internal developer utility. It does not touch protected production systems and is completely decoupled from customer-facing bot pipelines.

## Architecture

```
+-------------------------------------------------------------+
|              Single-Page Web UI (ui.py)                     |
|  - Colab / Runtime Status Badge (reconnecting/ready/error)  |
|  - GPU Allocation Gauge (VRAM Used / Total, Utilization)    |
|  - Model Source Picker (Google Drive / Catalog)             |
|  - Test Chat Interface (Interactive inference sandbox)      |
+-------------------------------------------------------------+
                              | REST API
                              v
+-------------------------------------------------------------+
|               HTTP Server & API (server.py)                 |
|  GET /api/status, POST /api/runtime/*, POST /api/chat...   |
+-------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------+
|            ComputeConsoleService (service.py)               |
|  - State Machine: DISCONNECTED -> RECONNECTING ->           |
|                   CONNECTED -> LOADING -> READY / ERROR     |
|  - Timeout & Error Handling Safeguards                      |
|  - Chat Guard (Permitted ONLY when status == READY)         |
+-------------------------------------------------------------+
               /                              \
              v                                v
+-----------------------------+   +---------------------------+
|   ComputeProviderAdapter    |   |   StorageProviderAdapter  |
|  - MockComputeAdapter       |   |  - GoogleDriveStorage     |
|  - ColabComputeAdapter      |   |  - NASStorageAdapter      |
|  - HermesComputeAdapter     |   +---------------------------+
|  - OllamaComputeAdapter     |
+-----------------------------+
```

## Supported & Extension Adapters

1. **Compute Adapters (`services/compute_console/adapters/`)**:
   - `MockComputeAdapter`: Local zero-dependency simulation with simulated GPU (NVIDIA Tesla T4), latency, and fault injection hooks. Used when live credentials are absent.
   - `ColabComputeAdapter`: Remote integration with Google Colab kernel gateway / HTTP tunnel. Requires `COLAB_ENDPOINT_URL` and optional `COLAB_AUTH_TOKEN`.
   - `HermesComputeAdapter`: Extension adapter for Hermes agent orchestrator and worker clusters.
   - `OllamaComputeAdapter`: Extension adapter for local/remote Ollama REST API daemon.

2. **Storage Adapters**:
   - `GoogleDriveStorageAdapter`: Discovers and validates GGUF / SafeTensors model sources from Google Drive mounted directories or Drive catalog URIs.
   - `NASStorageAdapter`: Extension adapter for internal SMB/NFS storage mounts.

## Configuration & Secrets Management

All secrets and configuration are strictly externalized from source code:
- Template: `.env.example`
- Environment variables:
  - `COMPUTE_ENV`: `development` | `test` | `production`
  - `COMPUTE_PROVIDER`: `mock` | `colab` | `hermes` | `ollama`
  - `STORAGE_PROVIDER`: `gdrive` | `nas`
  - `COLAB_ENDPOINT_URL`: Remote URL for Colab runtime (do not hardcode)
  - `COLAB_AUTH_TOKEN`: Auth token (masked in all logs and status APIs)
  - `GDRIVE_MODELS_PATH`: Path or URI to models repository
  - `TIMEOUT_CONNECT_SEC`: Connection timeout (default: 15.0s)
  - `TIMEOUT_LOAD_SEC`: Model load timeout (default: 45.0s)
  - `TIMEOUT_CHAT_SEC`: Inference timeout (default: 20.0s)

## How to Run

### Run Server Locally:
```bash
python -m services.compute_console.server
```
Then open: `http://127.0.0.1:8080`

### Run Automated Tests:
```bash
python -m unittest discover -s tests -p "test_*.py" -v
```
