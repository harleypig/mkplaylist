#!/bin/bash
# Script to check files for trailing whitespace and missing final newlines
# without modifying them

set -e

# Find all text files, excluding certain directories
mapfile -t files < <(find . -type f -not -path "*/\.*" -not -path "*/venv/*" -not -path "*/node_modules/*")

# Initialize error flags
trailing_whitespace_found=0
missing_newline_found=0

# Check for trailing whitespace
echo "Checking for trailing whitespace..."
for file in "${files[@]}"; do
  # Skip markdown files for trailing whitespace check
  if [[ "$file" != *.md ]]; then
    if grep -q "[[:space:]]$" "$file"; then
      echo "Trailing whitespace found in: $file"
      trailing_whitespace_found=1
    fi
  fi
done

# Check for missing final newlines
echo "Checking for missing final newlines..."
for file in "${files[@]}"; do
  if [ -s "$file" ] && [ -n "$(tail -c 1 "$file")" ]; then
    echo "Missing final newline in: $file"
    missing_newline_found=1
  fi
done

# Exit with error if any issues were found
if [ $trailing_whitespace_found -eq 1 ] || [ $missing_newline_found -eq 1 ]; then
  echo "Issues found. Please fix them before committing."
  exit 1
fi

echo "All files passed checks."
exit 0
