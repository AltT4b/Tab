"""Grimoire registry loader for the personality plugin's SKILL.md files.

The CLI's job at startup is to figure out which skill (if any) the user
just invoked. Rather than rebuild a gating layer, we lean on grimoire:
each ``SKILL.md`` becomes a gated row in a corpus, with the skill's
``description`` as the match-text. ``match(query)`` then asks grimoire
"does this clear any item's bar?" — silent below threshold, named hit
above.

The loader is deliberately small. It walks
``plugins/tab/skills/*/SKILL.md``, parses YAML frontmatter for ``name``
and ``description`` (``argument-hint`` is optional), and seeds a
:class:`grimoire.Gate` with the resulting rows. The chat/ask wiring
holds the registry and queries it per turn — silence-by-default is the
safety property; below-threshold input falls through to the agent.

What the loader does **not** do:

- Invoke skills. It returns "this input matches skill X above
  threshold" or "no match"; what to do next is the caller's business.
- Tune per-item thresholds. v0 ships one default for every skill. The
  per-item tuning UX is owned by a deferred design ticket
  (config file vs CLI command vs implicit-from-usage — TBD).
- Load the ``tab-for-projects`` skills. Those stay Claude-Code-shaped;
  the CLI sticks to the personality plugin.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

import yaml

if TYPE_CHECKING:  # avoid forcing grimoire's Postgres import path at module load
    from grimoire import Gate, Hit


# The corpus key under which all v0 personality-skill rows live. Single
# corpus is the right shape today — every skill is a peer, threshold is
# uniform, and grimoire's mismatch-detection works at the corpus level.
SKILL_CORPUS = "tab-cli-skills"


# v0 single-default threshold across every skill. Calibrated against
# ollama's ``nomic-embed-text`` on description-shaped prompts: cosine
# similarity for an obvious paraphrase ("draw me a dinosaur" against the
# draw-dino description) sits comfortably above this; an unrelated query
# ("what's the weather in Berlin") sits below.
#
# Per-item tuning is the deferred design ticket's job — config file vs
# CLI command vs implicit-from-usage is unresolved, and v0 doesn't need
# it to ship. Picking too-low here over-routes (false positives, the
# agent never sees a chunk of input); picking too-high under-routes
# (skills silently miss). Mid-range biases toward under-routing, which
# is the safer failure mode given silence-by-default.
DEFAULT_THRESHOLD = 0.55


@dataclass(frozen=True, slots=True)
class SkillRecord:
    """One parsed ``SKILL.md`` ready to seed grimoire.

    ``threshold`` is held alongside the parsed fields so the loader can
    pass per-row thresholds to :meth:`grimoire.Gate.seed` without going
    back to a constant; today every record ships with
    :data:`DEFAULT_THRESHOLD`, but the deferred per-item-tuning ticket
    lands on this same field.
    """

    name: str
    description: str
    threshold: float
    path: Path
    argument_hint: str | None = None


class SkillFrontmatterError(ValueError):
    """A ``SKILL.md`` was missing required frontmatter or malformed.

    Loud rather than skipped: the CLI's whole gating story rests on
    correct registration, and a silently-dropped skill would make the
    agent feel mysteriously unresponsive. Better to fail loading and
    surface the broken file.
    """


class SkillRegistry:
    """Holds the loaded skill records and wraps the grimoire gate.

    The registry is what ``tab chat`` and ``tab ask`` consult per turn:
    given user input, did anything match? The wrapper is intentionally
    thin — it exposes :meth:`match` (gating) and :attr:`records` (what
    was registered, for diagnostics and the ``tab list`` surface that
    will follow). Any deeper grimoire call (``explain``, ``neighbors``)
    can reach :attr:`gate` directly.
    """

    def __init__(self, gate: Gate, records: Iterable[SkillRecord]) -> None:
        self._gate = gate
        # Tuple, not list: the registry is read-mostly post-load and
        # downstream callers shouldn't be able to mutate the snapshot
        # they got back.
        self._records: tuple[SkillRecord, ...] = tuple(records)

    @property
    def gate(self) -> Gate:
        """The underlying :class:`grimoire.Gate`. Exposed for diagnostics."""
        return self._gate

    @property
    def records(self) -> tuple[SkillRecord, ...]:
        """Every skill registered in load order."""
        return self._records

    def match(self, query: str) -> Hit | None:
        """Return the top-1 :class:`grimoire.Hit` for ``query``.

        Mirror of :meth:`grimoire.Gate.match` — we don't reshape the
        return type because callers will want ``passed``, ``similarity``,
        and ``threshold`` to log diagnostics ("almost matched X with
        0.51 vs 0.55"). The chat wiring decides what to do with a
        non-passing hit; the registry just relays.
        """
        return self._gate.match(query)


def parse_skill_frontmatter(path: Path) -> SkillRecord:
    """Read a ``SKILL.md`` and return its parsed frontmatter.

    Required keys: ``name``, ``description``. Optional: ``argument-hint``.
    Anything else in the frontmatter is ignored — the parent
    ``CLAUDE.md`` documents the convention that nothing else should be
    added, so unknown keys are a planner-side problem to flag, not a
    loader-side translation problem.

    Raises :class:`SkillFrontmatterError` for missing/invalid documents.
    """
    text = path.read_text(encoding="utf-8")
    frontmatter = _extract_frontmatter(text, path)

    name = frontmatter.get("name")
    description = frontmatter.get("description")

    if not isinstance(name, str) or not name.strip():
        raise SkillFrontmatterError(
            f"{path}: missing or empty 'name' in frontmatter",
        )
    if not isinstance(description, str) or not description.strip():
        raise SkillFrontmatterError(
            f"{path}: missing or empty 'description' in frontmatter",
        )

    argument_hint_raw = frontmatter.get("argument-hint")
    if argument_hint_raw is not None and not isinstance(argument_hint_raw, str):
        raise SkillFrontmatterError(
            f"{path}: 'argument-hint' must be a string when present",
        )

    return SkillRecord(
        name=name.strip(),
        description=description.strip(),
        threshold=DEFAULT_THRESHOLD,
        path=path,
        argument_hint=argument_hint_raw.strip() if argument_hint_raw else None,
    )


def load_skill_registry(
    plugins_dir: Path,
    *,
    gate: Gate | None = None,
) -> SkillRegistry:
    """Walk ``plugins_dir/tab/skills/*/SKILL.md`` and seed a grimoire gate.

    The signature documented in the task is ``(plugins_dir) ->
    SkillRegistry``; the keyword-only ``gate=`` is a test seam mirroring
    grimoire's own ``Gate(repository=None)`` shape. When omitted, the
    function constructs the canonical gate via
    :meth:`grimoire.Gate.from_settings` (Ollama + the shared pgvector
    pool). When provided, the caller has already wired an embedder and
    repository — typically a fake pair for unit tests.

    Returns a :class:`SkillRegistry` ready to answer ``match(query)``.

    Notes:

    - The walker only descends into ``plugins_dir/tab/skills/`` —
      the ``tab-for-projects`` plugin is deliberately not loaded, per
      the v0 scope split in the Tab CLI decision doc.
    - Skills are seeded in sorted order so the registry is
      deterministic across runs (filesystem iteration order isn't).
    - An empty skills directory is not an error; the registry returns
      no matches. Whether that's the user's intent or a packaging miss
      is the caller's call.
    """
    skills_dir = plugins_dir / "tab" / "skills"
    if not skills_dir.is_dir():
        raise FileNotFoundError(
            f"expected personality skills directory at {skills_dir}",
        )

    # Sort by skill-folder name. The glob pattern keeps us scoped to
    # immediate children of ``skills/`` — nested ``SKILL.md`` files
    # would be a structural surprise and shouldn't be silently picked
    # up.
    skill_md_paths = sorted(skills_dir.glob("*/SKILL.md"))
    records = [parse_skill_frontmatter(path) for path in skill_md_paths]

    if gate is None:
        # Lazy import: grimoire's top-level ``Gate.from_settings`` pulls
        # in pgvector and ollama at first call. Tests that pass an
        # injected gate avoid the import entirely, which keeps the
        # ``tab_cli.registry`` module cheap to import in environments
        # that don't have the runtime stack wired up yet.
        from grimoire import Gate

        gate = Gate.from_settings(corpus=SKILL_CORPUS)

    if records:
        gate.seed(
            (record.name, record.description, record.threshold)
            for record in records
        )

    return SkillRegistry(gate=gate, records=records)


# --------------------------------------------------------------- internals


def _extract_frontmatter(text: str, path: Path) -> dict[str, object]:
    """Pull the YAML frontmatter block out of a Markdown file.

    Frontmatter is the standard Jekyll-shaped fence: a leading ``---``
    on its own line, a trailing ``---`` on its own line, YAML in
    between. Anything else (no fence, single fence, non-mapping
    content) raises :class:`SkillFrontmatterError`.
    """
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise SkillFrontmatterError(
            f"{path}: file does not start with a '---' frontmatter fence",
        )

    closing_index: int | None = None
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            closing_index = index
            break

    if closing_index is None:
        raise SkillFrontmatterError(
            f"{path}: frontmatter fence is not closed",
        )

    yaml_block = "\n".join(lines[1:closing_index])
    try:
        parsed = yaml.safe_load(yaml_block)
    except yaml.YAMLError as exc:
        raise SkillFrontmatterError(
            f"{path}: frontmatter is not valid YAML ({exc})",
        ) from exc

    if not isinstance(parsed, dict):
        raise SkillFrontmatterError(
            f"{path}: frontmatter must be a YAML mapping, got {type(parsed).__name__}",
        )

    return parsed
