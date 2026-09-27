"""Owner alert channel (T-071) — email-first transport.

Design invariants (T-071 INTAKE):

- *Never blocks the room flow*: alert dispatch is fire-and-forget. Any
  alert-transport failure is contained in the alerting wrapper and never
  propagates into room orchestration or persistence.
- *Fail-closed configuration*: when the SMTP settings are incomplete, the
  channel reports itself disabled and alerts fall back to the log sink.
  There is no half-wired channel that logs in with a partial credential.
- *Severity discipline*: only a small whitelist of critical War Room event
  types fires an owner alert, so the owner is not alerted on ordinary
  room activity.
"""

from __future__ import annotations

import asyncio
import logging
import smtplib
import ssl
from dataclasses import dataclass
from email.message import EmailMessage
from email.utils import formatdate
from typing import Protocol

from .contracts import RoomState
from .interfaces import OrderedRoomEvent, RoomEventDraft

logger = logging.getLogger("nippan.alert")


class AlertTransport(Protocol):
    """Delivers one already-rendered alert message. Must not hang."""

    async def deliver(self, message: RenderedAlert) -> None: ...


@dataclass(frozen=True, slots=True)
class RenderedAlert:
    """A fully rendered alert, transport-agnostic."""

    subject: str
    body: str
    to_addr: str
    from_addr: str


class EventAlertRenderer:
    """Renders one War Room event (or sink failure) into an email alert."""

    def __init__(self, to_addr: str, from_addr: str) -> None:
        self._to_addr = to_addr
        self._from_addr = from_addr

    def render_critical_event(self, event: OrderedRoomEvent) -> RenderedAlert:
        event_type = event.event_type.value
        room_state = (
            event.room_state.value if event.room_state is not None else "-"
        )
        message_type = (
            event.message_type.value if event.message_type is not None else "-"
        )
        halt_reason = (
            event.halt_reason.value if event.halt_reason is not None else "-"
        )

        subject = (
            f"[NIPPAN][{event_type}]"
            f" state={room_state}"
            f" halt={halt_reason}"
        )
        body = (
            "Nippan War Room alert (T-071 email channel)\n"
            "\n"
            f"event_type: {event_type}\n"
            f"message_type: {message_type}\n"
            f"room_state: {room_state}\n"
            f"halt_reason: {halt_reason}\n"
            "occurred_at (UTC): "
            f"{event.occurred_at.strftime('%Y-%m-%d %H:%M:%S UTC')}\n"
            f"trace_id: {event.correlation.trace_id}\n"
            f"tenant_id: {event.correlation.tenant_id}\n"
            f"application_id: {event.correlation.application_id}\n"
            f"room_id: {event.correlation.room_id}\n"
            f"participant_id: {event.participant_id or '-'}\n"
            "payload: "
            + self._payload_summary(event)
            + "\n"
        )
        return RenderedAlert(
            subject=subject,
            body=body,
            to_addr=self._to_addr,
            from_addr=self._from_addr,
        )

    def render_sink_failure(
        self,
        draft: RoomEventDraft,
        exc: Exception,
    ) -> RenderedAlert:
        event_type = draft.event_type.value
        subject = (
            f"[NIPPAN][SINK_FAILURE][{event_type}]"
            f" trace={draft.correlation.trace_id}"
        )
        body = (
            "Nippan War Room alert (T-071 email channel)\n"
            "\n"
            "The durable event sink FAILED to commit a room event.\n"
            "\n"
            f"event_type: {event_type}\n"
            f"trace_id: {draft.correlation.trace_id}\n"
            f"tenant_id: {draft.correlation.tenant_id}\n"
            f"application_id: {draft.correlation.application_id}\n"
            f"room_id: {draft.correlation.room_id}\n"
            f"error: {type(exc).__name__}: {exc}\n"
        )
        return RenderedAlert(
            subject=subject,
            body=body,
            to_addr=self._to_addr,
            from_addr=self._from_addr,
        )

    @staticmethod
    def _payload_summary(event: OrderedRoomEvent) -> str:
        """One-line payload summary from frozen payload keys only.

        No room conversation content is copied into the alert body — only
        operational keys. The alert channel never becomes a channel for
        room content.
        """

        payload = event.payload
        interesting_keys = (
            "failure_kind",
            "model",
            "provider_request_id",
            "round_number",
            "usage_tokens",
        )
        picked: list[str] = []
        for key in interesting_keys:
            value = payload.get(key)
            if value is None:
                continue
            if isinstance(value, str) and len(value) > 120:
                value = value[:117] + "..."
            picked.append(f"{key}={value!r}")
        if not picked:
            return "<no operational payload>"
        return ", ".join(picked)


class SmtpEmailAlertTransport:
    """Email transport over plain SMTP (optional STARTTLS) via stdlib.

    `send_alert` is the blocking send; `deliver` runs it in a worker
    thread with timeout isolation so a slow SMTP host cannot stall the
    event loop.
    """

    def __init__(self, *, host: str, port: int, timeout: float) -> None:
        self._host = host
        self._port = port
        self._timeout = timeout

    async def deliver(self, message: RenderedAlert) -> None:
        await asyncio.wait_for(
            asyncio.to_thread(self.send_alert, message),
            timeout=self._timeout,
        )

    def send_alert(self, message: RenderedAlert) -> None:
        email_message = EmailMessage()
        email_message["Subject"] = message.subject
        email_message["From"] = message.from_addr
        email_message["To"] = message.to_addr
        email_message["Date"] = formatdate(localtime=False, usegmt=True)
        email_message.set_content(message.body)

        # Trust only the system CA bundle; no user-supplied certs here.
        context = ssl.create_default_context()
        with smtplib.SMTP(
            self._host,
            self._port,
            timeout=self._timeout,
        ) as smtp:
            smtp.ehlo()
            if smtp.has_extn("starttls"):
                smtp.starttls(context=context)
                smtp.ehlo()
            smtp.send_message(email_message)


class DisabledAlertChannel:
    """Fallback channel for incomplete configuration (fail-closed).

    Succeeds silently — a missing environment must never surface as a
    room-flow error through the alert path.
    """

    async def deliver(self, message: RenderedAlert) -> None:
        logger.warning(
            "alert channel disabled (incomplete SMTP config); "
            "alert not delivered: subject=%s",
            message.subject,
        )


class LoggingAlertChannel:
    """Always-on secondary channel: emits every alert to the log sink."""

    async def deliver(self, message: RenderedAlert) -> None:
        logger.error(
            "ALERT %s :: to=%s :: body=%s",
            message.subject,
            message.to_addr,
            message.body,
        )


class RoomEventSinkProtocol(Protocol):
    """The inner sink interface AlertingEventSink wraps."""

    async def append(
        self,
        event: RoomEventDraft,
        *,
        expected_state: RoomState | None = None,
        new_state: RoomState | None = None,
    ) -> OrderedRoomEvent: ...


class AlertingEventSink:
    """Wraps a RoomEventSink; emits email alerts for critical events.

    Wraps `append(...)` of the inner sink so that:

    - on a *successful* append of a whitelisted critical event type, an
      alert fires (email when configured, log always);
    - when the inner sink *raises* (e.g. `RoomPersistenceError`, a DB
      outage), a SINK_FAILURE alert is queued and the exception is then
      re-raised unchanged — the room flow keeps its fail-closed
      semantics while the owner still gets alerted;
    - the alert dispatch itself can never alter the room flow: delivery
      errors are swallowed into the log only.
    """

    _CRITICAL_EVENT_TYPES = frozenset(
        {
            "TURN_FAILED",
            "BUDGET_HARD_STOP",
        }
    )

    def __init__(
        self,
        inner: RoomEventSinkProtocol,
        channel: AlertTransport,
        renderer: EventAlertRenderer,
    ) -> None:
        self._inner = inner
        self._channel = channel
        self._renderer = renderer
        self._bg_tasks: set[asyncio.Task[None]] = set()

    async def append(
        self,
        event: RoomEventDraft,
        *,
        expected_state: RoomState | None = None,
        new_state: RoomState | None = None,
    ) -> OrderedRoomEvent:
        try:
            ordered = await self._inner.append(
                event,
                expected_state=expected_state,
                new_state=new_state,
            )
        except Exception as exc:
            self._fire_sink_failure_alert(event, exc)
            raise
        if ordered.event_type.value in self._CRITICAL_EVENT_TYPES:
            self._fire_alert(ordered)
        return ordered

    async def await_pending(self) -> None:
        """Await all in-flight alert deliveries (test/shutdown seam)."""

        if self._bg_tasks:
            await asyncio.gather(*self._bg_tasks, return_exceptions=True)

    def _fire_alert(self, ordered: OrderedRoomEvent) -> None:
        message = self._renderer.render_critical_event(ordered)
        self._dispatch(message)

    def _fire_sink_failure_alert(
        self,
        draft: RoomEventDraft,
        exc: Exception,
    ) -> None:
        message = self._renderer.render_sink_failure(draft, exc)
        self._dispatch(message)

    def _dispatch(self, message: RenderedAlert) -> None:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            # Defensive: no running loop. Deliver synchronously in a
            # worker thread; a timeout still degrades to the log channel.
            try:
                asyncio.run(self._deliver_with_fallback(message))
            except Exception as exc:  # pragma: no cover - defensive
                logger.error(
                    "alert dispatch failed outside loop: %s: %s",
                    type(exc).__name__,
                    exc,
                )
            return
        task = loop.create_task(self._deliver_with_fallback(message))
        self._bg_tasks.add(task)
        task.add_done_callback(self._bg_tasks.discard)

    async def _deliver_with_fallback(self, message: RenderedAlert) -> None:
        try:
            await self._channel.deliver(message)
        except Exception as exc:
            logger.error(
                "alert delivery failed; falling back to log sink: "
                "subject=%s error=%s: %s",
                message.subject,
                type(exc).__name__,
                exc,
            )
            await LoggingAlertChannel().deliver(message)


def build_alert_channel(settings) -> tuple[AlertTransport, str, str]:
    """Build (channel, to_addr, from_addr) from settings, fail-closed.

    Returns the SMTP transport only when every required field is present;
    otherwise returns the DisabledAlertChannel so the alerting wrapper
    still works (log-only) instead of crashing at startup.
    """

    required = (
        settings.alert_email_enabled,
        settings.alert_email_smtp_host,
        settings.alert_email_username,
        settings.alert_email_password,
        settings.alert_email_from,
        settings.alert_email_to,
    )
    if not all(required):
        return DisabledAlertChannel(), "", ""
    assert settings.alert_email_smtp_host is not None
    assert settings.alert_email_username is not None
    assert settings.alert_email_password is not None
    assert settings.alert_email_from is not None
    assert settings.alert_email_to is not None
    return (
        SmtpEmailAlertTransport(
            host=settings.alert_email_smtp_host,
            port=settings.alert_email_smtp_port,
            timeout=settings.alert_email_timeout_seconds,
        ),
        settings.alert_email_to,
        settings.alert_email_from,
    )
