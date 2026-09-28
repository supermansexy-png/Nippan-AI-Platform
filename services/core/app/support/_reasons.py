"""Fixed-phrase reasons for the Support change path (T-079e).

Nothing here is ever built from customer text — the phrases are code
constants. They explain WHY a change was refused/held, in the run log.
"""

__all__ = ["REFUSAL_MESSAGE", "cost_why"]


def cost_why(field: str) -> str:
    if field == "monthly_message_quota":
        return (
            "held: a higher chat-reply quota means more replies served per "
            "month, which changes per-bot cost; needs Cost Guard approval"
        )
    if field == "monthly_push_quota":
        return (
            "held: a higher push cap means more paid push messages; "
            "needs Cost Guard approval"
        )
    if field == "enabled_tools":
        return "held: enabling a tool adds per-call cost; needs Cost Guard approval"
    return "held: this change can raise cost; needs Cost Guard approval"


REFUSAL_FREE_TEXT_REASON = (
    "refused: only fixed-menu fields may change — free-form instructions, "
    "custom prompts, or free text cannot be stored or applied "
    "(CUSTOMER_FACING_RULES.md §3)"
)
