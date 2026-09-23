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
    root.textContent = "No participants.";
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
    card.append(el("div", "meta", `${item.status} · max ${item.round_limit} rounds`));
    card.append(el("div", "meta", item.objective));
    return card;
  }, "No agenda.");

  cardList("#finding-list", app.snapshot?.findings, (item) => {
    const card = el("article", "card");
    card.append(el("strong", "", item.summary));
    card.append(el("div", "meta", `${item.severity} · ${item.status}`));
    return card;
  }, "No findings.");

  cardList("#decision-list", app.snapshot?.decisions, (item) => {
    const card = el("article", "card");
    card.append(el("strong", "", item.decision));
    card.append(el("div", "meta", `${item.decision_type} · ${item.status}`));
    return card;
  }, "No decisions.");
}

function eventContent(event) {
  const payload = event.payload || {};
  return payload.content_text || payload.content_reference || payload.failure_kind ||
    event.halt_reason || event.event_type;
}

function renderMessages() {
  const root = $("#message-list");
  root.replaceChildren();
  const events = [...app.events].sort((a, b) => a.sequence - b.sequence);
  if (!events.length) {
    root.className = "messages empty";
    root.textContent = "No durable room events yet.";
    return;
  }
  root.className = "messages";
  for (const event of events) {
    const messageType = event.message_type || "SYSTEM_EVENT";
    const classes = [
      "message",
      messageType === "OWNER_MESSAGE" ? "owner" : "",
      event.event_type === "TURN_FAILED" ? "error" : "",
    ].filter(Boolean).join(" ");
    const article = el("article", classes);
    const head = el("div", "message-head");
    head.append(el("span", "", `#${event.sequence} · ${messageType}`));
    head.append(el("span", "", event.event_type));
    article.append(head);
    article.append(el("div", "content", String(eventContent(event))));
    const model = event.payload?.model;
    const providerRequest = event.payload?.provider_request_id;
    if (model || providerRequest) {
      article.append(el("div", "evidence", [model, providerRequest].filter(Boolean).join(" · ")));
    }
    root.append(article);
  }
  root.scrollTop = root.scrollHeight;
}

function renderSnapshot() {
  $("#room-state").textContent = app.snapshot?.state || "—";
  $("#sequence-label").textContent = `Sequence ${app.snapshot?.last_sequence || 0}`;
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
  setConnection("Disconnected", "idle");
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

  source.onopen = () => setConnection("Live", "live");
  source.onerror = () => setConnection("Reconnecting", "error");

  for (const type of EVENT_TYPES) {
    source.addEventListener(type, (message) => {
      try {
        mergeEvent(JSON.parse(message.data));
      } catch {
        setNotice(`Ignored invalid ${type} event payload.`);
      }
    });
  }
}

async function loadRoom(roomId) {
  disconnect();
  setNotice("");
  setConnection("Loading", "idle");

  const response = await fetch(
    `/war-room/rooms/${encodeURIComponent(roomId)}/snapshot`,
    { credentials: "same-origin", headers: { Accept: "application/json" } },
  );
  if (!response.ok) throw new Error(`Snapshot request failed (${response.status}).`);

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
  if (!app.snapshot) throw new Error("Load a room first.");

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
    throw new Error(`Command ${command} failed (${response.status}): ${detail}`);
  }

  const event = await response.json();
  if (event?.sequence) mergeEvent(event);
}

async function handleCommand(button) {
  const command = button.dataset.command;
  const text = $("#owner-message").value.trim();
  const extra = {};

  if (command === "ASK_ROLE") {
    if (!text) throw new Error("Enter a message before Ask role.");
    extra.target_role = $("#target-role").value;
    extra.content_text = text;
  } else if (command === "ASK_ALL" || command === "SUBMIT_OWNER_DECISION") {
    if (!text) throw new Error(`Enter content before ${command}.`);
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
    if (!roomId) throw new Error("Enter a room ID.");
    await loadRoom(roomId);
  } catch (error) {
    setConnection("Error", "error");
    setNotice(error.message);
  }
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
    setConnection("Error", "error");
    setNotice(error.message);
  });
}
