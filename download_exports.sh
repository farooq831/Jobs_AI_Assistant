#!/bin/bash
# Download exports properly without auto-extraction

USER_ID="user_001"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

echo "Downloading job exports..."

# Excel export
echo "📊 Downloading Excel file..."
curl -o ~/Downloads/jobs_${USER_ID}_${TIMESTAMP}.xlsx \
  http://localhost:5000/api/export/excel/stored-jobs/${USER_ID}

# PDF export
echo "📄 Downloading PDF file..."
curl -o ~/Downloads/jobs_${USER_ID}_${TIMESTAMP}.pdf \
  http://localhost:5000/api/export/pdf/stored-jobs/${USER_ID}

# CSV export
echo "📋 Downloading CSV file..."
curl -o ~/Downloads/jobs_${USER_ID}_${TIMESTAMP}.csv \
  http://localhost:5000/api/export/csv/stored-jobs/${USER_ID}

echo ""
echo "✅ Downloads complete!"
echo "Files saved to ~/Downloads/"
ls -lh ~/Downloads/jobs_${USER_ID}_${TIMESTAMP}.*

echo ""
echo "File types:"
file ~/Downloads/jobs_${USER_ID}_${TIMESTAMP}.*
