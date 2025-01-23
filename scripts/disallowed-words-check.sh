#!/usr/bin/env bash

DISALLOWED_WORDS_FILE=".github/disallowed-words.txt"

# 1) If the file doesn't exist, fail the commit.
if [[ ! -f "$DISALLOWED_WORDS_FILE" ]]; then
  echo "ERROR: $DISALLOWED_WORDS_FILE not found."
  echo "Cannot proceed with disallowed word checks."
  exit 1
fi

# 2) If Git LFS isn't installed, fail the commit.
if ! command -v git-lfs &>/dev/null; then
  echo "ERROR: Git LFS not installed or not in PATH."
  echo "Cannot proceed with disallowed word checks."
  exit 1
fi

# 3) If the file is still an LFS pointer (not synced), fail the commit.
if grep -q "https://git-lfs.github.com/spec/v1" "$DISALLOWED_WORDS_FILE"; then
  echo "ERROR: $DISALLOWED_WORDS_FILE is an LFS pointer but not synced."
  echo "Cannot proceed with disallowed word checks."
  exit 1
fi

# 4) Read the disallowed words (one per line).
DISALLOWED_WORDS="$(grep -v '^[[:space:]]*$' "$DISALLOWED_WORDS_FILE")"
if [[ -z "$DISALLOWED_WORDS" ]]; then
  echo "ERROR: No disallowed words found in $DISALLOWED_WORDS_FILE."
  echo "Cannot proceed with disallowed word checks."
  exit 1
fi

# Build a single regex WITHOUT word boundaries.
# NOTE: This is intentionally strict. For example, banning "cat" also flags "catastrophic".
# Will tweak and change this to a more lenient regex later.
DISALLOWED_REGEX="($(echo "$DISALLOWED_WORDS" | paste -s -d '|' -))"

# 5) Find staged files that are Added (A) or Modified (M).
FILES_TO_CHECK=$(git diff --cached --name-status | egrep '^[AM]' | cut -f2)
# FILES_TO_CHECK=$(git ls-files)  # Uncomment this to check ALL files - CAUTION: SLOW!

FAILED=0

# 6) For each file:
#    - Check the filename itself.
#    - Check the file contents (if it exists).
for FILE in $FILES_TO_CHECK; do
  FILENAME_MATCHES=$(echo "$FILE" | grep -i -E -o "$DISALLOWED_REGEX")
  if [[ -n "$FILENAME_MATCHES" ]]; then
    echo "ERROR: Filename '$FILE' contains these disallowed words:"
    echo "$FILENAME_MATCHES"
    FAILED=1
  fi

  if [[ -f "$FILE" ]]; then
    CONTENT_MATCHES=$(grep -I -i -E -o "$DISALLOWED_REGEX" "$FILE" | sort -u)
    if [[ -n "$CONTENT_MATCHES" ]]; then
      echo "ERROR: File '$FILE' contains these disallowed words:"
      echo "$CONTENT_MATCHES"
      FAILED=1
    fi
  fi
done

# 7) Block commit if any violations were found.
if [[ $FAILED -eq 1 ]]; then
  exit 1
fi

exit 0
