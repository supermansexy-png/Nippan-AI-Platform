import { type Plugin, tool } from "@opencode-ai/plugin"
import { readFile, writeFile } from "node:fs/promises"
import { join } from "node:path"

const HANDOFF_FILE = "docs/project-memory/SESSION_HANDOFF.md"
const AUTO_START = "<!-- AUTO-HANDOFF:START -->"
const AUTO_END = "<!-- AUTO-HANDOFF:END -->"

// Warn when the accumulated chat context grows large, because every turn
// re-sends the whole history — compacting (or opening a new chat) saves tokens/cost.
// Primary lever per Owner decision 2026-09-25: `/compact` in the same chat
// (the desktop app has no easy session switcher).
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

export const SessionHandoff: Plugin = async ({ client, ...rest }) => {
  const root =
    (rest as { directory?: string }).directory ??
    (rest as { worktree?: string }).worktree ??
    process.cwd()
  const lastWarn = new Map<string, number>()

  // Write/refresh the auto-handoff block at the top of the tracked handoff file,
  // so a fresh `/new` chat can continue with "อ่าน SESSION_HANDOFF.md แล้วทำงานต่อ".
  const writeHandoffFile = async (summary: string, title?: string): Promise<string> => {
    const path = join(root, HANDOFF_FILE)
    // Local date (UTC would show the previous day in UTC+7).
    const d = new Date()
    const stamp = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`
    const block = [
      AUTO_START,
      `## Handoff ล่าสุด (auto) — ${stamp}`,
      ...(title ? [`**หัวข้อ:** ${title}`] : []),
      "",
      summary.trim(),
      AUTO_END,
    ].join("\n")

    let existing = ""
    try {
      existing = await readFile(path, "utf8")
    } catch {
      existing = "# Session Handoff\n"
    }

    let next: string
    const s = existing.indexOf(AUTO_START)
    const e = existing.indexOf(AUTO_END)
    if (s >= 0 && e > s) {
      next = existing.slice(0, s) + block + existing.slice(e + AUTO_END.length)
    } else {
      next = block + "\n\n" + existing
    }

    await writeFile(path, next, "utf8")
    return path
  }

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
          `แชทนี้สะสมบริบทเยอะแล้ว (${size}) — ทุก turn ส่งซ้ำ เปลือง token; พิมพ์ /compact เพื่อย่อประวัติแล้วทำงานต่อในแชทเดิม (หรือ /handoff หากต้องการย้ายไปแชทใหม่)`,
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
          "Create a NEW opencode session seeded with a handoff summary, and also write that summary into docs/project-memory/SESSION_HANDOFF.md so a fresh `/new` chat can continue from the file. Use when the current chat is getting long. Returns the new session id.",
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
            "",
            "Instruction: นี่คือ handoff จากแชทก่อนหน้า — สรุปสั้น ๆ 2-4 บรรทัดว่าเรากำลังทำอะไร สถานะล่าสุด และงานถัดไปที่แนะนำ แล้วรอคำสั่งผู้ใช้",
          ].join("\n")

          // Trigger a visible reply so the new chat immediately shows the summary
          // and the assistant has consumed the handoff context.
          await client.session.prompt({
            path: { id },
            body: { parts: [{ type: "text", text: seed }] },
          })

          let fileNote: string
          try {
            await writeHandoffFile(args.summary, args.title)
            fileNote = `Handoff summary also written to ${HANDOFF_FILE}`
          } catch {
            fileNote = `WARN: could not write ${HANDOFF_FILE}`
          }

          await toast(`สร้างแชทใหม่แล้ว + อัปเดต ${HANDOFF_FILE}`, "success")

          return [
            `Created new session: ${id}`,
            "It is seeded with the handoff summary and a visible summary reply was triggered.",
            fileNote,
            "Tell the user (Thai): สรุปเสร็จแล้ว — ถ้าต้องการเริ่มหน้าใหม่เอง ให้กด /new แล้วพิมพ์ว่า 'อ่าน docs/project-memory/SESSION_HANDOFF.md แล้วทำงานต่อ'",
          ].join("\n")
        },
      }),
    },
  }
}