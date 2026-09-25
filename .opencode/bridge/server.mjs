import express from "express";
import path from "node:path";
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
  const server = new McpServer({
    name: "nippan-opencode-bridge",
    version: "1.0.0",
  });

  server.registerTool(
    "opencode_status",
    {
      description:
        "ตรวจสถานะ OpenCode และ Nippan project โดยไม่แก้ไขอะไร",
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
        "ดูรายชื่อ AI agents ที่หัวหน้าโปรเจกต์สามารถใช้งานได้",
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

  server.registerTool(
    "opencode_start_task",
    {
      description:
        "สร้างงานใหม่และส่งให้ Project Lead ของ Nippan AI Platform",
      inputSchema: z.object({
        task: z.string().min(1),
        title: z.string().optional(),
      }),
    },
    async ({ task, title }) => {
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

  server.registerTool(
    "opencode_send_message",
    {
      description:
        "ส่งคำสั่งเพิ่มเติมให้ Project Lead ใน session ที่มีอยู่",
      inputSchema: z.object({
        sessionId: z.string().min(1),
        message: z.string().min(1),
      }),
    },
    async ({ sessionId, message }) => {
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
        "อ่านสถานะและคำตอบล่าสุดจาก Project Lead",
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
        "ดู diff ที่เกิดจาก session โดยไม่แก้ไขไฟล์",
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

  server.registerTool(
    "opencode_abort_task",
    {
      description:
        "หยุดงานที่กำลังทำอยู่ใน OpenCode session",
      inputSchema: z.object({
        sessionId: z.string().min(1),
      }),
    },
    async ({ sessionId }) => {
      await getSession(sessionId);

      const aborted = await oc(
        `/session/${encodeURIComponent(
          sessionId
        )}/abort`,
        {
          method: "POST",
        }
      );

      return result({
        sessionId,
        aborted,
      });
    }
  );

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