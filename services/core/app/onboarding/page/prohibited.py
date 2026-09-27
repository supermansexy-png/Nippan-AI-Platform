"""Forbidden names for the customer-facing page (honesty rule 2).

Built from the REAL model/vendor names in use in this project —
``docs/product/MODEL_ROSTER.md`` slugs (per-role staffing + review tiers)
plus the literal project tool names. The page and every string it serves
must contain NONE of these tokens, visible or not (title, comment,
data-*, CSS, error message). Checked by a test, not a promise.
"""

from __future__ import annotations

__all__ = ["PROHIBITED_TOKENS"]

# provider/platform names (roster prefixes + tool names)
PROHIBITED_TOKENS: list[str] = [
    "openrouter",
    "opencode-go",
    "opencode",
    "openrouter.ai",
    "anthropic",
    "openai",
    "google",
    "mistralai",
    "nvidia",
    "poolside",
    "nex-agi",
    "thinkingmachines",
    "groq",
    "zapier",
]

# model slugs / model ids actually pinned or tested in the project
PROHIBITED_TOKENS += [
    "glm-5.3-flash",
    "glm",
    "kimi-k3",
    "deepseek-v4.1-flash",
    "deepseek-v4-flash-free",
    "qwen3.8-flash",
    "qwen3.7-flash",
    "nemotron-3.5-lightning",
    "nemotron-3-ultra-free",
    "nemotron-3-ultra-550b-a55b",
    "mimo-v2.6-pro",
    "mimo-v2.6-flash-free",
    "mimo-v2.6-flash",
    "space-bunny-free",
    "muse-spark-1.2-contributor-free",
    "muse-spark-1.3-contributor-free",
    "big-pickle",
    "ling-3.0-flash-fin-free",
    "laguna-s-2.1",
    "longcat-2.5-preview-free",
    "inkling-small",
    "inkling",
    "jev-1.13",
    "nex-n2.5-mini",
    "gpt-6-luna",
    "claude-opus-5.5",
    "opus-5.5",
    "claude",
    "opus",
    "gemini",
    "grok-4.7",
    "gmft",
    "voxtral",
    "whisper",
    "seedream",
    "bedrock",
    "ollama",
]

# tool names that are the project's own automation (not model/product)
PROHIBITED_TOKENS += [
    "warroom",
    "headless-run",
    "headless_status",
]
