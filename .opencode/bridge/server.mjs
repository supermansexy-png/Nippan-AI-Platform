import express from "express";
import path from "node:path";
import { createHash, timingSafeEqual } from "node:crypto";
import { appendFileSync } from "node:fs";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/streamableHttp.js";
import { z } from "zod";

const OPENCODE_URL =
  process.env.OPENCODE_URL || "http://127.0.0.1:4096";

const OPENCODE_USERNAME =
  process.env.OPENCODE_SERVER_USERNAME || "opencode";

const OPENCODE_PASSWORD =
  process.env.OPENCODE_SERVER_PASSWORD;

const PROJECT_ROOT = path.resolve(
  process.env.NIPPAN_PROJECT_ROOT || "C:\\opencode\\nippan"
);

const PORT = Number(process.env.NIPPAN_BRIDGE_PORT || 4100);

// Session-id allowlist for opencode_send_message (fail-closed: empty = reject all).
const ALLOWED_SESSIONS = String(
  process.env.NIPPAN_BRIDGE_ALLOWED_SESSIONS || ""
)
  .split(",")
  .map((entry) => entry.trim())
  .filter(Boolean);

// Privileged tools (start/abort task) are OFF by default.
const ENABLE_PRIVILEGED =
  process.env.NIPPAN_BRIDGE_ENABLE_PRIVILEGED === "true";

const PRIVILEGED_TOKEN =
  process.env.NIPPAN_BRIDGE_PRIVILEGED_TOKEN || "";

function safeTokenEquals(provided, expected) {
  if (!expected) return false;
  const a = createHash("sha256")
    .update(String(provided || ""))
    .digest();
  const b = createHash("sha256")
    .update(expected)
    .digest();
  return timingSafeEqual(a, b);
}

// --- Guardrails for privileged tools (Owner-approved 2026-09-25) ---
// 1) audit: every privileged call is appended as a JSON line
// 2) rate limit: cap how many sessions can be created in a 10-minute window
// 3) abort: only sessions created by THIS bridge instance can be aborted
const AUDIT_LOG =
  process.env.NIPPAN_BRIDGE_AUDIT_LOG ||
  path.join(PROJECT_ROOT, ".opencode", "bridge", "privileged-audit.log");

const MAX_SESSIONS_PER_WINDOW = Number(
  process.env.NIPPAN_BRIDGE_MAX_SESSIONS_PER_10MIN || 3
);
const SESSION_WINDOW_MS = 10 * 60 * 1000;

const createdSessions = new Set();
let sessionTimestamps = [];

function audit(event, detail = {}) {
  try {
    appendFileSync(
      AUDIT_LOG,
      JSON.stringify({ at: new Date().toISOString(), event, ...detail }) +
        "\n"
    );
  } catch (error) {
    console.error("audit write failed:", String(error));
  }
}

function rateLimitOk() {
  const now = Date.now();
  sessionTimestamps = sessionTimestamps.filter(
    (t) => now - t < SESSION_WINDOW_MS
  );
  return sessionTimestamps.length < MAX_SESSIONS_PER_WINDOW;
}

if (!OPENCODE_PASSWORD) {
  console.error("Missing OPENCODE_SERVER_PASSWORD");
  process.exit(1);
}

function basicAuth() {
  return (
    "Basic " +
    Buffer.from(
      `${OPENCODE_USERNAME}:${OPENCODE_PASSWORD}`
    ).toString("base64")
  );
}

async function oc(endpoint, options = {}) {
  const response = await fetch(`${OPENCODE_URL}${endpoint}`, {
    ...options,
    headers: {
      Authorization: basicAuth(),
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
  });

  if (!response.ok) {
    const body = await response.text();
    throw new Error(
      `OpenCode ${response.status}: ${body || response.statusText}`
    );
  }

  if (response.status === 204) {
    return null;
  }

  const text = await response.text();

  if (!text) return null;

  try {
    return JSON.parse(text);
  } catch {
    return text;
  }
}

function normalize(p) {
  return path.resolve(p).toLowerCase();
}

async function getSession(sessionId) {
  const session = await oc(
    `/session/${encodeURIComponent(sessionId)}`
  );

  if (!session?.directory) {
    throw new Error("Session directory cannot be verified");
  }

  if (normalize(session.directory) !== normalize(PROJECT_ROOT)) {
    throw new Error(
      `Session is outside allowed project: ${session.directory}`
    );
  }

  return session;
}

function result(data) {
  return {
    content: [
      {
        type: "text",
        text:
          typeof data === "string"
            ? data
            : JSON.stringify(data, null, 2),
      },
    ],
  };
}

function createServer() {
  const server = new McpServer(
    {
      name: "nippan-opencode-bridge",
      version: "1.0.0",
    },
    {
      instructions:
        "Nippan dev-time bridge. The caller is a dev-time ASSISTANT reporting to the Nippan Project Lead. The caller is NOT the Project Lead and NOT the Owner. Use opencode_send_message to report to / ask the Project Lead and opencode_get_result to read the reply. ONLY session ids in the operator-configured allowlist (NIPPAN_BRIDGE_ALLOWED_SESSIONS) can be messaged; messages are capped at 8000 characters. opencode_start_task and opencode_abort_task are DISABLED BY DEFAULT; they only exist when the operator enables NIPPAN_BRIDGE_ENABLE_PRIVILEGED=true, and then they require the shared privileged token (NIPPAN_BRIDGE_PRIVILEGED_TOKEN) as authToken. Do NOT create tasks, do NOT command other agents, do NOT approve or close work, do NOT change architecture.",
    }
  );

  server.registerTool(
    "opencode_status",
    {
      description:
        "ตรวจสถานะ OpenCode และ Nippan project แบบ read-only (สำหรับผู้ช่วย dev-time ดูสถานะ ไม่ใช่สั่งงาน)",
      inputSchema: z.object({}),
    },
    async () => {
      const [health, project, vcs, sessions] =
        await Promise.all([
          oc("/global/health"),
          oc("/project/current"),
          oc("/vcs"),
          oc("/session/status"),
        ]);

      return result({
        health,
        project,
        vcs,
        sessions,
        allowedProject: PROJECT_ROOT,
      });
    }
  );

  server.registerTool(
    "opencode_list_agents",
    {
      description:
        "ดูรายชื่อ AI agents แบบ read-only",
      inputSchema: z.object({}),
    },
    async () => {
      const agents = await oc("/agent");

      const allowedNames = new Set([
        "project-lead",
        "builder",
        "reviewer",
        "security",
        "researcher",
        "ops",
        "build",
        "plan",
        "explore",
        "general",
      ]);

      return result(
        agents
          .filter((a) => allowedNames.has(a.name))
          .map((a) => ({
            name: a.name,
            description: a.description,
            mode: a.mode,
          }))
      );
    }
  );

  if (ENABLE_PRIVILEGED) {
    server.registerTool(
      "opencode_start_task",
      {
        description:
          "สร้างงานใหม่ให้ Project Lead — PRIVILEGED: ต้องเปิด NIPPAN_BRIDGE_ENABLE_PRIVILEGED=true และส่ง authToken ให้ตรงกับ NIPPAN_BRIDGE_PRIVILEGED_TOKEN ผู้ช่วย dev-time ห้ามใช้ (ปิดใช้งานโดย default)",
        inputSchema: z.object({
          authToken: z.string().min(1),
          task: z.string().min(1),
          title: z.string().optional(),
        }),
      },
      async ({ authToken, task, title }) => {
        if (!safeTokenEquals(authToken, PRIVILEGED_TOKEN)) {
          throw new Error(
            "Invalid or missing authToken for privileged tool opencode_start_task"
          );
        }

        if (!rateLimitOk()) {
          audit("start_task.rate_limited");
          throw new Error(
            `Rate limit: at most ${MAX_SESSIONS_PER_WINDOW} sessions per 10 minutes`
          );
        }

        const session = await oc("/session", {
          method: "POST",
          body: JSON.stringify({
            title:
              title ||
              `Nippan task - ${task.slice(0, 60)}`,
          }),
        });

        if (
          !session?.directory ||
          normalize(session.directory) !==
            normalize(PROJECT_ROOT)
        ) {
          throw new Error(
            `Refusing session outside ${PROJECT_ROOT}`
          );
        }

        createdSessions.add(session.id);
        sessionTimestamps.push(Date.now());
        audit("start_task.created", {
          sessionId: session.id,
          title: session.title,
        });

        await oc(
          `/session/${encodeURIComponent(
            session.id
          )}/prompt_async`,
          {
            method: "POST",
            body: JSON.stringify({
              agent: "project-lead",
              parts: [
                {
                  type: "text",
                  text: task,
                },
              ],
            }),
          }
        );

        return result({
          accepted: true,
          sessionId: session.id,
          title: session.title,
          directory: session.directory,
          agent: "project-lead",
        });
      }
    );
  }

  server.registerTool(
    "opencode_send_message",
    {
      description:
        "ผู้ช่วย dev-time ใช้ช่องนี้ส่งข้อความ/รายงานผล/คำถาม ถึง Project Lead ใน session ที่ระบุ แล้วอ่านคำตอบด้วย opencode_get_result — ส่งได้เฉพาะ sessionId ที่อยู่ใน NIPPAN_BRIDGE_ALLOWED_SESSIONS (allowlist) เท่านั้น และข้อความห้ามเกิน 8000 ตัวอักษร",
      inputSchema: z.object({
        sessionId: z.string().min(1),
        message: z.string().min(1),
      }),
    },
    async ({ sessionId, message }) => {
      if (ALLOWED_SESSIONS.length === 0) {
        throw new Error(
          "opencode_send_message is disabled: NIPPAN_BRIDGE_ALLOWED_SESSIONS is not set. The operator must set it to a comma-separated allowlist of session ids, e.g. NIPPAN_BRIDGE_ALLOWED_SESSIONS=ses_xxx."
        );
      }

      if (!ALLOWED_SESSIONS.includes(sessionId)) {
        throw new Error(
          `Session ${sessionId} is not in the NIPPAN_BRIDGE_ALLOWED_SESSIONS allowlist. Ask the operator to allowlist it.`
        );
      }

      if (message.length > 8000) {
        throw new Error(
          `message is ${message.length} characters; the limit is 8000. Split or shorten the message.`
        );
      }

      await getSession(sessionId);

      await oc(
        `/session/${encodeURIComponent(
          sessionId
        )}/prompt_async`,
        {
          method: "POST",
          body: JSON.stringify({
            agent: "project-lead",
            parts: [
              {
                type: "text",
                text: message,
              },
            ],
          }),
        }
      );

      return result({
        accepted: true,
        sessionId,
      });
    }
  );

  server.registerTool(
    "opencode_get_result",
    {
      description:
        "อ่านสถานะและคำตอบล่าสุดจาก Project Lead แบบ read-only",
      inputSchema: z.object({
        sessionId: z.string().min(1),
      }),
    },
    async ({ sessionId }) => {
      await getSession(sessionId);

      const [statuses, messages] =
        await Promise.all([
          oc("/session/status"),
          oc(
            `/session/${encodeURIComponent(
              sessionId
            )}/message?limit=30`
          ),
        ]);

      const latestAssistant = [...messages]
        .reverse()
        .find(
          (m) =>
            m?.info?.role === "assistant"
        );

      const text = latestAssistant?.parts
        ?.filter((p) => p.type === "text")
        ?.map((p) => p.text)
        ?.join("\n");

      return result({
        sessionId,
        status: statuses?.[sessionId] || null,
        latestAssistantText:
          text || null,
      });
    }
  );

  server.registerTool(
    "opencode_get_diff",
    {
      description:
        "ดู diff ที่เกิดจาก session แบบ read-only",
      inputSchema: z.object({
        sessionId: z.string().min(1),
      }),
    },
    async ({ sessionId }) => {
      await getSession(sessionId);

      const diff = await oc(
        `/session/${encodeURIComponent(
          sessionId
        )}/diff`
      );

      return result(diff);
    }
  );

  if (ENABLE_PRIVILEGED) {
    server.registerTool(
      "opencode_abort_task",
      {
        description:
          "หยุดงานใน session — PRIVILEGED: ต้องเปิด NIPPAN_BRIDGE_ENABLE_PRIVILEGED=true และส่ง authToken ให้ตรงกับ NIPPAN_BRIDGE_PRIVILEGED_TOKEN ผู้ช่วย dev-time ห้ามใช้ (ปิดใช้งานโดย default)",
        inputSchema: z.object({
          authToken: z.string().min(1),
          sessionId: z.string().min(1),
        }),
      },
      async ({ authToken, sessionId }) => {
        if (!safeTokenEquals(authToken, PRIVILEGED_TOKEN)) {
          throw new Error(
            "Invalid or missing authToken for privileged tool opencode_abort_task"
          );
        }

        if (!createdSessions.has(sessionId)) {
          audit("abort_task.denied", { sessionId });
          throw new Error(
            "opencode_abort_task is restricted to sessions created by this bridge instance"
          );
        }

        await getSession(sessionId);

        const aborted = await oc(
          `/session/${encodeURIComponent(
            sessionId
          )}/abort`,
          {
            method: "POST",
          }
        );

        audit("abort_task.aborted", { sessionId });

        return result({
          sessionId,
          aborted,
        });
      }
    );
  }

  return server;
}

const app = express();

app.use(express.json({ limit: "1mb" }));

app.get("/health", async (_req, res) => {
  try {
    const health = await oc("/global/health");

    res.json({
      bridge: true,
      opencode: health,
      project: PROJECT_ROOT,
    });
  } catch (error) {
    res.status(503).json({
      bridge: false,
      error: String(error),
    });
  }
});

// OAuth discovery probes (RFC 9728 / OAuth metadata). This bridge is
// loopback-only and deliberately has NO OAuth, so answer every /.well-known/*
// path with a clean JSON 404. Without this, Express returns its default HTML
// 404 page and strict MCP clients fail with: "decode protected resource
// metadata: invalid character '<' looking for beginning of value".
app.use("/.well-known", (_req, res) => {
  res.status(404).json({ error: "not_found" });
});

app.post("/mcp", async (req, res) => {
  const server = createServer();

  const transport =
    new StreamableHTTPServerTransport({
      sessionIdGenerator: undefined,
      enableJsonResponse: true,
    });

  res.on("close", () => {
    transport.close();
  });

  await server.connect(transport);
  await transport.handleRequest(
    req,
    res,
    req.body
  );
});

app.listen(PORT, "127.0.0.1", () => {
  console.log("");
  console.log("Nippan OpenCode MCP Bridge");
  console.log(
    `Health: http://127.0.0.1:${PORT}/health`
  );
  console.log(
    `MCP:    http://127.0.0.1:${PORT}/mcp`
  );
  console.log(
    `Project: ${PROJECT_ROOT}`
  );
  console.log("");
});