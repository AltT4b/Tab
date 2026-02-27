# Skill: run-agent

Dispatch a task to a named Tab agent. Reads the agent's `AGENT.md`, resolves inheritance, loads supplemental rules, then runs the task in a subagent that embodies the agent's defined identity, process, and rules.

## Usage

```
/run-agent <agent-name> <task>
```

**Examples:**
- `/run-agent researcher "What are the top open-source AI agent frameworks in 2026?"`
- `/run-agent coder "Write a Python function to parse YAML frontmatter from a markdown string"`
- `/run-agent writer "Draft a README introduction for the Tab framework"`
- `/run-agent orchestrator "Produce a market analysis report on AI coding tools"`

To dispatch multiple agents in parallel, describe the agents and tasks in a single message — Claude will fan out Task calls simultaneously.

---

## Steps

### 1. Parse args

Extract `agent-name` and `task` from the skill args.

- If `agent-name` is missing: run `Glob("agents/*/AGENT.md")`, list the available agent names (directory names only), and ask the user to specify one.
- If `task` is missing: ask the user what task to run.

### 2. Locate agent definition

Read `agents/<agent-name>/AGENT.md` from the repo root.

- If the file does not exist: report the error, list available agents via `Glob("agents/*/AGENT.md")`, and stop.

### 3. Resolve inheritance

Parse the YAML frontmatter. If `extends: <path>` is present:

1. Read `agents/<path>/AGENT.md`.
2. Merge: parent body sections provide defaults; child sections with the same heading override the parent.
3. Repeat up to 3 levels. Stop if a cycle is detected.

Abstract agents (names prefixed with `_`) cannot be the target of `/run-agent` — report an error if the user attempts this.

### 4. Load supplemental rules

Check whether `agents/<agent-name>/rules/` exists. If it does, read each `.md` file in that directory and collect the content as additional constraints.

### 5. Compose agent context

Build the full agent context string:

```
<merged AGENT.md markdown body>

## Supplemental Rules

<contents of each rules/*.md file, separated by blank lines>
```

Omit the "Supplemental Rules" section if no rules files were found.

### 6. Dispatch the task

Call the Task tool with:

- `subagent_type`: `general-purpose`
- `description`: `"Running <agent-name> agent"`
- `prompt`:

```
You are acting as the following Tab agent. Follow its identity, process, rules, and output format exactly.

---
<agent context from step 5>
---

Your task:

<user-provided task>
```

For parallel dispatch (multiple agents, independent tasks), fire all Task calls in a single response.

### 7. Present output

Return the subagent's output to the user, prefixed with the agent name:

```
**[agent-name]:**

<output>
```

If multiple agents were dispatched in parallel, present each result under its own agent-name heading in the order they complete.
