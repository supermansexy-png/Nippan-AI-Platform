import { type Plugin, tool } from "@opencode-ai/plugin"

// Warn when the accumulated chat context grows large, because every turn
// re-sends the whole history — opening a new chat saves tokens/cost.
const TOKEN_THRESHOLD = 120_000 // current-context tokens (input + cache read + output of the latest turn)
const MESSAGE_THRESHOLD = 60 // fallback if token info is unavailable
const WARN_COOLDOWN_MS = 5 * 60 * 1000 // re-warn at most every 5 minutes per session

function asList(res: unknown): unknown[] {
  if (Array.isArray(res)) return res
  const r = res as { data?: unknown[] } | undefined
  if (r && Array.isArray(r.data)) return r.data
  return []
}

type Msg = {
  info?: {
    role?: string
    tokens?: {
      input?: number
      output?: number
      cache?: { read?: number; write?: number }
    }
  }
}

export const SessionHandoff: Plugin = async ({ client }) => {
  const lastWarn = new Map<string, number>()

  const toast = async (
    message: string,
    variant: "info" | "success" | "warning" | "error" = "info",
  ) => {
    try {
      await client.tui.showToast({ body: { message, variant } })
    } catch {
      // toast is best-effort; never break the session
    }
  }

  return {
    // Warn when the accumulated context is large — the lever is "open a new chat".
    event: async ({ event }) => {
      if (event.type !== "session.idle") return
      const props = (event as { properties?: Record<string, unknown> }).properties ?? {}
      const id =
        (props.sessionID as string | undefined) ??
        (props.sessionId as string | undefined) ??
        ((props.info as { id?: string } | undefined)?.id) ??
        ((props.session as { id?: string } | undefined)?.id)
      if (!id) return

      const now = Date.now()
      if (now - (lastWarn.get(id) ?? 0) < WARN_COOLDOWN_MS) return

      try {
        const res = await client.session.messages({ path: { id } })
        const list = asList(res) as Msg[]
        const msgCount = list.length

        // Context size ≈ the latest assistant turn's input + cache read + output,
        // which is roughly what gets re-sent on the next turn.
        let ctxTokens = 0
        for (let i = list.length - 1; i >= 0; i--) {
          const info = list[i]?.info
          if (info?.role === "assistant" && info.tokens) {
            const t = info.tokens
            ctxTokens = (t.input ?? 0) + (t.cache?.read ?? 0) + (t.output ?? 0)
            break
          }
        }

        const overTokens = ctxTokens >= TOKEN_THRESHOLD
        const overMsgs = ctxTokens === 0 && msgCount >= MESSAGE_THRESHOLD
        if (!overTokens && !overMsgs) return

        lastWarn.set(id, now)
        const size = ctxTokens > 0 ? `~${ctxTokens.toLocaleString()} tokens` : `${msgCount} ข้อความ`
        await toast(
          `แชทนี้สะสมบริบทเยอะแล้ว (${size}) — ทุก turn จะส่งซ้ำ ทำให้เปลือง token; เปิดแชทใหม่หรือพิมพ์ /handoff เพื่อย้ายงานต่อ`,
          "warning",
        )
      } catch {
        // best-effort; ignore failures
      }
    },

    // Tool the AI calls to open a fresh session seeded with a handoff summary.
    tool: {
      handoff: tool({
        description:
          "Create a NEW opencode session and seed it with a handoff summary so work can continue there. Use when the current chat is getting long. Returns the new session id.",
        args: {
          summary: tool.schema
            .string()
            .describe(
              "Concise handoff summary: what was done, status/decisions, what's still open, recommended next step.",
            ),
          title: tool.schema.string().optional().describe("Short title for the new session."),
        },
        async execute(args) {
          const created = (await client.session.create({
            body: { title: args.title ?? "Handoff" },
          })) as { id?: string; data?: { id?: string } }
          const session = created?.data ?? created
          const id = session?.id
          if (!id) return "ERROR: could not create a new session."

          const seed = [
            "# Handoff — continue from here",
            "",
            args.summary,
            "",
            "Working dir: this repo. Follow AGENTS.md and docs/warroom/AI_OPERATING_PROTOCOL.md.",
          ].join("\n")

          await client.session.prompt({
            path: { id },
            body: { noReply: true, parts: [{ type: "text", text: seed }] },
          })

          await toast("สร้างแชทใหม่แล้ว — เปิด /sessions เพื่อไปทำงานต่อ", "success")

          return [
            `Created new session: ${id}`,
            "It is seeded with the handoff summary (no AI reply triggered).",
            "Tell the user (Thai): สรุปเสร็จแล้ว เปิด /sessions แล้วเลือกแชทใหม่เพื่อทำงานต่อ — opencode ยังไม่มี API สลับหน้าให้อัตโนมัติ จึงต้องเลือกเอง 1 ครั้ง",
          ].join("\n")
        },
      }),
    },
  }
}