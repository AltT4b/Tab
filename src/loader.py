"""
Role loader — loads a role bundle from roles/, resolves inheritance,
deep-merges configs, and renders Jinja2 system prompts.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml
import jsonschema
import jinja2

REPO_ROOT = Path(__file__).parent.parent
ROLES_DIR = REPO_ROOT / "roles"
SCHEMA_PATH = REPO_ROOT / "schemas" / "role.schema.json"
MAX_DEPTH = 3

# List-typed fields that are union-merged (child never loses parent values).
# All other fields use scalar merge (child wins outright).
LIST_UNION_KEYS: frozenset[str] = frozenset({
    "allow", "deny",
    "allowed_paths", "forbidden_patterns",
    "rules", "skills", "commands",
    "can_spawn", "can_delegate_to",
    "tags",
})


class RoleError(Exception):
    pass


# ── Dataclasses ───────────────────────────────────────────────────────────────

@dataclass
class ModelConfig:
    id: str
    temperature: float = 0.5
    max_tokens: int = 8096


@dataclass
class AutonomyConfig:
    max_tool_calls: int = 25
    max_cost_usd: float = 0.50
    checkpoint_every: int = 10
    allowed_paths: list[str] = field(default_factory=lambda: ["./workspace/**"])
    forbidden_patterns: list[str] = field(default_factory=lambda: ["rm -rf", "DROP TABLE"])


@dataclass
class OutputConfig:
    format: str = "markdown"
    schema_path: Path | None = None
    destinations: list[dict] = field(default_factory=lambda: [{"type": "stdout"}])


@dataclass
class OrchestrationConfig:
    role: str = "worker"
    can_spawn: list[str] = field(default_factory=list)
    can_delegate_to: list[str] = field(default_factory=list)
    max_sub_agents: int = 3
    delegation_strategy: str = "sequential"


@dataclass
class ResolvedRole:
    name: str
    role_dir: Path
    model: ModelConfig
    system_prompt: str
    tools_allow: list[str]
    tools_deny: list[str]
    autonomy: AutonomyConfig
    output: OutputConfig
    orchestration: OrchestrationConfig | None
    rules: list[str]
    skills: list[str]
    raw: dict[str, Any]


# ── Public entry point ────────────────────────────────────────────────────────

def load_role(
    role_name: str,
    run_id: str,
    extra_vars: dict[str, str] | None = None,
) -> ResolvedRole:
    """
    Load, merge, and render a role bundle.

    role_name: directory name inside roles/ (e.g. "orchestrator", "researcher")
    run_id:    injected into Jinja2 render context for output path templates
    extra_vars: optional overrides for system_prompt.vars
    """
    role_dir = ROLES_DIR / role_name

    if not role_dir.exists():
        raise RoleError(f"Role directory not found: {role_dir}")

    # Abstract roles cannot be instantiated directly
    if _is_abstract(role_dir):
        raise RoleError(
            f"Cannot instantiate abstract role '{role_name}'. "
            "Abstract roles are prefixed with '_'."
        )

    # Build merged config: walk chain root→child, fold merges left-to-right
    chain = _resolve_chain(role_dir)  # [root_data, ..., child_data]
    merged: dict[str, Any] = {}
    for layer in chain:
        merged = _deep_merge(merged, layer)

    # Determine the role_dir for the declaring role (child wins for template path)
    declaring_dir = _find_declaring_dir(role_dir)

    # Render system prompt
    sp_config = merged.get("system_prompt", "You are a helpful AI agent.")
    vars_: dict[str, str] = {}
    if isinstance(sp_config, dict):
        vars_ = dict(merged.get("system_prompt", {}).get("vars", {}))
    if extra_vars:
        vars_.update(extra_vars)

    rendered_prompt = _render_system_prompt(declaring_dir, sp_config, vars_, run_id)

    # Load rule and skill file contents
    claude_section = merged.get("claude", {})
    rule_paths: list[str] = claude_section.get("rules", [])
    rules = _load_rules(declaring_dir, rule_paths)
    if rules:
        rendered_prompt += "\n\n---\n\n## Rules\n\n" + "\n\n".join(rules)

    skill_paths: list[str] = claude_section.get("skills", [])
    skills = _load_skills(declaring_dir, skill_paths)
    if skills:
        rendered_prompt += "\n\n---\n\n## Skills\n\n" + "\n\n".join(skills)

    # Build typed sub-configs
    model_raw = merged.get("model", {})
    model = ModelConfig(
        id=model_raw.get("id", "claude-sonnet-4-5-20250929"),
        temperature=model_raw.get("temperature", 0.5),
        max_tokens=model_raw.get("max_tokens", 8096),
    )

    tools_raw = merged.get("tools", {})
    tools_allow: list[str] = tools_raw.get("allow", [])
    tools_deny: list[str] = tools_raw.get("deny", [])

    autonomy_raw = merged.get("autonomy", {})
    autonomy = AutonomyConfig(
        max_tool_calls=autonomy_raw.get("max_tool_calls", 25),
        max_cost_usd=autonomy_raw.get("max_cost_usd", 0.50),
        checkpoint_every=autonomy_raw.get("checkpoint_every", 10),
        allowed_paths=autonomy_raw.get("allowed_paths", ["./workspace/**"]),
        forbidden_patterns=autonomy_raw.get("forbidden_patterns", ["rm -rf", "DROP TABLE"]),
    )

    output_raw = merged.get("output", {})
    schema_ref = output_raw.get("schema")
    schema_path = (declaring_dir / schema_ref).resolve() if schema_ref else None
    output = OutputConfig(
        format=output_raw.get("format", "markdown"),
        schema_path=schema_path,
        destinations=output_raw.get("destinations", [{"type": "stdout"}]),
    )

    orch_raw = merged.get("orchestration")
    orchestration: OrchestrationConfig | None = None
    if orch_raw:
        orchestration = OrchestrationConfig(
            role=orch_raw.get("role", "worker"),
            can_spawn=orch_raw.get("can_spawn", []),
            can_delegate_to=orch_raw.get("can_delegate_to", []),
            max_sub_agents=orch_raw.get("max_sub_agents", 3),
            delegation_strategy=orch_raw.get("delegation_strategy", "sequential"),
        )

    return ResolvedRole(
        name=merged.get("name", role_name),
        role_dir=declaring_dir,
        model=model,
        system_prompt=rendered_prompt,
        tools_allow=tools_allow,
        tools_deny=tools_deny,
        autonomy=autonomy,
        output=output,
        orchestration=orchestration,
        rules=rules,
        skills=skills,
        raw=merged,
    )


# ── Internals ────────────────────────────────────────────────────────────────

def _is_abstract(role_dir: Path) -> bool:
    """True if any path component starts with '_'."""
    return any(part.startswith("_") for part in role_dir.parts)


def _find_declaring_dir(role_dir: Path) -> Path:
    """Return the role_dir itself (used as the base for relative file references)."""
    return role_dir


def _load_schema() -> dict:
    with open(SCHEMA_PATH) as f:
        return json.load(f)


def _load_raw_yaml(role_dir: Path) -> dict:
    """Load role.yml and validate against the JSON Schema."""
    role_yml = role_dir / "role.yml"
    if not role_yml.exists():
        raise RoleError(f"role.yml not found at {role_yml}")

    with open(role_yml) as f:
        data = yaml.safe_load(f)

    if data is None:
        raise RoleError(f"role.yml is empty: {role_yml}")

    schema = _load_schema()
    validator = jsonschema.Draft7Validator(schema)
    errors = list(validator.iter_errors(data))
    if errors:
        msgs = "; ".join(e.message for e in errors[:3])
        raise RoleError(f"Schema validation failed for {role_dir.name}: {msgs}")

    return data


def _resolve_chain(role_dir: Path, visited: list[str] | None = None) -> list[dict]:
    """
    Walk the extends chain and return a list of raw dicts from root → child.
    The child's dict is last so that _deep_merge gives child values precedence.
    """
    visited = visited or []
    abs_path = str(role_dir.resolve())

    if abs_path in visited:
        raise RoleError(f"Circular inheritance detected: {' → '.join(visited + [abs_path])}")

    if len(visited) >= MAX_DEPTH:
        raise RoleError(
            f"Inheritance depth exceeds maximum ({MAX_DEPTH}). "
            f"Chain: {' → '.join(visited + [abs_path])}"
        )

    data = _load_raw_yaml(role_dir)
    extends = data.get("extends")

    if not extends:
        return [data]

    parent_dir = ROLES_DIR / extends
    if not parent_dir.exists():
        raise RoleError(
            f"Parent role '{extends}' not found (expected at {parent_dir})"
        )

    parent_chain = _resolve_chain(parent_dir, visited=visited + [abs_path])
    return parent_chain + [data]


def _deep_merge(parent: dict, child: dict) -> dict:
    """
    Deep-merge child into parent.
    - List keys in LIST_UNION_KEYS: union (parent + child, deduped, order-preserving)
    - Dict values: recurse
    - Scalar values: child wins
    """
    result = dict(parent)

    for key, child_val in child.items():
        if key not in result:
            result[key] = child_val
            continue

        parent_val = result[key]

        if key in LIST_UNION_KEYS and isinstance(parent_val, list) and isinstance(child_val, list):
            # Union: parent items first, then child additions (deduped, order-preserving)
            result[key] = list(dict.fromkeys(parent_val + child_val))

        elif isinstance(parent_val, dict) and isinstance(child_val, dict):
            result[key] = _deep_merge(parent_val, child_val)

        else:
            # Scalar: child wins
            result[key] = child_val

    return result


def _render_system_prompt(
    role_dir: Path,
    sp_config: dict | str,
    vars_: dict[str, str],
    run_id: str,
) -> str:
    """
    Render the system prompt.

    Two-pass for template mode:
    1. Render vars values through Jinja2 to resolve {{ var | default(...) }} in var strings
    2. Render the .j2 template with the resolved vars + run_id

    Falls back to inline string if sp_config is a str.
    """
    render_ctx: dict[str, Any] = {**vars_, "run_id": run_id}

    # Pass 1: resolve any Jinja2 expressions inside the vars values themselves
    env = jinja2.Environment(
        undefined=jinja2.Undefined,
        keep_trailing_newline=True,
    )
    resolved_vars: dict[str, str] = {}
    for k, v in vars_.items():
        if isinstance(v, str) and "{{" in v:
            try:
                resolved_vars[k] = env.from_string(v).render(**render_ctx)
            except jinja2.TemplateError:
                resolved_vars[k] = v
        else:
            resolved_vars[k] = str(v) if v is not None else ""

    final_ctx = {**resolved_vars, "run_id": run_id}

    if isinstance(sp_config, str):
        return sp_config

    # Template mode
    template_rel = sp_config.get("template")
    if not template_rel:
        return sp_config.get("inline", "You are a helpful AI agent.")

    template_path = role_dir / template_rel
    if not template_path.exists():
        raise RoleError(f"System prompt template not found: {template_path}")

    # Pass 2: render the .j2 file
    file_env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(str(role_dir)),
        undefined=jinja2.Undefined,
        keep_trailing_newline=True,
    )
    try:
        template = file_env.get_template(template_rel)
        return template.render(**final_ctx)
    except jinja2.TemplateError as e:
        raise RoleError(f"Failed to render system prompt template: {e}") from e


def _load_rules(role_dir: Path, rule_paths: list[str]) -> list[str]:
    """Load rule .md file contents. Paths are relative to role_dir."""
    contents = []
    for rel_path in rule_paths:
        full = role_dir / rel_path
        if not full.exists():
            raise RoleError(f"Rule file not found: {full}")
        contents.append(full.read_text())
    return contents


def _load_skills(role_dir: Path, skill_paths: list[str]) -> list[str]:
    """Load SKILL.md from each skill directory. Paths are relative to role_dir."""
    contents = []
    for rel_path in skill_paths:
        full = role_dir / rel_path / "SKILL.md"
        if not full.exists():
            raise RoleError(f"Skill SKILL.md not found: {full}")
        contents.append(full.read_text())
    return contents
