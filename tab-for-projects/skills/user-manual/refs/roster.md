# Agent Roster

Canonical reference for all agents in the tab-for-projects plugin. Load via `/user-manual roster`.

## Three-Layer Model

```
┌─────────────────────────────────────────────┐
│            ORCHESTRATION                     │
│               Manager                        │
├─────────────────────────────────────────────┤
│              ADVISORY                        │
│              Tech Lead                       │
├─────────────────────────────────────────────┤
│            EXECUTION                          │
│               Developer                       │
└─────────────────────────────────────────────┘
```

## Agent Reference

| Agent | Plugin ID | Layer | Role | Produces | Owns |
|-------|-----------|-------|------|----------|------|
| **Manager** | `tab-for-projects:manager` | Orchestration | Routes work to agents, tracks progress | Workflow state, dispatch briefs | Project lifecycle, agent coordination |
| **Tech Lead** | `tab-for-projects:tech-lead` | Advisory | Writes all KB documents, maintains codebase truth, decomposes work into tasks, manages KB health | All KB documents (design docs, ADRs, codebase docs, pattern records, convention docs) + task graphs | All document CRUD, task creation, KB health (10-doc soft cap) |
| **Developer** | `tab-for-projects:developer` | Execution | Implements tasks, writes tests, commits code | Code commits from worktrees, task status updates | Implementation, testing, commits, merges |

## Capabilities and Boundaries

### Manager

- **Can:** Read MCP state (projects, tasks, document summaries), spawn agents, update project fields, create tasks
- **Cannot:** Touch the codebase, fetch full document content, mark tasks done, do substantive work
- **MCP tools used:** All project/task/document list/get tools, Agent tool
- **Dispatch modes:** Direct dispatch (focused work per agent)

### Tech Lead

- **Can:** Read code (via subagents), read all KB documents, create/update/delete documents, attach/detach documents to projects, create tasks, wire dependencies
- **Cannot:** Modify the codebase
- **MCP tools used:** `list_documents`, `get_document`, `create_document`, `update_document`, `delete_document`, `update_project` (attach/detach docs), `list_tasks`, `create_task`, `update_task`, `get_dependency_graph`
- **Key behavior:** Single owner of all doc output; creates task graphs from investigation findings; KB health management with 10-doc soft cap

### Developer

- **Can:** Read/modify the codebase, read KB documents, read tasks, update task status and implementation
- **Cannot:** Create tasks, write documents, make design decisions
- **MCP tools used:** `get_task`, `update_task`, `list_documents`, `get_document`
- **Key behavior:** Claims task (in_progress), implements, tests, commits, merges worktree branch, marks done

## Handoff Guide

When to recommend handing off to another agent:

| You are | Situation | Hand off to |
|---------|-----------|-------------|
| **Any agent** | Need to understand who does what | Load `/user-manual roster` |
| **Manager** | Design decisions needed or documents need writing | **Tech Lead** |
| **Manager** | Tasks need creating from existing design | **Tech Lead** (with decomposition scope) |
| **Manager** | Tasks are ready for implementation | **Developer** (worktree) |
| **Tech Lead** | Tasks created, ready for development | Report to **Manager** for developer dispatch |
| **Developer** | Found additional work needed | Note in implementation field; **Manager** routes to tech lead |
| **Developer** | Requirements are unclear | Flag on task; **Manager** resolves |

## Document Flow

```
Tech Lead ──KB documents + tasks──> Developer
    │                                    │
    └──── codebase docs <── reads code ──┘
```

The tech lead is the single funnel for all document output and task decomposition. Design decisions, codebase truth, and task graphs all flow through the tech lead. The developer reads documents but never writes them.
