#!/usr/bin/env python3
"""
validate_role.py — Tab role bundle validator.

Usage:
    python scripts/validate_role.py roles/researcher
    python scripts/validate_role.py --all

Checks:
    1. role.yml exists and is valid YAML.
    2. role.yml conforms to schemas/role.schema.json.
    3. Inheritance chain resolves (no missing parents, no cycles, max depth 3).
    4. Abstract roles (_-prefixed) are not passed as direct targets unless --allow-abstract is set.
    5. File references in role.yml exist on disk (templates, hooks, rules, etc.).
"""

import argparse
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML is required. Run: pip install pyyaml --break-system-packages")
    sys.exit(1)

try:
    import jsonschema
except ImportError:
    print("ERROR: jsonschema is required. Run: pip install jsonschema --break-system-packages")
    sys.exit(1)

import json

# ── Paths ─────────────────────────────────────────────────────────────────────

REPO_ROOT = Path(__file__).parent.parent
ROLES_DIR = REPO_ROOT / "roles"
SCHEMA_PATH = REPO_ROOT / "schemas" / "role.schema.json"

MAX_INHERITANCE_DEPTH = 3

# ── Helpers ───────────────────────────────────────────────────────────────────

def load_yaml(path: Path) -> dict:
    with open(path) as f:
        return yaml.safe_load(f)

def load_schema() -> dict:
    with open(SCHEMA_PATH) as f:
        return json.load(f)

def is_abstract(role_dir: Path) -> bool:
    return role_dir.name.startswith("_") or any(
        part.startswith("_") for part in role_dir.parts
    )

# ── Validation steps ──────────────────────────────────────────────────────────

def check_role_yml_exists(role_dir: Path) -> list[str]:
    errors = []
    if not (role_dir / "role.yml").exists():
        errors.append(f"Missing required file: role.yml")
    return errors

def check_schema(role_data: dict, schema: dict) -> list[str]:
    errors = []
    validator = jsonschema.Draft7Validator(schema)
    for error in sorted(validator.iter_errors(role_data), key=lambda e: e.path):
        path = " > ".join(str(p) for p in error.absolute_path) or "root"
        errors.append(f"Schema violation at [{path}]: {error.message}")
    return errors

def resolve_inheritance_chain(role_dir: Path, visited: list[str] | None = None) -> tuple[list[str], list[str]]:
    """
    Returns (chain, errors).
    chain: list of role paths in inheritance order (child → ... → root).
    errors: list of error strings found during resolution.
    """
    visited = visited or []
    errors = []
    chain = [str(role_dir)]

    role_yml = role_dir / "role.yml"
    if not role_yml.exists():
        return chain, [f"role.yml not found at {role_yml}"]

    data = load_yaml(role_yml)
    extends = data.get("extends")

    if not extends:
        return chain, []

    # Cycle detection
    parent_path = str(ROLES_DIR / extends)
    if parent_path in visited:
        errors.append(f"Circular inheritance detected: {' → '.join(visited + [parent_path])}")
        return chain, errors

    # Depth check
    if len(visited) >= MAX_INHERITANCE_DEPTH:
        errors.append(
            f"Inheritance depth exceeds maximum ({MAX_INHERITANCE_DEPTH}). "
            f"Chain so far: {' → '.join(visited + [str(role_dir)])}"
        )
        return chain, errors

    parent_dir = ROLES_DIR / extends
    if not parent_dir.exists():
        errors.append(f"Parent role not found: '{extends}' (expected at {parent_dir})")
        return chain, errors

    parent_chain, parent_errors = resolve_inheritance_chain(
        parent_dir, visited=visited + [str(role_dir)]
    )
    chain.extend(parent_chain)
    errors.extend(parent_errors)
    return chain, errors

def check_file_references(role_dir: Path, role_data: dict) -> list[str]:
    """Check that files referenced in role.yml actually exist."""
    errors = []

    def check_ref(path_str: str, field: str):
        ref = role_dir / path_str
        if not ref.exists():
            errors.append(f"Referenced file not found [{field}]: {path_str}")

    # system_prompt template
    sp = role_data.get("system_prompt")
    if isinstance(sp, dict) and "template" in sp:
        check_ref(sp["template"], "system_prompt.template")

    # claude artifacts
    claude = role_data.get("claude", {})
    for skill_path in claude.get("skills", []):
        check_ref(skill_path, "claude.skills")
    for hook in claude.get("hooks", []):
        if "script" in hook:
            check_ref(hook["script"], f"claude.hooks[{hook.get('event', '?')}].script")
    for cmd in claude.get("commands", []):
        check_ref(cmd, "claude.commands")
    for rule in claude.get("rules", []):
        check_ref(rule, "claude.rules")

    # output schema
    output = role_data.get("output", {})
    if "schema" in output:
        check_ref(output["schema"], "output.schema")

    return errors

# ── Main validator ─────────────────────────────────────────────────────────────

def validate_role(role_dir: Path, schema: dict, allow_abstract: bool = False) -> bool:
    """Run all checks on a single role directory. Returns True if valid."""
    print(f"\n{'─' * 60}")
    print(f"Validating: {role_dir.relative_to(REPO_ROOT)}")
    print(f"{'─' * 60}")

    all_errors = []

    # Abstract guard
    if is_abstract(role_dir) and not allow_abstract:
        print("  ⚠ Skipped (abstract role — use --allow-abstract to validate)")
        return True

    # 1. role.yml exists
    existence_errors = check_role_yml_exists(role_dir)
    if existence_errors:
        for e in existence_errors:
            print(f"  ✗ {e}")
        return False

    # 2. Load YAML
    try:
        role_data = load_yaml(role_dir / "role.yml")
    except yaml.YAMLError as e:
        print(f"  ✗ YAML parse error: {e}")
        return False

    # 3. Schema validation
    schema_errors = check_schema(role_data, schema)
    all_errors.extend(schema_errors)

    # 4. Inheritance chain
    _, chain_errors = resolve_inheritance_chain(role_dir)
    all_errors.extend(chain_errors)

    # 5. File references
    ref_errors = check_file_references(role_dir, role_data)
    all_errors.extend(ref_errors)

    if all_errors:
        for e in all_errors:
            print(f"  ✗ {e}")
        print(f"\n  RESULT: FAILED ({len(all_errors)} error(s))")
        return False
    else:
        print(f"  ✓ All checks passed")
        return True

# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Validate one or all Tab role bundles against the role schema."
    )
    parser.add_argument(
        "role_path",
        nargs="?",
        help="Path to role directory (e.g. roles/researcher). Omit with --all."
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Validate all roles in the roles/ directory."
    )
    parser.add_argument(
        "--allow-abstract",
        action="store_true",
        help="Also validate abstract (_-prefixed) roles."
    )
    args = parser.parse_args()

    if not args.role_path and not args.all:
        parser.print_help()
        sys.exit(1)

    if not SCHEMA_PATH.exists():
        print(f"ERROR: Schema not found at {SCHEMA_PATH}")
        sys.exit(1)

    schema = load_schema()
    all_passed = True

    if args.all:
        expanded = []
        for d in sorted(ROLES_DIR.iterdir()):
            if not d.is_dir():
                continue
            # _base/ is a namespace directory — expand its children
            if d.name.startswith("_"):
                for sub in sorted(d.iterdir()):
                    if sub.is_dir():
                        expanded.append(sub)
            else:
                # Concrete role — the directory itself is the bundle
                expanded.append(d)
        role_dirs = expanded
    else:
        role_dirs = [Path(args.role_path)]

    results = []
    for role_dir in role_dirs:
        if not role_dir.exists():
            print(f"\nERROR: Role directory not found: {role_dir}")
            all_passed = False
            results.append((role_dir, False))
            continue
        passed = validate_role(role_dir, schema, allow_abstract=args.allow_abstract)
        results.append((role_dir, passed))
        if not passed:
            all_passed = False

    # Summary
    print(f"\n{'═' * 60}")
    print("SUMMARY")
    print(f"{'═' * 60}")
    for role_dir, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        label = role_dir.relative_to(REPO_ROOT) if role_dir.is_absolute() or REPO_ROOT in role_dir.parents else role_dir
        print(f"  {status}  {label}")

    total = len(results)
    passed_count = sum(1 for _, p in results if p)
    print(f"\n{passed_count}/{total} roles passed.")

    sys.exit(0 if all_passed else 1)

if __name__ == "__main__":
    main()
