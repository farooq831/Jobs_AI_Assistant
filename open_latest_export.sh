#!/bin/bash
# Open the most recent job export file in LibreOffice

DOWNLOAD_DIR="$HOME/Downloads"

# Find the most recent job export Excel file
LATEST_XLSX=$(ls -t "$DOWNLOAD_DIR"/jobs_*.xlsx 2>/dev/null | head -1)

if [ -z "$LATEST_XLSX" ]; then
    echo "❌ No Excel export files found in $DOWNLOAD_DIR"
    echo "Please export jobs from the web app first."
    exit 1
fi

echo "📊 Opening latest export: $(basename "$LATEST_XLSX")"
libreoffice "$LATEST_XLSX" &

echo "✅ LibreOffice launched!"
