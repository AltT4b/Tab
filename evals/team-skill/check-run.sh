#!/usr/bin/env bash
#
# Post-run scorer for the team skill eval suite.
# Auto-scores 4 rubric dimensions: P2a, P3a, C1, C2.
#
# Usage: ./check-run.sh <run-id>
# Example: ./check-run.sh postgres-v-sqlite-20260306

set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 <run-id>"
  echo "Example: $0 postgres-v-sqlite-20260306"
  exit 1
fi

RUN_ID="$1"
RUN_DIR=".tab/team/${RUN_ID}"

if [[ ! -d "$RUN_DIR" ]]; then
  echo "FAIL: Run directory not found: ${RUN_DIR}"
  exit 1
fi

echo "Checking run: ${RUN_ID}"
echo "Directory: ${RUN_DIR}"
echo "---"

pass=0
fail=0
warn=0

# --- P2a: File output structure ---
echo ""
echo "P2a: File output"

round_dirs=("${RUN_DIR}"/round-*)
has_rounds=false
for d in "${round_dirs[@]}"; do
  if [[ -d "$d" ]]; then
    has_rounds=true
    round_name=$(basename "$d")
    agent_files=("${d}"/*.md)
    agent_count=0
    for f in "${agent_files[@]}"; do
      if [[ -f "$f" ]]; then
        agent_count=$((agent_count + 1))
        if [[ ! -s "$f" ]]; then
          echo "  WARN: Empty agent file: ${f}"
          warn=$((warn + 1))
        fi
      fi
    done
    if [[ $agent_count -eq 0 ]]; then
      echo "  FAIL: ${round_name}/ has no agent output files"
      fail=$((fail + 1))
    else
      echo "  OK: ${round_name}/ has ${agent_count} agent file(s)"
    fi
  fi
done

if $has_rounds; then
  echo "  SCORE: 2/2"
  pass=$((pass + 1))
else
  echo "  FAIL: No round-* directories found"
  echo "  SCORE: 0/2"
  fail=$((fail + 1))
fi

# --- P3a: Synthesis file ---
echo ""
echo "P3a: Synthesis file"

if [[ -f "${RUN_DIR}/synthesis.md" ]]; then
  synth_words=$(wc -w < "${RUN_DIR}/synthesis.md" | tr -d ' ')
  if [[ $synth_words -gt 50 ]]; then
    echo "  OK: synthesis.md exists (${synth_words} words)"
    echo "  SCORE: 2/2 (content check — not concatenated dumps — still needs manual review)"
    pass=$((pass + 1))
  else
    echo "  WARN: synthesis.md exists but only ${synth_words} words — may be a stub"
    echo "  SCORE: 1/2"
    warn=$((warn + 1))
  fi
else
  echo "  FAIL: synthesis.md not found"
  echo "  SCORE: 0/2"
  fail=$((fail + 1))
fi

# --- C1: Round cap (max 4) ---
echo ""
echo "C1: Round cap"

round_count=0
for d in "${RUN_DIR}"/round-*; do
  if [[ -d "$d" ]]; then
    round_count=$((round_count + 1))
  fi
done

if [[ $round_count -le 4 ]]; then
  echo "  OK: ${round_count} round(s) (cap: 4)"
  echo "  SCORE: 2/2"
  pass=$((pass + 1))
else
  echo "  FAIL: ${round_count} rounds — exceeds cap of 4"
  echo "  SCORE: 0/2"
  fail=$((fail + 1))
fi

# --- C2: Agent output cap (max 1000 words per file) ---
echo ""
echo "C2: Agent output cap"

over_cap=0
slightly_over=0
for d in "${RUN_DIR}"/round-*; do
  if [[ -d "$d" ]]; then
    for f in "${d}"/*.md; do
      if [[ -f "$f" ]]; then
        words=$(wc -w < "$f" | tr -d ' ')
        name="$(basename "$(dirname "$f")")/$(basename "$f")"
        if [[ $words -gt 1200 ]]; then
          echo "  FAIL: ${name} — ${words} words (grossly over cap)"
          over_cap=$((over_cap + 1))
        elif [[ $words -gt 1000 ]]; then
          echo "  WARN: ${name} — ${words} words (slightly over cap)"
          slightly_over=$((slightly_over + 1))
        else
          echo "  OK: ${name} — ${words} words"
        fi
      fi
    done
  fi
done

if [[ $over_cap -gt 0 ]]; then
  echo "  SCORE: 0/2"
  fail=$((fail + 1))
elif [[ $slightly_over -gt 0 ]]; then
  echo "  SCORE: 1/2"
  warn=$((warn + 1))
else
  echo "  SCORE: 2/2"
  pass=$((pass + 1))
fi

# --- Summary ---
echo ""
echo "==="
auto_score=$((pass * 2))
echo "Auto-scored: ${auto_score}/8 (4 dimensions)"
echo "  Passed: ${pass}"
echo "  Warnings: ${warn}"
echo "  Failed: ${fail}"
echo ""
echo "Manual scoring still needed: P0, P1a, P1b, P1c, P2b, P3b"
echo "Record all scores in evals/team-skill/results.md"
