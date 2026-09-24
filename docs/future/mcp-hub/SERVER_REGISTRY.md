# Nippan MCP Hub Server Registry

## Purpose

Central registry for all tools exposed through Nippan MCP Hub.

## Server Entry Model

Each MCP server should define:

- name
- endpoint
- owner
- capabilities
- authentication method
- permission scope
- audit policy
- health status

## Initial Registry

| Server | Purpose | Status |
|---|---|---|
| GitHub | Repository and development operations | Connected |
| OpenRouter | Model gateway | Planned |
| Supabase | Database and backend operations | Planned |
| Nippan Core | Internal platform services | Planned |

## Rules

- Least privilege access
- All actions logged
- Destructive operations require approval
- Agents only access assigned capabilities
