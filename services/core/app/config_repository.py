from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from uuid import UUID

from psycopg.rows import dict_row

from .db import Database


@dataclass(frozen=True)
class ActiveAgentConfig:
    config_version_id: UUID
    published_config_hash: str
    policy_merge_version: str
    config_document: dict[str, Any]


class ConfigRepository:
    def __init__(self, database: Database) -> None:
        self._database = database

    async def load_active_agent_config(
        self,
        *,
        tenant_id: UUID,
        application_id: UUID,
        agent_id: UUID,
        environment: str,
        request_id: UUID | None = None,
    ) -> ActiveAgentConfig | None:
        async with self._database.tenant_transaction(
            tenant_id=tenant_id,
            application_id=application_id,
            request_id=request_id,
        ) as conn:
            async with conn.cursor(row_factory=dict_row) as cur:
                await cur.execute(
                    """
                    select
                      c.config_version_id,
                      c.published_config_hash,
                      c.policy_merge_version,
                      c.config_document
                    from public.agent_activations a
                    join public.agent_config_versions c
                      on c.tenant_id = a.tenant_id
                     and c.application_id = a.application_id
                     and c.agent_id = a.agent_id
                     and c.environment = a.environment
                     and c.config_version_id = a.config_version_id
                    where a.tenant_id = %s
                      and a.application_id = %s
                      and a.agent_id = %s
                      and a.environment = %s
                      and c.lifecycle_status = 'PUBLISHED'
                    limit 1
                    """,
                    (tenant_id, application_id, agent_id, environment),
                )
                row = await cur.fetchone()

        if row is None:
            return None

        return ActiveAgentConfig(
            config_version_id=row["config_version_id"],
            published_config_hash=row["published_config_hash"],
            policy_merge_version=row["policy_merge_version"],
            config_document=row["config_document"],
        )
