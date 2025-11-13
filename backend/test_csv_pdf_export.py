"""
Test suite for CSV and PDF export functionality.
Tests both CSV and PDF export with various configurations.
"""

import pytest
import os
import csv
from io import BytesIO, StringIO
from csv_pdf_exporter import (
    CSVExporter, PDFExporter,
    export_jobs_to_csv, export_jobs_to_pdf
)


# Sample test data
SAMPLE_JOBS = [
    {
        'title': 'Senior Python Developer',
        'company': 'Tech Corp',
        'location': 'San Francisco, CA',
        'salary': '$120k-$150k',
        'job_type': 'Remote',
        'description': 'Looking for an experienced Python developer with strong backend skills. Must have 5+ years of experience with Python, Django, and REST APIs.',
        'link': 'https://example.com/job1',
        'score': {
            'overall_score': 87.5,
            'highlight': 'green',
            'keyword_match_score': 85.0,
            'salary_match_score': 90.0,
            'location_match_score': 85.0
        }
    },
    {
        'title': 'Junior Developer',
        'company': 'Startup Inc',
        'location': 'New York, NY',
        'salary': '$60k-$80k',
        'job_type': 'Onsite',
        'description': 'Entry-level position for new graduates. Great learning opportunity.',
        'link': 'https://example.com/job2',
        'score': {
            'overall_score': 45.0,
            'highlight': 'yellow',
            'keyword_match_score': 40.0,
            'salary_match_score': 50.0,
            'location_match_score': 45.0
        }
    },
    {
        'title': 'Data Scientist',
        'company': 'Analytics Co',
        'location': 'Remote',
        'salary': '$100k-$130k',
        'job_type': 'Remote',
        'description': 'Data scientist position requiring Python, machine learning, and statistical analysis skills.',
        'link': 'https://example.com/job3',
        'score': {
            'overall_score': 72.0,
            'highlight': 'white',
            'keyword_match_score': 70.0,
            'salary_match_score': 75.0,
            'location_match_score': 71.0
        }
    }
]

SAMPLE_TIPS = {
    'summary': 'Your resume shows good technical skills but needs improvement in quantifying achievements and adding missing keywords.',
    'overall_assessment': {
        'strength_score': 72,
        'completeness': 'Good',
        'ats_compatibility': 'Fair'
    },
    'critical_tips': [
        {
            'category': 'keywords',
            'title': 'Add Missing Technical Keywords',
            'description': 'Your resume is missing important keywords like Python, AWS, Docker',
            'action': 'Add these keywords naturally in your experience section',
            'impact': 'high'
        },
        {
            'category': 'format',
            'title': 'Improve ATS Compatibility',
            'description': 'Use standard section headings and avoid complex formatting',
            'action': 'Reorganize resume with clear sections: Experience, Skills, Education',
            'impact': 'high'
        }
    ],
    'important_tips': [
        {
            'category': 'achievements',
            'title': 'Quantify Your Achievements',
            'description': 'Use numbers and metrics to show impact',
            'action': 'Add specific metrics to at least 3 bullet points',
            'impact': 'medium'
        }
    ],
    'optional_tips': [
        {
            'category': 'skills',
            'title': 'Add Soft Skills',
            'description': 'Include relevant soft skills like leadership, communication',
            'action': 'Add a brief summary section highlighting key soft skills',
            'impact': 'low'
        }
    ]
}


class TestCSVExporter:
    """Test cases for CSV export functionality."""
    
    def test_csv_exporter_initialization(self):
        """Test CSV exporter can be initialized."""
        exporter = CSVExporter()
        assert exporter is not None
    
    def test_export_jobs_basic(self):
        """Test basic CSV export with scores and descriptions."""
        exporter = CSVExporter()
        result = exporter.export_jobs(SAMPLE_JOBS)
        
        assert result is not None
        assert isinstance(result, BytesIO)
        
        # Verify content
        content = result.getvalue().decode('utf-8')
        assert 'Senior Python Developer' in content
        assert 'Tech Corp' in content
        assert 'Score (%)' in content
    
    def test_export_jobs_without_scores(self):
        """Test CSV export without score columns."""
        exporter = CSVExporter()
        result = exporter.export_jobs(SAMPLE_JOBS, include_scores=False)
        
        content = result.getvalue().decode('utf-8')
        assert 'Score (%)' not in content
        assert 'Match Quality' not in content
    
    def test_export_jobs_without_description(self):
        """Test CSV export without description column."""
        exporter = CSVExporter()
        result = exporter.export_jobs(SAMPLE_JOBS, include_description=False)
        
        content = result.getvalue().decode('utf-8')
        assert 'Description' not in content
        # Should still have other fields
        assert 'Job Title' in content
        assert 'Company' in content
    
    def test_export_jobs_minimal(self):
        """Test CSV export with minimal columns (no scores, no description)."""
        exporter = CSVExporter()
        result = exporter.export_jobs(
            SAMPLE_JOBS, 
            include_scores=False, 
            include_description=False
        )
        
        content = result.getvalue().decode('utf-8')
        lines = content.strip().split('\n')
        
        # Should have header + 3 data rows
        assert len(lines) == 4
        
        # Verify header
        assert 'Job Title,Company,Location,Salary,Job Type,Link' in lines[0]
    
    def test_export_empty_jobs_raises_error(self):
        """Test that exporting empty jobs list raises ValueError."""
        exporter = CSVExporter()
        
        with pytest.raises(ValueError, match="Cannot export empty jobs list"):
            exporter.export_jobs([])
    
    def test_csv_row_data_structure(self):
        """Test CSV row data structure is correct."""
        exporter = CSVExporter()
        result = exporter.export_jobs(SAMPLE_JOBS)
        
        # Parse CSV
        content = result.getvalue().decode('utf-8')
        csv_reader = csv.DictReader(StringIO(content))
        rows = list(csv_reader)
        
        # Check we have 3 rows
        assert len(rows) == 3
        
        # Check first row
        first_row = rows[0]
        assert first_row['Job Title'] == 'Senior Python Developer'
        assert first_row['Company'] == 'Tech Corp'
        assert float(first_row['Score (%)']) == 87.5
        assert first_row['Match Quality'] == 'GREEN'
    
    def test_export_jobs_to_file(self, tmp_path):
        """Test exporting CSV to file."""
        exporter = CSVExporter()
        filename = tmp_path / "test_jobs.csv"
        
        exporter.export_jobs_to_file(SAMPLE_JOBS, str(filename))
        
        # Verify file exists
        assert filename.exists()
        
        # Verify content
        with open(filename, 'r') as f:
            content = f.read()
            assert 'Senior Python Developer' in content
    
    def test_convenience_function(self):
        """Test the convenience function export_jobs_to_csv."""
        result = export_jobs_to_csv(SAMPLE_JOBS)
        
        assert result is not None
        assert isinstance(result, BytesIO)
        
        content = result.getvalue().decode('utf-8')
        assert 'Senior Python Developer' in content


class TestPDFExporter:
    """Test cases for PDF export functionality."""
    
    def test_pdf_exporter_initialization(self):
        """Test PDF exporter can be initialized."""
        exporter = PDFExporter()
        assert exporter is not None
        assert exporter.styles is not None
    
    def test_export_jobs_basic(self):
        """Test basic PDF export."""
        exporter = PDFExporter()
        result = exporter.export_jobs(SAMPLE_JOBS)
        
        assert result is not None
        assert isinstance(result, BytesIO)
        
        # Verify it's a PDF (starts with PDF header)
        content = result.getvalue()
        assert content.startswith(b'%PDF')
    
    def test_export_jobs_with_tips(self):
        """Test PDF export with resume tips."""
        exporter = PDFExporter()
        result = exporter.export_jobs(SAMPLE_JOBS, resume_tips=SAMPLE_TIPS)
        
        assert result is not None
        content = result.getvalue()
        assert content.startswith(b'%PDF')
        
        # PDF should be larger with tips
        result_without_tips = exporter.export_jobs(SAMPLE_JOBS, include_tips=False)
        assert len(content) > len(result_without_tips.getvalue())
    
    def test_export_jobs_without_tips(self):
        """Test PDF export without tips even when tips are provided."""
        exporter = PDFExporter()
        result = exporter.export_jobs(
            SAMPLE_JOBS, 
            resume_tips=SAMPLE_TIPS, 
            include_tips=False
        )
        
        assert result is not None
        assert isinstance(result, BytesIO)
    
    def test_export_empty_jobs_raises_error(self):
        """Test that exporting empty jobs list raises ValueError."""
        exporter = PDFExporter()
        
        with pytest.raises(ValueError, match="Cannot export empty jobs list"):
            exporter.export_jobs([])
    
    def test_export_jobs_to_file(self, tmp_path):
        """Test exporting PDF to file."""
        exporter = PDFExporter()
        filename = tmp_path / "test_jobs.pdf"
        
        exporter.export_jobs_to_file(SAMPLE_JOBS, str(filename))
        
        # Verify file exists
        assert filename.exists()
        
        # Verify it's a PDF
        with open(filename, 'rb') as f:
            content = f.read()
            assert content.startswith(b'%PDF')
    
    def test_convenience_function(self):
        """Test the convenience function export_jobs_to_pdf."""
        result = export_jobs_to_pdf(SAMPLE_JOBS)
        
        assert result is not None
        assert isinstance(result, BytesIO)
        
        content = result.getvalue()
        assert content.startswith(b'%PDF')
    
    def test_convenience_function_with_tips(self):
        """Test PDF convenience function with tips."""
        result = export_jobs_to_pdf(SAMPLE_JOBS, resume_tips=SAMPLE_TIPS)
        
        assert result is not None
        content = result.getvalue()
        assert content.startswith(b'%PDF')


class TestExportIntegration:
    """Integration tests for export functionality."""
    
    def test_export_all_formats(self, tmp_path):
        """Test exporting to all formats."""
        # CSV
        csv_exporter = CSVExporter()
        csv_file = tmp_path / "jobs.csv"
        csv_exporter.export_jobs_to_file(SAMPLE_JOBS, str(csv_file))
        assert csv_file.exists()
        
        # PDF
        pdf_exporter = PDFExporter()
        pdf_file = tmp_path / "jobs.pdf"
        pdf_exporter.export_jobs_to_file(SAMPLE_JOBS, str(pdf_file))
        assert pdf_file.exists()
    
    def test_export_with_different_highlights(self):
        """Test export handles all highlight colors."""
        jobs_with_colors = [
            {**SAMPLE_JOBS[0], 'score': {'overall_score': 90, 'highlight': 'green'}},
            {**SAMPLE_JOBS[1], 'score': {'overall_score': 75, 'highlight': 'white'}},
            {**SAMPLE_JOBS[2], 'score': {'overall_score': 50, 'highlight': 'yellow'}},
        ]
        
        # Test CSV
        csv_result = export_jobs_to_csv(jobs_with_colors)
        assert csv_result is not None
        
        # Test PDF
        pdf_result = export_jobs_to_pdf(jobs_with_colors)
        assert pdf_result is not None
    
    def test_export_large_dataset(self):
        """Test export with larger dataset."""
        # Create 50 jobs
        large_dataset = []
        for i in range(50):
            job = SAMPLE_JOBS[0].copy()
            job['title'] = f"Job {i}"
            job['score'] = {
                'overall_score': 50 + i,
                'highlight': 'yellow' if i % 2 == 0 else 'white'
            }
            large_dataset.append(job)
        
        # Test CSV export
        csv_result = export_jobs_to_csv(large_dataset)
        assert csv_result is not None
        
        # Verify all jobs are in CSV
        content = csv_result.getvalue().decode('utf-8')
        lines = content.strip().split('\n')
        assert len(lines) == 51  # Header + 50 jobs
        
        # Test PDF export
        pdf_result = export_jobs_to_pdf(large_dataset)
        assert pdf_result is not None
        assert pdf_result.getvalue().startswith(b'%PDF')


def test_csv_special_characters():
    """Test CSV export handles special characters properly."""
    jobs_with_special_chars = [
        {
            'title': 'Developer, Senior Level',
            'company': 'Tech "Corp" Inc.',
            'location': 'San Francisco, CA',
            'salary': '$120k-$150k',
            'job_type': 'Remote',
            'description': 'Looking for developer with skills in:\n- Python\n- JavaScript\n- SQL',
            'link': 'https://example.com/job1',
            'score': {'overall_score': 85, 'highlight': 'green'}
        }
    ]
    
    result = export_jobs_to_csv(jobs_with_special_chars)
    content = result.getvalue().decode('utf-8')
    
    # Should handle commas and quotes properly
    assert 'Developer, Senior Level' in content or '"Developer, Senior Level"' in content
    assert 'Tech' in content


def test_pdf_handles_missing_score_data():
    """Test PDF export handles jobs with missing score data gracefully."""
    jobs_missing_scores = [
        {
            'title': 'Test Job',
            'company': 'Test Company',
            'location': 'Test Location',
            'salary': 'N/A',
            'job_type': 'Remote',
            'description': 'Test description',
            'link': 'https://example.com/test',
            # Missing score data
        }
    ]
    
    result = export_jobs_to_pdf(jobs_missing_scores)
    assert result is not None
    assert result.getvalue().startswith(b'%PDF')


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
