#!/usr/bin/env bash
# Memory skill eval — deterministic checks
# Usage: ./check-run.sh [case-id]
# If no case-id, runs all checks against current memory state.

set -euo pipefail

MEMORY_DIR="$HOME/.claude/tab/memory"
PASS=0
FAIL=0
SKIP=0

pass() { echo "  PASS: $1"; PASS=$((PASS+1)); }
fail() { echo "  FAIL: $1"; FAIL=$((FAIL+1)); }
skip() { echo "  SKIP: $1"; SKIP=$((SKIP+1)); }

check_file_exists() {
  local file="$1" label="$2"
  if [[ -f "$file" ]]; then pass "$label"; else fail "$label"; fi
}

check_line_cap() {
  local file="$1" cap="$2" label="$3"
  if [[ ! -f "$file" ]]; then skip "$label (file not found)"; return; fi
  local lines
  lines=$(wc -l < "$file" | tr -d ' ')
  if (( lines <= cap )); then
    pass "$label ($lines lines, cap $cap)"
  else
    fail "$label ($lines lines, cap $cap)"
  fi
}

check_section_exists() {
  local file="$1" section="$2" label="$3"
  if grep -q "^## $section" "$file" 2>/dev/null; then
    pass "$label"
  else
    fail "$label"
  fi
}

check_section_count() {
  local file="$1" section="$2" expected="$3" label="$4"
  if [[ ! -f "$file" ]]; then skip "$label (file not found)"; return; fi
  local count
  count=$(grep -c "^## $section" "$file" || true)
  if (( count == expected )); then
    pass "$label ($count occurrences)"
  else
    fail "$label (expected $expected, found $count)"
  fi
}

check_contains() {
  local file="$1" pattern="$2" label="$3"
  if [[ ! -f "$file" ]]; then skip "$label (file not found)"; return; fi
  if grep -qi "$pattern" "$file" 2>/dev/null; then
    pass "$label"
  else
    fail "$label"
  fi
}

check_not_contains() {
  local file="$1" pattern="$2" label="$3"
  if [[ ! -f "$file" ]]; then pass "$label (file not found — OK)"; return; fi
  if grep -qi "$pattern" "$file" 2>/dev/null; then
    fail "$label (found '$pattern')"
  else
    pass "$label"
  fi
}

count_recent_entries() {
  local file="$1"
  if [[ ! -f "$file" ]]; then echo 0; return; fi
  # Count lines starting with "- " after "## Recent"
  awk '/^## Recent/{found=1; next} /^##/{found=0} found && /^- /{count++} END{print count+0}' "$file"
}

# --- Case checks ---

run_mc01() {
  echo "MC-01: New User — Index Creation"
  check_file_exists "$MEMORY_DIR/index.md" "index.md exists"
  check_section_exists "$MEMORY_DIR/index.md" "User" "User section present"
  check_section_exists "$MEMORY_DIR/index.md" "Active" "Active section present"
  check_section_exists "$MEMORY_DIR/index.md" "Recent" "Recent section present"
  check_line_cap "$MEMORY_DIR/index.md" 20 "Index under 20 lines"
}

run_mc02() {
  echo "MC-02: Index Cap — 20 Lines"
  check_line_cap "$MEMORY_DIR/index.md" 20 "Index cap respected"
  check_section_exists "$MEMORY_DIR/index.md" "User" "User section present"
  check_section_exists "$MEMORY_DIR/index.md" "Active" "Active section present"
  check_section_exists "$MEMORY_DIR/index.md" "Recent" "Recent section present"
}

run_mc03() {
  echo "MC-03: Notes Cap — 50 Lines"
  check_line_cap "$MEMORY_DIR/notes.md" 50 "Notes cap respected"
}

run_mc04() {
  echo "MC-04: Structured File Cap — 30 Lines"
  check_line_cap "$MEMORY_DIR/profile.md" 30 "Profile cap respected"
}

run_mc05() {
  echo "MC-05: Recent Section — 3 to 5 Entries"
  local count
  count=$(count_recent_entries "$MEMORY_DIR/index.md")
  if (( count >= 3 && count <= 5 )); then
    pass "Recent count in range ($count entries)"
  else
    fail "Recent count out of range ($count entries, expected 3-5)"
  fi
}

run_mc06() {
  echo "MC-06: Immediate Save — 'Remember This'"
  check_contains "$MEMORY_DIR/notes.md" "us-east-1" "us-east-1 in notes.md"
  if [[ $? -ne 0 ]]; then
    check_contains "$MEMORY_DIR/profile.md" "us-east-1" "us-east-1 in profile.md"
  fi
}

run_mc07() {
  echo "MC-07: Forget — Entry Removal"
  check_not_contains "$MEMORY_DIR/notes.md" "demo" "Demo entry removed from notes"
  check_not_contains "$MEMORY_DIR/notes.md" "2026-03-07" "Demo date removed from notes"
  # Verify other entries survived
  check_contains "$MEMORY_DIR/notes.md" "rate limiting" "Other entries intact (rate limiting)"
  check_contains "$MEMORY_DIR/notes.md" "PostgreSQL" "Other entries intact (PostgreSQL)"
}

run_mc10() {
  echo "MC-10: Trivial Skip — No Detail File Writes"
  # These checks assume seed files were snapshotted before the trial
  # In practice, diff against the seed. Here we just check no new files appeared.
  for f in goals.md learning.md; do
    if [[ -f "$MEMORY_DIR/$f" ]]; then
      fail "Unexpected file created: $f"
    else
      pass "No $f created"
    fi
  done
}

run_mc11() {
  echo "MC-11: Rewrite Not Append — Index Integrity"
  check_section_count "$MEMORY_DIR/index.md" "User" 1 "Single User section"
  check_section_count "$MEMORY_DIR/index.md" "Active" 1 "Single Active section"
  check_section_count "$MEMORY_DIR/index.md" "Recent" 1 "Single Recent section"
  check_line_cap "$MEMORY_DIR/index.md" 20 "Index cap after rewrite"
}

# --- Main ---

CASE="${1:-all}"

echo "=== Memory Skill Eval — Deterministic Checks ==="
echo "Memory dir: $MEMORY_DIR"
echo ""

case "$CASE" in
  MC-01) run_mc01 ;;
  MC-02) run_mc02 ;;
  MC-03) run_mc03 ;;
  MC-04) run_mc04 ;;
  MC-05) run_mc05 ;;
  MC-06) run_mc06 ;;
  MC-07) run_mc07 ;;
  MC-10) run_mc10 ;;
  MC-11) run_mc11 ;;
  all)
    run_mc01; echo ""
    run_mc02; echo ""
    run_mc03; echo ""
    run_mc04; echo ""
    run_mc05; echo ""
    run_mc06; echo ""
    run_mc07; echo ""
    run_mc10; echo ""
    run_mc11; echo ""
    ;;
  *) echo "Unknown case: $CASE"; exit 1 ;;
esac

echo ""
echo "=== Results: $PASS passed, $FAIL failed, $SKIP skipped ==="
exit $((FAIL > 0 ? 1 : 0))
