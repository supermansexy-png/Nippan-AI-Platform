"""
HTML/CSS/JS Single-Page UI for Nippan AI Compute Console MVP.
Zero external CDN dependencies - 100% self-contained for offline internal use.
"""

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Nippan AI - Compute Console MVP</title>
  <style>
    :root {
      --bg: #0b0f19;
      --card-bg: #111827;
      --card-border: #1f2937;
      --text: #f3f4f6;
      --text-muted: #9ca3af;
      --primary: #3b82f6;
      --primary-hover: #2563eb;
      --accent: #8b5cf6;
      --success: #10b981;
      --warning: #f59e0b;
      --danger: #ef4444;
      --disconnected: #6b7280;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, sans-serif; }
    body { background-color: var(--bg); color: var(--text); min-height: 100vh; display: flex; flex-direction: column; }
    
    header { background: #0f172a; border-bottom: 1px solid var(--card-border); padding: 1rem 1.5rem; display: flex; justify-content: space-between; align-items: center; }
    .brand { display: flex; align-items: center; gap: 0.75rem; }
    .brand-logo { width: 32px; height: 32px; background: linear-gradient(135deg, var(--primary), var(--accent)); border-radius: 8px; display: flex; align-items: center; justify-content: center; font-weight: bold; color: white; }
    .brand-title { font-size: 1.15rem; font-weight: 700; letter-spacing: -0.02em; }
    .brand-badge { background: #1e293b; color: #94a3b8; font-size: 0.75rem; padding: 0.2rem 0.5rem; border-radius: 4px; border: 1px solid #334155; }
    
    .status-badge { display: inline-flex; align-items: center; gap: 0.5rem; padding: 0.35rem 0.85rem; border-radius: 9999px; font-size: 0.85rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; }
    .status-dot { width: 8px; height: 8px; border-radius: 50%; }
    
    .status-disconnected { background: rgba(107, 114, 128, 0.15); color: #9ca3af; border: 1px solid #4b5563; }
    .status-disconnected .status-dot { background: #6b7280; }
    
    .status-reconnecting { background: rgba(245, 158, 11, 0.15); color: #fbbf24; border: 1px solid #d97706; }
    .status-reconnecting .status-dot { background: #f59e0b; animation: pulse 1s infinite; }
    
    .status-connected { background: rgba(59, 130, 246, 0.15); color: #60a5fa; border: 1px solid #2563eb; }
    .status-connected .status-dot { background: #3b82f6; }
    
    .status-loading { background: rgba(139, 92, 246, 0.15); color: #c084fc; border: 1px solid #7c3aed; }
    .status-loading .status-dot { background: #8b5cf6; animation: pulse 1s infinite; }
    
    .status-ready { background: rgba(16, 185, 129, 0.15); color: #34d399; border: 1px solid #059669; }
    .status-ready .status-dot { background: #10b981; }
    
    .status-error { background: rgba(239, 68, 68, 0.15); color: #f87171; border: 1px solid #dc2626; }
    .status-error .status-dot { background: #ef4444; }
    
    @keyframes pulse {
      0%, 100% { opacity: 1; transform: scale(1); }
      50% { opacity: 0.4; transform: scale(1.3); }
    }
    
    main { flex: 1; max-width: 1200px; width: 100%; margin: 0 auto; padding: 1.5rem; display: grid; grid-template-columns: 380px 1fr; gap: 1.5rem; }
    
    .card { background: var(--card-bg); border: 1px solid var(--card-border); border-radius: 12px; padding: 1.25rem; display: flex; flex-direction: column; gap: 1rem; }
    .card-title { font-size: 0.95rem; font-weight: 600; color: #e5e7eb; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #1f2937; padding-bottom: 0.5rem; }
    
    .metric-row { display: flex; justify-content: space-between; align-items: center; font-size: 0.875rem; margin-bottom: 0.35rem; }
    .metric-label { color: var(--text-muted); }
    .metric-value { font-weight: 600; color: #f3f4f6; }
    
    .progress-bar-bg { width: 100%; height: 8px; background: #1f2937; border-radius: 9999px; overflow: hidden; margin-top: 0.25rem; }
    .progress-bar-fill { height: 100%; background: linear-gradient(90deg, var(--primary), var(--accent)); width: 0%; transition: width 0.3s; }
    
    .btn { background: var(--primary); color: white; border: none; padding: 0.6rem 1rem; border-radius: 8px; font-weight: 600; font-size: 0.875rem; cursor: pointer; transition: all 0.2s; display: inline-flex; align-items: center; justify-content: center; gap: 0.5rem; }
    .btn:hover:not(:disabled) { background: var(--primary-hover); transform: translateY(-1px); }
    .btn:disabled { opacity: 0.5; cursor: not-allowed; }
    .btn-secondary { background: #374151; color: #f3f4f6; }
    .btn-secondary:hover:not(:disabled) { background: #4b5563; }
    .btn-danger { background: #dc2626; color: white; }
    .btn-danger:hover:not(:disabled) { background: #b91c1c; }
    
    .select, .input { width: 100%; background: #0f172a; border: 1px solid #334155; color: #f1f5f9; padding: 0.6rem 0.75rem; border-radius: 8px; font-size: 0.875rem; outline: none; }
    .select:focus, .input:focus { border-color: var(--primary); }
    
    .error-banner { background: rgba(239, 68, 68, 0.15); border: 1px solid #ef4444; border-radius: 8px; padding: 0.75rem 1rem; font-size: 0.85rem; color: #fca5a5; display: none; align-items: center; justify-content: space-between; }
    
    /* Chat Area */
    .chat-card { height: 640px; display: flex; flex-direction: column; }
    .chat-messages { flex: 1; overflow-y: auto; display: flex; flex-direction: column; gap: 0.75rem; padding: 0.5rem; }
    .message-bubble { max-width: 80%; padding: 0.75rem 1rem; border-radius: 12px; font-size: 0.875rem; line-height: 1.45; white-space: pre-wrap; }
    .message-user { align-self: flex-end; background: #2563eb; color: white; border-bottom-right-radius: 2px; }
    .message-assistant { align-self: flex-start; background: #1e293b; color: #f1f5f9; border: 1px solid #334155; border-bottom-left-radius: 2px; }
    .message-system { align-self: center; background: rgba(107, 114, 128, 0.2); color: #9ca3af; font-size: 0.75rem; border-radius: 6px; padding: 0.25rem 0.75rem; }
    
    .chat-input-bar { display: flex; gap: 0.5rem; padding-top: 0.75rem; border-top: 1px solid #1f2937; }
    .chat-input { flex: 1; }
    
    /* Extension Points Info */
    .adapters-list { display: flex; flex-direction: column; gap: 0.5rem; font-size: 0.8rem; }
    .adapter-item { display: flex; justify-content: space-between; padding: 0.4rem 0.6rem; background: #0f172a; border-radius: 6px; border: 1px solid #1e293b; }
    
    footer { text-align: center; padding: 1rem; font-size: 0.75rem; color: #64748b; border-top: 1px solid #1e293b; }
  </style>
</head>
<body>

  <header>
    <div class="brand">
      <div class="brand-logo">N</div>
      <div class="brand-title">Nippan AI Compute Console</div>
      <span class="brand-badge" id="envBadge">INTERNAL MVP</span>
    </div>
    <div id="statusBadge" class="status-badge status-disconnected">
      <div class="status-dot"></div>
      <span id="statusText">DISCONNECTED</span>
    </div>
  </header>

  <div id="errorBanner" class="error-banner" style="margin: 1rem 1.5rem 0 1.5rem;">
    <span id="errorMessage">Error text</span>
    <button onclick="dismissError()" style="background:none; border:none; color:#fca5a5; cursor:pointer; font-weight:bold;">&times;</button>
  </div>

  <main>
    <!-- Left Column: Runtime Controls, GPU, Storage -->
    <div style="display:flex; flex-direction:column; gap:1.25rem;">
      
      <!-- Runtime Control Card -->
      <div class="card">
        <div class="card-title">
          <span>Compute Runtime</span>
          <select id="providerSelect" class="select" style="width: auto; padding: 0.2rem 0.5rem; font-size: 0.75rem;" onchange="switchProvider()">
            <option value="mock">Mock Colab (Local)</option>
            <option value="colab">Google Colab (Remote)</option>
            <option value="hermes">Hermes Cluster</option>
            <option value="ollama">Ollama Daemon</option>
          </select>
        </div>
        <div class="metric-row">
          <span class="metric-label">Status Info:</span>
          <span class="metric-value" id="statusMessageText" style="font-size:0.8rem; text-align:right;">Disconnected</span>
        </div>
        <div style="display:flex; gap:0.5rem; margin-top:0.5rem;">
          <button id="btnConnect" class="btn" style="flex:1;" onclick="connectRuntime()">Start / Reconnect</button>
          <button id="btnDisconnect" class="btn btn-secondary" onclick="disconnectRuntime()">Disconnect</button>
        </div>
      </div>

      <!-- GPU Card -->
      <div class="card">
        <div class="card-title">
          <span>Hardware Allocation</span>
          <span id="gpuStatusTag" style="font-size:0.75rem; color:#9ca3af;">No GPU</span>
        </div>
        <div class="metric-row">
          <span class="metric-label">Device Name:</span>
          <span class="metric-value" id="gpuName">--</span>
        </div>
        <div class="metric-row">
          <span class="metric-label">VRAM Usage:</span>
          <span class="metric-value" id="vramText">0 MB / 0 MB</span>
        </div>
        <div class="progress-bar-bg">
          <div id="vramBar" class="progress-bar-fill"></div>
        </div>
        <div class="metric-row" style="margin-top:0.25rem;">
          <span class="metric-label">Utilization:</span>
          <span class="metric-value" id="gpuUtil">0.0%</span>
        </div>
      </div>

      <!-- Model Source Card (Google Drive) -->
      <div class="card">
        <div class="card-title">
          <span>Google Drive Model Storage</span>
          <span class="brand-badge">Storage</span>
        </div>
        <div>
          <label style="font-size:0.75rem; color:var(--text-muted); display:block; margin-bottom:0.35rem;">Select Model Checkpoint:</label>
          <select id="modelSelect" class="select">
            <option value="">Loading models...</option>
          </select>
        </div>
        <div style="font-size:0.75rem; color:var(--text-muted);">
          <span>Or enter custom Drive path:</span>
          <input type="text" id="customModelPath" class="input" placeholder="gdrive:/models/custom.gguf" style="margin-top:0.25rem;">
        </div>
        <button id="btnLoadModel" class="btn" onclick="loadSelectedModel()">Load Model into VRAM</button>
        <div class="metric-row" style="font-size:0.8rem;">
          <span class="metric-label">Loaded:</span>
          <span class="metric-value" id="loadedModelName" style="color:#60a5fa;">None</span>
        </div>
      </div>

      <!-- Extension Points & Adapters -->
      <div class="card">
        <div class="card-title">
          <span>Platform Extension Adapters</span>
          <span style="font-size:0.75rem; color:#9ca3af;">Interfaces</span>
        </div>
        <div class="adapters-list">
          <div class="adapter-item"><span>Google Colab</span><span style="color:#60a5fa;">Compute (Remote)</span></div>
          <div class="adapter-item"><span>Hermes Cluster</span><span style="color:#c084fc;">Compute (Agentic)</span></div>
          <div class="adapter-item"><span>Ollama Daemon</span><span style="color:#34d399;">Compute (Local API)</span></div>
          <div class="adapter-item"><span>Google Drive</span><span style="color:#fbbf24;">Storage (Drive API)</span></div>
          <div class="adapter-item"><span>Internal NAS</span><span style="color:#94a3b8;">Storage (NFS/SMB)</span></div>
        </div>
      </div>

    </div>

    <!-- Right Column: Interactive Test Chat -->
    <div class="card chat-card">
      <div class="card-title">
        <span>Model Test Chat</span>
        <div style="display:flex; gap:0.5rem; align-items:center;">
          <span id="chatModelIndicator" style="font-size:0.75rem; color:#9ca3af;">Model not loaded</span>
          <button class="btn btn-secondary" style="padding:0.2rem 0.5rem; font-size:0.75rem;" onclick="clearChat()">Clear</button>
        </div>
      </div>

      <div id="chatMessages" class="chat-messages">
        <div class="message-bubble message-system">
          Welcome to Nippan AI Compute Console. Connect the runtime and load a model to begin test inference.
        </div>
      </div>

      <div class="chat-input-bar">
        <input type="text" id="chatInput" class="input chat-input" placeholder="Enter message to test model inference..." onkeydown="if(event.key==='Enter') sendChatMessage()">
        <button id="btnSend" class="btn" onclick="sendChatMessage()">Send</button>
      </div>
    </div>
  </main>

  <footer>
    Nippan AI Platform &bull; Compute Console Internal Prototype &bull; Branch-only MVP (T-005)
  </footer>

  <script>
    let currentState = {};

    async function fetchStatus() {
      try {
        const res = await fetch('/api/status');
        const data = await res.json();
        if (data.ok) {
          updateUI(data.state, data.config);
        }
      } catch (err) {
        console.error("Error polling status:", err);
      }
    }

    async function fetchModels() {
      try {
        const res = await fetch('/api/models');
        const data = await res.json();
        if (data.ok) {
          const select = document.getElementById('modelSelect');
          select.innerHTML = '';
          data.models.forEach(m => {
            const opt = document.createElement('option');
            opt.value = m.id;
            opt.textContent = `${m.name} (${m.size_mb} MB - ${m.format})`;
            select.appendChild(opt);
          });
        }
      } catch (err) {
        console.error("Error loading models:", err);
      }
    }

    function updateUI(state, config) {
      currentState = state;

      // Status Badge
      const badge = document.getElementById('statusBadge');
      const text = document.getElementById('statusText');
      badge.className = `status-badge status-${state.status}`;
      text.textContent = state.status.toUpperCase();

      document.getElementById('statusMessageText').textContent = state.status_message || '';

      // Error banner
      const errBanner = document.getElementById('errorBanner');
      if (state.active_error) {
        document.getElementById('errorMessage').textContent = state.active_error;
        errBanner.style.display = 'flex';
      } else {
        errBanner.style.display = 'none';
      }

      // GPU Info
      if (state.gpu_info) {
        document.getElementById('gpuName').textContent = state.gpu_info.name;
        document.getElementById('vramText').textContent = `${state.gpu_info.memory_used_mb} MB / ${state.gpu_info.memory_total_mb} MB`;
        document.getElementById('gpuUtil').textContent = `${state.gpu_info.utilization_pct}%`;
        const pct = Math.min(100, Math.round((state.gpu_info.memory_used_mb / state.gpu_info.memory_total_mb) * 100));
        document.getElementById('vramBar').style.width = `${pct}%`;
        document.getElementById('gpuStatusTag').textContent = 'Allocated';
        document.getElementById('gpuStatusTag').style.color = '#34d399';
      } else {
        document.getElementById('gpuName').textContent = '--';
        document.getElementById('vramText').textContent = '0 MB / 0 MB';
        document.getElementById('gpuUtil').textContent = '0.0%';
        document.getElementById('vramBar').style.width = '0%';
        document.getElementById('gpuStatusTag').textContent = 'No GPU';
        document.getElementById('gpuStatusTag').style.color = '#9ca3af';
      }

      // Loaded Model
      if (state.loaded_model) {
        document.getElementById('loadedModelName').textContent = state.loaded_model.name;
        document.getElementById('chatModelIndicator').textContent = `Loaded: ${state.loaded_model.name}`;
        document.getElementById('chatModelIndicator').style.color = '#34d399';
      } else {
        document.getElementById('loadedModelName').textContent = 'None';
        document.getElementById('chatModelIndicator').textContent = 'Model not loaded';
        document.getElementById('chatModelIndicator').style.color = '#9ca3af';
      }

      // Buttons state
      const isReconnecting = state.status === 'reconnecting';
      const isLoading = state.status === 'loading';
      const isReady = state.status === 'ready';
      const isConnected = state.status === 'connected' || isReady;

      document.getElementById('btnConnect').disabled = isReconnecting || isLoading;
      document.getElementById('btnLoadModel').disabled = !isConnected || isLoading;
      document.getElementById('btnSend').disabled = !isReady;
      document.getElementById('chatInput').disabled = !isReady;
      if (!isReady) {
        document.getElementById('chatInput').placeholder = isConnected ? 'Load a model to enable chat...' : 'Connect runtime to begin...';
      } else {
        document.getElementById('chatInput').placeholder = 'Enter message to test model inference...';
      }

      // Active Provider dropdown
      if (state.active_provider) {
        document.getElementById('providerSelect').value = state.active_provider;
      }
    }

    async function connectRuntime() {
      setLoadingMessage("Initiating runtime connection...");
      try {
        const res = await fetch('/api/runtime/connect', { method: 'POST' });
        const data = await res.json();
        await fetchStatus();
      } catch (err) {
        showError("Failed to trigger connect: " + err.message);
      }
    }

    async function disconnectRuntime() {
      try {
        await fetch('/api/runtime/disconnect', { method: 'POST' });
        await fetchStatus();
      } catch (err) {
        showError("Failed to trigger disconnect: " + err.message);
      }
    }

    async function loadSelectedModel() {
      const custom = document.getElementById('customModelPath').value.trim();
      const selected = document.getElementById('modelSelect').value;
      const target = custom || selected;
      if (!target) {
        showError("Please select or enter a model path.");
        return;
      }
      setLoadingMessage("Loading model into runtime VRAM...");
      try {
        const res = await fetch('/api/model/load', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ model_id: target })
        });
        const data = await res.json();
        await fetchStatus();
      } catch (err) {
        showError("Model load failed: " + err.message);
      }
    }

    async function switchProvider() {
      const provider = document.getElementById('providerSelect').value;
      try {
        await fetch('/api/adapter/select', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ provider })
        });
        await fetchStatus();
      } catch (err) {
        showError("Failed to switch provider: " + err.message);
      }
    }

    async function sendChatMessage() {
      const input = document.getElementById('chatInput');
      const text = input.value.trim();
      if (!text) return;

      appendMessage('user', text);
      input.value = '';

      document.getElementById('btnSend').disabled = true;
      try {
        const res = await fetch('/api/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ message: text })
        });
        const data = await res.json();
        if (data.ok) {
          appendMessage('assistant', data.reply);
        } else {
          appendMessage('system', 'Error: ' + data.error);
        }
      } catch (err) {
        appendMessage('system', 'Inference failed: ' + err.message);
      } finally {
        document.getElementById('btnSend').disabled = false;
        input.focus();
      }
    }

    function appendMessage(role, content) {
      const container = document.getElementById('chatMessages');
      const div = document.createElement('div');
      div.className = `message-bubble message-${role}`;
      div.textContent = content;
      container.appendChild(div);
      container.scrollTop = container.scrollHeight;
    }

    async function clearChat() {
      await fetch('/api/chat/clear', { method: 'POST' });
      const container = document.getElementById('chatMessages');
      container.innerHTML = '<div class="message-bubble message-system">Chat history cleared.</div>';
    }

    function showError(msg) {
      document.getElementById('errorMessage').textContent = msg;
      document.getElementById('errorBanner').style.display = 'flex';
    }

    function dismissError() {
      document.getElementById('errorBanner').style.display = 'none';
    }

    function setLoadingMessage(msg) {
      document.getElementById('statusMessageText').textContent = msg;
    }

    // Initial load
    fetchStatus();
    fetchModels();
    setInterval(fetchStatus, 3000);
  </script>
</body>
</html>
"""
