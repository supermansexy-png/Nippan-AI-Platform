const EVENT_TYPES = [
  "ROOM_STATE_CHANGED",
  "TURN_SCHEDULED",
  "SCHEDULER_HALTED",
  "MESSAGE_APPENDED",
  "OWNER_DECISION_REQUIRED",
  "BUDGET_HARD_STOP",
  "TURN_FAILED",
];

const app = {
  roomId: null,
  snapshot: null,
  events: [],
  source: null,
};

const $ = (selector) => document.querySelector(selector);
const el = (tag, className, text) => {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
};

function setNotice(message = "") {
  $("#notice").textContent = message;
}

function setConnection(label, state) {
  const node = $("#connection-status");
  node.textContent = label;
  node.dataset.state = state;
}

function queryRoomId() {
  return new URL(window.location.href).searchParams.get("room_id");
}

function formatCost(usage) {
  if (usage?.normalized_cost === null || usage?.normalized_cost === undefined) return "—";
  const currency = usage.currency || "";
  return `${usage.normalized_cost} ${currency}`.trim();
}

function activeAgenda() {
  if (!app.snapshot?.agenda?.length) return null;
  return (
    app.snapshot.agenda.find((item) =>
      ["OPEN", "RUNNING", "NEEDS_OWNER_DECISION"].includes(item.status)
    ) || app.snapshot.agenda[0]
  );
}

function randomTraceId() {
  const bytes = crypto.getRandomValues(new Uint8Array(16));
  return [...bytes].map((value) => value.toString(16).padStart(2, "0")).join("");
}

function resolveSpeaker(event) {
  if (event.event_type === 'ROOM_STATE_CHANGED' && event.message_type === 'OWNER_DECISION') {
    return app.snapshot?.participants?.find(p => p.role === 'OWNER') || null;
  }
  const pid = event.participant_id || event.payload?.participant_id || event.payload?.actor_id;
  if (!pid || !app.snapshot?.participants) return null;
  return app.snapshot.participants.find(p => p.participant_id === pid || p.id === pid);
}

function speakerLabel(event, speaker) {
  if (event.event_type === 'ROOM_STATE_CHANGED' && event.message_type === 'OWNER_DECISION') {
    return { name: speaker?.display_name || speaker?.name || "เจ้าของห้อง", role: speaker?.role || "เจ้าของ", isOwner: true };
  }
  if (event.message_type === "OWNER_MESSAGE") {
    return { name: "เจ้าของห้อง", role: "เจ้าของ", isOwner: true };
  }
  if (speaker) {
    return { name: speaker.display_name || speaker.name, role: speaker.role || "—", isOwner: false };
  }
  return { name: "ระบบ", role: "ไม่ระบุ", isOwner: false };
}

function formatTimestamp(ts) {
  if (!ts) return "";
  const d = new Date(ts);
  if (isNaN(d.getTime())) return String(ts).slice(0, 19);
  return d.toLocaleString("th-TH", { hour: "2-digit", minute: "2-digit", second: "2-digit", hour12: false });
}

function buildCorrelation() {
  const agenda = activeAgenda();
  if (!agenda) throw new Error("This room has no agenda item for command correlation.");
  return {
    tenant_id: app.snapshot.tenant_id,
    application_id: app.snapshot.application_id,
    room_id: app.snapshot.room_id,
    agenda_item_id: agenda.agenda_item_id,
    request_id: crypto.randomUUID(),
    trace_id: randomTraceId(),
  };
}

function renderRoster() {
  const root = $("#participant-roster");
  const items = app.snapshot?.participants || [];
  root.replaceChildren();
  $("#participant-count").textContent = String(items.length);
  if (!items.length) {
    root.className = "roster empty";
    root.textContent = "ยังไม่มีผู้เข้าร่วม";
    return;
  }
  root.className = "roster";
  for (const participant of items) {
    const card = el("div", `roster-item${participant.active ? "" : " inactive"}`);
    card.append(el("strong", "", participant.display_name));
    card.append(el("div", "role", participant.role));
    root.append(card);
  }
}

function renderSystemLog(events) {
  const log = $("#system-log");
  const btn = $("#system-log-toggle");
  const wasOpen = log.classList.contains("open");
  log.replaceChildren();
  if (!events.length) {
    log.className = "system-log" + (wasOpen ? " open" : "");
    if (btn) btn.textContent = wasOpen ? "ซ่อนบันทึกระบบ" : "แสดงบันทึกระบบ";
    return;
  }
  log.className = "system-log" + (wasOpen ? " open" : "");
  for (const event of events) {
    const item = el("div", "message system-log-item");
    const ts = formatTimestamp(event.occurred_at);
    const line = `[${event.event_type}] #${event.sequence}${ts ? " · " + ts : ""} · ${String(eventContent(event)).slice(0, 120)}`;
    item.textContent = line;
    log.append(item);
  }
  if (btn) btn.textContent = wasOpen ? "ซ่อนบันทึกระบบ" : "แสดงบันทึกระบบ";
}

function renderUsage() {
  const usage = app.snapshot?.usage || {};
  const input = Number(usage.input_tokens || 0);
  const output = Number(usage.output_tokens || 0);
  $("#usage-input").textContent = input.toLocaleString();
  $("#usage-output").textContent = output.toLocaleString();
  $("#usage-total").textContent = (input + output).toLocaleString();
  $("#usage-cost").textContent = formatCost(usage);
}

function cardList(selector, items, renderer, emptyText) {
  const root = $(selector);
  root.replaceChildren();
  if (!items?.length) {
    root.className = "stack empty";
    root.textContent = emptyText;
    return;
  }
  root.className = "stack";
  for (const item of items) root.append(renderer(item));
}

function renderContext() {
  cardList("#agenda-list", app.snapshot?.agenda, (item) => {
    const card = el("article", "card");
    card.append(el("strong", "", `${item.sequence}. ${item.title}`));
    card.append(el("div", "meta", `${item.status} · สูงสุด ${item.round_limit} รอบ`));
    card.append(el("div", "meta", item.objective));
    return card;
  }, "ยังไม่มีวาระ");

  cardList("#finding-list", app.snapshot?.findings, (item) => {
    const card = el("article", "card");
    card.append(el("strong", "", item.summary));
    card.append(el("div", "meta", `${item.severity} · ${item.status}`));
    return card;
  }, "ยังไม่มีข้อค้นพบ");

  cardList("#decision-list", app.snapshot?.decisions, (item) => {
    const card = el("article", "card");
    card.append(el("strong", "", item.decision));
    card.append(el("div", "meta", `${item.decision_type} · ${item.status}`));
    return card;
  }, "ยังไม่มีคำตัดสิน");
}

function eventContent(event) {
  const payload = event.payload || {};
  return payload.content_text || payload.content_reference || payload.failure_kind ||
    event.halt_reason || event.event_type;
}

function renderMessages() {
  const root = $("#message-list");
  const wasNearBottom = root.scrollHeight - root.scrollTop - root.clientHeight < 50;
  const isConversationEvent = (e) => e.event_type === 'MESSAGE_APPENDED' || (e.event_type === 'ROOM_STATE_CHANGED' && e.message_type === 'OWNER_DECISION');
  const conversationEvents = [...app.events].filter(isConversationEvent).sort((a, b) => a.sequence - b.sequence);
  const systemLog = [...app.events].filter(e => !isConversationEvent(e)).sort((a, b) => a.sequence - b.sequence);
  root.replaceChildren();

  if (!conversationEvents.length && !systemLog.length) {
    root.className = "messages empty";
    root.textContent = "ยังไม่มีเหตุการณ์ในห้อง";
    renderSystemLog(systemLog);
    return;
  }
  if (!conversationEvents.length) {
    root.className = "messages empty";
    root.textContent = "ยังไม่มีข้อความในห้อง";
  } else {
    root.className = "messages";
    let prevSpeakerKey = null;
    for (let i = 0; i < conversationEvents.length; i++) {
      const event = conversationEvents[i];
      const speaker = resolveSpeaker(event);
      const label = speakerLabel(event, speaker);
      const speakerKey = label.name + "|" + label.role;
      const isGrouped = speakerKey === prevSpeakerKey && i > 0;
      const messageType = event.message_type || (!isConversationEvent(event) ? "SYSTEM_EVENT" : "MESSAGE_APPENDED");
      const isSystem = !isConversationEvent(event);
      const classes = ["message"];
      if (messageType === "OWNER_MESSAGE") classes.push("owner");
      else if (label.isOwner) classes.push("owner");
      else { classes.push("ai"); }
      if (event.event_type === "TURN_FAILED") classes.push("error");
      if (isGrouped && i < conversationEvents.length - 1) classes.push("grouped");
      else if (isGrouped) classes.push("grouped-last");
      const article = el("article", classes.join(" "));

      const head = el("div", "message-head");
      const speakerSpan = el("span", `speaker ${label.isOwner ? "owner" : ""}`, label.name);
      const roleSpan = el("span", "role-label", label.role);
      head.append(speakerSpan, roleSpan);
      const meta = el("span", "", `#${event.sequence}`);
      if (event.occurred_at) meta.textContent = `#${event.sequence} · ${formatTimestamp(event.occurred_at)}`;
      else meta.textContent = `#${event.sequence}`;
      if (messageType === "OWNER_MESSAGE") meta.textContent += " · ข้อความจากเจ้าของ";
      head.append(meta);
      article.append(head);
      article.append(el("div", "content", String(eventContent(event))));
      const model = event.payload?.model;
      const tokens = event.payload?.usage_tokens ? `(${event.payload.usage_tokens} tokens)` : "";
      const modelLine = model ? `${model} ${tokens}` : tokens;
      if (modelLine.trim()) {
        article.append(el("div", "evidence", modelLine.trim()));
      }
      const providerRequestId = event.payload?.provider_request_id;
      const correlation = event.correlation || event.payload?.correlation;
      if (providerRequestId) {
        article.append(el("div", "evidence", `request_id: ${providerRequestId}`));
      }
      if (correlation && correlation.agenda_item_id) {
        const agendaItem = app.snapshot?.agenda?.find(a => a.agenda_item_id === correlation.agenda_item_id);
        if (agendaItem) {
          article.append(el("div", "evidence", `วาระ: ${agendaItem.title || agendaItem.sequence}`));
        }
      }
      root.append(article);
      prevSpeakerKey = speakerKey;
    }
  }
  renderSystemLog(systemLog);
  if (wasNearBottom) {
    root.scrollTop = root.scrollHeight;
  }
}

function renderSnapshot() {
  $("#room-state").textContent = app.snapshot?.state || "—";
  $("#sequence-label").textContent = `ลำดับ ${app.snapshot?.last_sequence || 0}`;
  $("#reconnect").disabled = !app.snapshot;
  renderRoster();
  renderUsage();
  renderContext();
  renderMessages();
}

function mergeEvent(event) {
  const existing = app.events.findIndex((item) => item.sequence === event.sequence);
  if (existing >= 0) app.events[existing] = event;
  else app.events.push(event);

  if (app.snapshot) {
    app.snapshot.last_sequence = Math.max(app.snapshot.last_sequence || 0, event.sequence);
    if (event.room_state) app.snapshot.state = event.room_state;
  }
  renderSnapshot();
}

function disconnect() {
  if (app.source) app.source.close();
  app.source = null;
  setConnection("ยังไม่เชื่อมต่อ", "idle");
}

function connectEvents() {
  disconnect();
  if (!app.snapshot) return;

  const cursor = app.snapshot.last_sequence || 0;
  const url = new URL(
    `/war-room/rooms/${encodeURIComponent(app.snapshot.room_id)}/events`,
    window.location.origin,
  );
  url.searchParams.set("after_sequence", String(cursor));

  const source = new EventSource(url, { withCredentials: true });
  app.source = source;

  source.onopen = () => setConnection("เชื่อมต่อสด", "live");
  source.onerror = () => setConnection("กำลังเชื่อมต่อใหม่", "error");

  for (const type of EVENT_TYPES) {
    source.addEventListener(type, (message) => {
      try {
        mergeEvent(JSON.parse(message.data));
      } catch {
        setNotice(`ข้าม event ${type} เพราะข้อมูลไม่ถูกต้อง`);
      }
    });
  }
}

async function loadRoom(roomId) {
  disconnect();
  setNotice("");
  setConnection("กำลังโหลด", "idle");

  const response = await fetch(
    `/war-room/rooms/${encodeURIComponent(roomId)}/snapshot`,
    { credentials: "same-origin", headers: { Accept: "application/json" } },
  );
  if (!response.ok) throw new Error(`โหลด snapshot ไม่สำเร็จ (${response.status})`);

  const snapshot = await response.json();
  app.roomId = snapshot.room_id;
  app.snapshot = snapshot;
  app.events = Array.isArray(snapshot.recent_events) ? [...snapshot.recent_events] : [];

  $("#room-id").value = snapshot.room_id;
  const url = new URL(window.location.href);
  url.searchParams.set("room_id", snapshot.room_id);
  history.replaceState(null, "", url);

  renderSnapshot();
  connectEvents();
}

async function sendCommand(command, extra = {}) {
  if (!app.snapshot) throw new Error("กรุณาโหลดห้องก่อน");

  const body = {
    command,
    correlation: buildCorrelation(),
    expected_state: app.snapshot.state,
    ...extra,
  };

  const response = await fetch(
    `/war-room/rooms/${encodeURIComponent(app.snapshot.room_id)}/commands`,
    {
      method: "POST",
      credentials: "same-origin",
      headers: { "Content-Type": "application/json", Accept: "application/json" },
      body: JSON.stringify(body),
    },
  );
  if (!response.ok) {
    const detail = await response.text();
    throw new Error(`คำสั่ง ${command} ไม่สำเร็จ (${response.status}): ${detail}`);
  }

  const event = await response.json();
  if (event?.sequence) mergeEvent(event);
}

async function handleCommand(button) {
  const command = button.dataset.command;
  const text = $("#owner-message").value.trim();
  const extra = {};

  if (command === "ASK_ROLE") {
    if (!text) throw new Error("กรุณาใส่ข้อความก่อนถาม role");
    extra.target_role = $("#target-role").value;
    extra.content_text = text;
  } else if (command === "ASK_ALL" || command === "SUBMIT_OWNER_DECISION") {
    if (!text) throw new Error(`กรุณาใส่ข้อความก่อนส่งคำสั่ง ${command}`);
    extra.content_text = text;
  }

  button.disabled = true;
  try {
    setNotice("");
    await sendCommand(command, extra);
    if (["ASK_ROLE", "ASK_ALL", "SUBMIT_OWNER_DECISION"].includes(command)) {
      $("#owner-message").value = "";
    }
  } finally {
    button.disabled = false;
  }
}

$("#load-room").addEventListener("click", async () => {
  try {
    const roomId = $("#room-id").value.trim();
    if (!roomId) throw new Error("กรุณาใส่ Room ID");
    await loadRoom(roomId);
  } catch (error) {
    setConnection("ผิดพลาด", "error");
    setNotice(error.message);
  }
});

$("#jump-latest").addEventListener("click", () => {
  const root = $("#message-list");
  root.scrollTop = root.scrollHeight;
});

$("#reconnect").addEventListener("click", () => connectEvents());

document.querySelectorAll("[data-command]").forEach((button) => {
  button.addEventListener("click", async () => {
    try {
      await handleCommand(button);
    } catch (error) {
      setNotice(error.message);
    }
  });
});

$("#owner-message-form").addEventListener("submit", (event) => event.preventDefault());

window.addEventListener("beforeunload", disconnect);

const initialRoom = queryRoomId();
if (initialRoom) {
  $("#room-id").value = initialRoom;
  loadRoom(initialRoom).catch((error) => {
    setConnection("ผิดพลาด", "error");
    setNotice(error.message);
  });
}
