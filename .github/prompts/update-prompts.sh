#!/usr/bin/env bash
set -euo pipefail

# Auto-update script for prompt templates from Coding-Krakken/prompts repository
# This script fetches the latest prompt templates and updates the local copies

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_URL="https://github.com/Coding-Krakken/prompts.git"
BRANCH="main"
SOURCE_PATH="Development/prompt-templates"
TEMP_DIR=$(mktemp -d)

echo "🔄 Updating prompt templates from Coding-Krakken/prompts repository..."

# Ensure cleanup on exit
cleanup() {
    if [ -d "${TEMP_DIR}" ]; then
        rm -rf "${TEMP_DIR}"
    fi
}
trap cleanup EXIT

# Clone repository with shallow clone for speed
echo "📦 Cloning repository (shallow clone)..."
if ! git clone --depth 1 --branch "${BRANCH}" "${REPO_URL}" "${TEMP_DIR}" >/dev/null 2>&1; then
    echo "❌ Error: Failed to clone repository"
    exit 1
fi

# Verify source path exists
if [ ! -d "${TEMP_DIR}/${SOURCE_PATH}" ]; then
    echo "❌ Error: Source path '${SOURCE_PATH}' not found in repository"
    exit 1
fi

# Check if there are any prompt files to copy
PROMPT_COUNT=$(find "${TEMP_DIR}/${SOURCE_PATH}" -maxdepth 1 -type f -name "*.prompt.md" | wc -l)
if [ "${PROMPT_COUNT}" -eq 0 ]; then
    echo "❌ Error: No *.prompt.md files found in ${SOURCE_PATH}"
    exit 1
fi

echo "📋 Found ${PROMPT_COUNT} prompt template(s) to update"

# Remove old prompt files (preserve the script itself and any other files)
echo "🗑️  Removing old prompt templates..."
find "${SCRIPT_DIR}" -maxdepth 1 -type f -name "*.prompt.md" -delete

# Copy new files
echo "📥 Copying new prompt templates..."
cp "${TEMP_DIR}/${SOURCE_PATH}"/*.prompt.md "${SCRIPT_DIR}/"

# List updated files
echo ""
echo "✅ Prompt templates updated successfully!"
echo ""
echo "📄 Updated files:"
ls -1 "${SCRIPT_DIR}"/*.prompt.md | xargs -n1 basename

echo ""
echo "💡 Review the changes and commit them to your repository:"
echo "   git diff .github/prompts/"
echo "   git add .github/prompts/"
echo "   git commit -m 'Update prompt templates'"
