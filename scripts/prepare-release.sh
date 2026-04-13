#!/usr/bin/env bash
# prepare-release.sh — Prepare NEWS file and Git tag before PR to main
set -euo pipefail

# ---- Config ----
BASE_BRANCH="main"
WORK_BRANCH="dev"
NEWS_FILE="NEWS"

# ---- Validate branch ----
CURRENT_BRANCH=$(git symbolic-ref --short HEAD)
if [[ "$CURRENT_BRANCH" != "$WORK_BRANCH" ]]; then
  echo "Error: Must be on '$WORK_BRANCH' branch (currently on '$CURRENT_BRANCH')"
  exit 1
fi

# ---- Collect commits ahead of main ----
COMMITS=$(git log --oneline "${BASE_BRANCH}..${WORK_BRANCH}" 2>/dev/null || true)
if [[ -z "$COMMITS" ]]; then
  echo "No commits ahead of '$BASE_BRANCH'. Nothing to release."
  exit 0
fi

# ---- Generate tag name (vYYYYMMDD, with suffix if duplicate) ----
DATE_TAG="v$(date +%Y%m%d)"
EXISTING=$(git tag -l "${DATE_TAG}*" | sort -V | tail -1)
if [[ -z "$EXISTING" ]]; then
  TAG_NAME="$DATE_TAG"
elif [[ "$EXISTING" == "$DATE_TAG" ]]; then
  TAG_NAME="${DATE_TAG}.1"
else
  LAST_SUFFIX="${EXISTING##*.}"
  TAG_NAME="${DATE_TAG}.$((LAST_SUFFIX + 1))"
fi

TODAY=$(date +%Y-%m-%d)

# ---- Build NEWS section ----
DIVIDER="$(printf '%0.s-' {1..23})"
NEWS_SECTION="${TAG_NAME} (${TODAY})\n${DIVIDER}\n\nAdded:\n"

while IFS= read -r commit_line; do
  HASH=$(echo "$commit_line" | awk '{print $1}')
  SUBJECT=$(echo "$commit_line" | cut -d' ' -f2-)
  NEWS_SECTION+="  - ${SUBJECT} (${HASH})\n"
done <<< "$COMMITS"

NEWS_SECTION+="\nChanged:\n  (none)\n\nFixed:\n  (none)\n"

# ---- Prepend section to NEWS file ----
if [[ -f "$NEWS_FILE" ]]; then
  HEADER=$(head -2 "$NEWS_FILE")
  BODY=$(tail -n +3 "$NEWS_FILE")
  printf "%s\n\n%b\n%s\n" "$HEADER" "$NEWS_SECTION" "$BODY" > "$NEWS_FILE"
else
  printf "NEWS -- Notable changes for dev-ai-agent\n=========================================\n\n%b" \
    "$NEWS_SECTION" > "$NEWS_FILE"
fi

# ---- Open editor for review ----
echo ""
echo "Opening NEWS file for review. Save and close editor to continue."
echo ""
${EDITOR:-vi} "$NEWS_FILE"

# ---- Commit NEWS ----
git add "$NEWS_FILE"
git commit -m "Update NEWS for ${TAG_NAME}

Prepare release notes for ${TAG_NAME} (${TODAY}).

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"

# ---- Create annotated tag ----
COMMIT_LIST=$(git log --format="  - %s" "${BASE_BRANCH}..HEAD~1")
git tag -a "$TAG_NAME" -m "Release ${TAG_NAME} (${TODAY})

Changes in this release:
${COMMIT_LIST}"

# ---- Next steps ----
echo ""
echo "Done! Tag '${TAG_NAME}' created. Next steps:"
echo ""
echo "  git push origin ${WORK_BRANCH}"
echo "  git push origin ${TAG_NAME}"
echo "  # Then open a PR on GitHub: ${BASE_BRANCH} <- ${WORK_BRANCH}"
echo ""
