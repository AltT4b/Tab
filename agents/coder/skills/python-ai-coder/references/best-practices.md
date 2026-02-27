# Best Practices Reference

## Table of Contents
- [Type Hints & Docstrings](#type-hints--docstrings)
- [Readability Over Cleverness](#readability-over-cleverness)
- [Security & Prompt Injection](#security--prompt-injection)
- [Async Best Practices](#async-best-practices)
- [CrewAI-Specific Patterns](#crewai-specific-patterns)

---

## Type Hints & Docstrings

All public functions and methods require full type annotations. Docstrings follow Google style.
Use `TypedDict`, `dataclass`, or Pydantic `BaseModel` for structured data — no bare dicts for config.

```python
# ✅ Correct
async def run_agent(persona: PersonaConfig, task: str) -> AgentResult:
    """
    Execute a task using a configured persona agent.

    Args:
        persona: The persona configuration defining role, goal, and backstory.
        task: The task description to execute.

    Returns:
        AgentResult containing output, token usage, and execution metadata.

    Raises:
        AgentExecutionError: If the agent fails to complete the task.

    Example:
        result = await run_agent(persona=coder_persona, task="Review auth module")
    """

# ❌ Incorrect
def run_agent(persona, task):
    """Runs the agent."""
```

---

## Readability Over Cleverness

Name variables and functions for intent, not implementation. No one-liners that sacrifice clarity.
Avoid deeply nested logic — extract to named functions. Magic values become named constants.

```python
# ✅ Correct
MAX_AGENT_RETRIES = 3
SUPPORTED_PROVIDERS = {"anthropic", "openai", "google"}

# ❌ Incorrect — magic values buried in condition
if len(results) > 3 and provider in {"anthropic", "openai", "google"}:
```

---

## Security & Prompt Injection

- **Never interpolate raw user input directly into agent prompts** — sanitize or wrap in structured context blocks
- Validate all tool inputs before execution — treat tool args like untrusted data
- Never log full prompt content at INFO level — use DEBUG with redaction for PII/secrets
- Use `ANTHROPIC_API_KEY` via environment variables only — never hardcode or accept from config files

```python
# ✅ Safe prompt construction
def build_task_prompt(user_input: str, context: TaskContext) -> str:
    sanitized = sanitize_input(user_input)  # strip injection patterns
    return TASK_TEMPLATE.format(
        context=context.to_safe_string(),
        request=sanitized
    )

# ❌ Injection risk
prompt = f"Complete this task: {user_input}"
```

---

## Async Best Practices

- Use `async def` for all agent execution, tool calls, and LLM API calls
- Never call `asyncio.run()` inside an async context — use `await` consistently
- Use `asyncio.gather()` for parallel agent tasks, not sequential `await` chains
- Handle `asyncio.CancelledError` explicitly in long-running agent loops
- Use `asyncio.timeout()` (Python 3.11+) or `asyncio.wait_for()` for LLM call timeouts

```python
# ✅ Parallel agent execution
results = await asyncio.gather(
    agent_a.execute(task_a),
    agent_b.execute(task_b),
    return_exceptions=True
)

# ❌ Sequential when parallel is possible
result_a = await agent_a.execute(task_a)
result_b = await agent_b.execute(task_b)
```

---

## CrewAI-Specific Patterns

- Define agents in `agents.yaml` — keep Python code for logic, not config
- Use `{variable}` interpolation in YAML for dynamic personas — avoid string formatting in Python
- Assign tools explicitly per agent — never give all tools to all agents
- Use `allow_delegation=False` unless the agent genuinely needs to delegate
- Set `max_iter` and `max_rpm` on all agents in production — unbounded agents are a cost and reliability risk
- Pass structured context between tasks using `context=[previous_task]` — don't rely on agent memory alone
- Use `verbose=False` in production; enable per-agent with an env flag for debugging
