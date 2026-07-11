#!/usr/bin/env bash
# Release helper for larpfetch.
#
# Usage:
#   scripts/release.sh            # tag + push + publish to PyPI + GitHub release
#   scripts/release.sh gh-release  # only create the GitHub release for current version
set -euo pipefail

cd "$(dirname "$0")/.."

VERSION="$(uv run python -c "from larpfetch import __version__; print(__version__)")"
TAG="v${VERSION}"

SUMMARY="$(awk -v v="## v${VERSION}" '$0==v{f=1;next} f&&$0!="" {print;exit}' CHANGELOG.md)"
TITLE="v${VERSION}: ${SUMMARY}"
NOTES="$(just changelog-notes "${VERSION}")"

if [ "${1:-}" = "gh-release" ]; then
  shift
  gh release create "${TAG}" --title "${TITLE}" --notes "${NOTES}" "$@"
  exit 0
fi

# Full release
git tag "${TAG}"
git push origin main
git push origin "${TAG}"
just publish
gh release create "${TAG}" --title "${TITLE}" --notes "${NOTES}"
