#!/bin/bash
set -euo pipefail

input=$(cat)
tool_name=$(echo "$input" | jq -r '.tool_name')
project_dir=$(echo "$input" | jq -r '.cwd')
plugin_root="${CLAUDE_PLUGIN_ROOT:-}"

# Extract the path to check based on tool type
case "$tool_name" in
  Read|Write|Edit)
    target_path=$(echo "$input" | jq -r '.tool_input.file_path // empty')
    ;;
  Glob|Grep)
    target_path=$(echo "$input" | jq -r '.tool_input.path // empty')
    ;;
  *)
    # Not a filesystem tool we guard — allow
    exit 0
    ;;
esac

# If no path specified (e.g. Glob/Grep default to cwd), allow
if [ -z "$target_path" ]; then
  exit 0
fi

# Resolve to absolute path (handle relative paths)
if [[ "$target_path" != /* ]]; then
  target_path="$project_dir/$target_path"
fi

# Normalize: resolve symlinks and ../ segments
resolved_path=$(cd "$(dirname "$target_path")" 2>/dev/null && pwd -P)/$(basename "$target_path") 2>/dev/null || resolved_path="$target_path"

# Check if path is within allowed directories
allowed=false

# Check project directory
if [[ "$resolved_path" == "$project_dir"/* || "$resolved_path" == "$project_dir" ]]; then
  allowed=true
fi

# Check plugin root
if [ -n "$plugin_root" ]; then
  if [[ "$resolved_path" == "$plugin_root"/* || "$resolved_path" == "$plugin_root" ]]; then
    allowed=true
  fi
fi

if [ "$allowed" = true ]; then
  exit 0
else
  cat >&2 <<EOF
{"hookSpecificOutput":{"permissionDecision":"deny"},"systemMessage":"Blocked: $tool_name tried to access '$target_path' which is outside the allowed directories (project: $project_dir, plugin: $plugin_root). Tab may only access files in the user's working directory and its own plugin directory."}
EOF
  exit 2
fi
