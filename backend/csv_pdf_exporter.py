"""
CSV and PDF Export Module
Export job listings in CSV and PDF formats for user convenience.
"""

import logging
import csv
from typing import Dict, List, Optional
from datetime import datetime
from io import BytesIO, StringIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.platypus import Image as RLImage
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CSVExporter:
    """
    Export job listings to CSV format.
    """
    
    def __init__(self):
        """Initialize the CSV exporter."""
        logger.info("CSVExporter initialized")
    
    def export_jobs(self, jobs: List[Dict], 
                    include_scores: bool = True,
                    include_description: bool = True) -> BytesIO:
        """
        Export jobs list to CSV format.
        
        Args:
            jobs: List of job dictionaries
            include_scores: Whether to include score columns
            include_description: Whether to include full job description
            
        Returns:
            BytesIO object containing the CSV file
        """
        if not jobs:
            logger.warning("No jobs to export")
            raise ValueError("Cannot export empty jobs list")
        
        # Create string buffer
        output = StringIO()
        
        # Define headers based on options
        headers = ['Job Title', 'Company', 'Location', 'Salary', 'Job Type']
        
        if include_scores:
            headers.extend(['Score (%)', 'Match Quality', 'Keyword Match', 'Salary Match', 'Location Match'])
        
        if include_description:
            headers.append('Description')
        
        headers.append('Link')
        
        # Create CSV writer
        writer = csv.DictWriter(output, fieldnames=headers)
        writer.writeheader()
        
        # Write job data
        for job in jobs:
            row = self._prepare_job_row(job, include_scores, include_description)
            writer.writerow(row)
        
        # Convert to BytesIO
        bytes_output = BytesIO(output.getvalue().encode('utf-8'))
        bytes_output.seek(0)
        
        logger.info(f"Exported {len(jobs)} jobs to CSV")
        return bytes_output
    
    def _prepare_job_row(self, job: Dict, include_scores: bool, include_description: bool) -> Dict:
        """
        Prepare a job dictionary for CSV row.
        
        Args:
            job: Job dictionary
            include_scores: Whether to include scores
            include_description: Whether to include description
            
        Returns:
            Dictionary with CSV row data
        """
        row = {
            'Job Title': job.get('title', 'N/A'),
            'Company': job.get('company', 'N/A'),
            'Location': job.get('location', 'N/A'),
            'Salary': job.get('salary', 'N/A'),
            'Job Type': job.get('job_type', 'N/A'),
        }
        
        if include_scores:
            score_data = job.get('score', {})
            if isinstance(score_data, dict):
                overall_score = score_data.get('overall_score', 0)
                highlight = score_data.get('highlight', 'white')
                keyword_match = score_data.get('keyword_match_score', 0)
                salary_match = score_data.get('salary_match_score', 0)
                location_match = score_data.get('location_match_score', 0)
            else:
                overall_score = 0
                highlight = 'white'
                keyword_match = 0
                salary_match = 0
                location_match = 0
            
            row['Score (%)'] = f"{overall_score:.1f}"
            row['Match Quality'] = highlight.upper()
            row['Keyword Match'] = f"{keyword_match:.1f}"
            row['Salary Match'] = f"{salary_match:.1f}"
            row['Location Match'] = f"{location_match:.1f}"
        
        if include_description:
            description = job.get('description', 'N/A')
            # Clean description for CSV (remove newlines and tabs)
            description = description.replace('\n', ' ').replace('\t', ' ').strip()
            row['Description'] = description[:500] if len(description) > 500 else description
        
        row['Link'] = job.get('link', 'N/A')
        
        return row
    
    def export_jobs_to_file(self, jobs: List[Dict], 
                           filename: str,
                           include_scores: bool = True,
                           include_description: bool = True):
        """
        Export jobs to a CSV file on disk.
        
        Args:
            jobs: List of job dictionaries
            filename: Output filename
            include_scores: Whether to include scores
            include_description: Whether to include descriptions
        """
        output = self.export_jobs(jobs, include_scores, include_description)
        
        with open(filename, 'wb') as f:
            f.write(output.getvalue())
        
        logger.info(f"Exported jobs to file: {filename}")


class PDFExporter:
    """
    Export job listings to PDF format with formatting and color-coding.
    """
    
    # Color definitions (RGB tuples)
    COLORS = {
        'red': colors.Color(1, 0.8, 0.8),      # Poor match
        'yellow': colors.Color(1, 1, 0.6),     # Fair match
        'white': colors.Color(1, 1, 1),        # Good match
        'green': colors.Color(0.8, 1, 0.8),    # Excellent match
        'header': colors.Color(0.27, 0.45, 0.77),
        'text': colors.black
    }
    
    def __init__(self):
        """Initialize the PDF exporter."""
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
        logger.info("PDFExporter initialized")
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles."""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#4472C4'),
            spaceAfter=30,
            alignment=TA_CENTER
        ))
        
        # Subtitle style
        self.styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#70AD47'),
            spaceAfter=12,
            alignment=TA_LEFT
        ))
        
        # Job title style
        self.styles.add(ParagraphStyle(
            name='JobTitle',
            parent=self.styles['Heading3'],
            fontSize=14,
            textColor=colors.HexColor('#000000'),
            spaceAfter=6,
            spaceBefore=12,
            alignment=TA_LEFT,
            fontName='Helvetica-Bold'
        ))
        
        # Normal text style
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=6,
            alignment=TA_LEFT
        ))
    
    def export_jobs(self, jobs: List[Dict], 
                    resume_tips: Optional[Dict] = None,
                    filename: Optional[str] = None,
                    include_tips: bool = True) -> BytesIO:
        """
        Export jobs list to PDF format.
        
        Args:
            jobs: List of job dictionaries with scores and highlights
            resume_tips: Optional resume optimization tips
            filename: Optional custom filename (for metadata)
            include_tips: Whether to include resume tips section
            
        Returns:
            BytesIO object containing the PDF file
        """
        if not jobs:
            logger.warning("No jobs to export")
            raise ValueError("Cannot export empty jobs list")
        
        # Create buffer
        output = BytesIO()
        
        # Create PDF document
        doc = SimpleDocTemplate(
            output,
            pagesize=letter,
            rightMargin=0.5*inch,
            leftMargin=0.5*inch,
            topMargin=0.75*inch,
            bottomMargin=0.5*inch
        )
        
        # Build content
        story = []
        
        # Add title
        title = Paragraph("Job Search Results", self.styles['CustomTitle'])
        story.append(title)
        story.append(Spacer(1, 0.2*inch))
        
        # Add metadata
        metadata_text = f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br/>"
        metadata_text += f"Total Jobs: {len(jobs)}"
        metadata = Paragraph(metadata_text, self.styles['CustomBody'])
        story.append(metadata)
        story.append(Spacer(1, 0.3*inch))
        
        # Add summary statistics
        self._add_summary_statistics(story, jobs)
        story.append(Spacer(1, 0.3*inch))
        
        # Add resume tips if available
        if include_tips and resume_tips:
            self._add_resume_tips_section(story, resume_tips)
            story.append(PageBreak())
        
        # Add jobs listing
        self._add_jobs_section(story, jobs)
        
        # Build PDF
        doc.build(story)
        output.seek(0)
        
        logger.info(f"Exported {len(jobs)} jobs to PDF")
        return output
    
    def _add_summary_statistics(self, story: List, jobs: List[Dict]):
        """
        Add summary statistics section.
        
        Args:
            story: PDF story list
            jobs: List of job dictionaries
        """
        subtitle = Paragraph("Summary Statistics", self.styles['CustomSubtitle'])
        story.append(subtitle)
        story.append(Spacer(1, 0.1*inch))
        
        # Calculate statistics
        highlights = {'red': 0, 'yellow': 0, 'white': 0, 'green': 0}
        total_score = 0
        
        for job in jobs:
            score_data = job.get('score', {})
            if isinstance(score_data, dict):
                highlight = score_data.get('highlight', 'white').lower()
                highlights[highlight] = highlights.get(highlight, 0) + 1
                total_score += score_data.get('overall_score', 0)
        
        avg_score = total_score / len(jobs) if jobs else 0
        
        # Create statistics table
        stats_data = [
            ['Metric', 'Value'],
            ['Average Match Score', f"{avg_score:.1f}%"],
            ['Excellent Matches (Green)', str(highlights.get('green', 0))],
            ['Good Matches (White)', str(highlights.get('white', 0))],
            ['Fair Matches (Yellow)', str(highlights.get('yellow', 0))],
            ['Poor Matches (Red)', str(highlights.get('red', 0))]
        ]
        
        stats_table = Table(stats_data, colWidths=[3*inch, 2*inch])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.COLORS['header']),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
        ]))
        
        story.append(stats_table)
    
    def _add_resume_tips_section(self, story: List, tips: Dict):
        """
        Add resume optimization tips section.
        
        Args:
            story: PDF story list
            tips: Resume tips dictionary
        """
        subtitle = Paragraph("Resume Optimization Tips", self.styles['CustomSubtitle'])
        story.append(subtitle)
        story.append(Spacer(1, 0.1*inch))
        
        # Add summary
        summary_text = tips.get('summary', 'No summary available')
        summary = Paragraph(f"<b>Summary:</b> {summary_text}", self.styles['CustomBody'])
        story.append(summary)
        story.append(Spacer(1, 0.1*inch))
        
        # Add overall assessment
        assessment = tips.get('overall_assessment', {})
        assessment_text = f"<b>Strength Score:</b> {assessment.get('strength_score', 'N/A')}/100 | "
        assessment_text += f"<b>Completeness:</b> {assessment.get('completeness', 'N/A')} | "
        assessment_text += f"<b>ATS Compatibility:</b> {assessment.get('ats_compatibility', 'N/A')}"
        assessment_para = Paragraph(assessment_text, self.styles['CustomBody'])
        story.append(assessment_para)
        story.append(Spacer(1, 0.2*inch))
        
        # Add tips table
        tips_data = [['Priority', 'Category', 'Title', 'Action']]
        
        # Add critical tips
        for tip in tips.get('critical_tips', [])[:3]:  # Limit to top 3
            tips_data.append([
                '🔴 CRITICAL',
                tip.get('category', 'N/A').upper(),
                tip.get('title', 'N/A'),
                tip.get('action', 'N/A')
            ])
        
        # Add important tips
        for tip in tips.get('important_tips', [])[:3]:  # Limit to top 3
            tips_data.append([
                '🟡 IMPORTANT',
                tip.get('category', 'N/A').upper(),
                tip.get('title', 'N/A'),
                tip.get('action', 'N/A')
            ])
        
        if len(tips_data) > 1:
            tips_table = Table(tips_data, colWidths=[1*inch, 1.2*inch, 2*inch, 3*inch])
            tips_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), self.COLORS['header']),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
            ]))
            
            story.append(tips_table)
    
    def _add_jobs_section(self, story: List, jobs: List[Dict]):
        """
        Add jobs listing section.
        
        Args:
            story: PDF story list
            jobs: List of job dictionaries
        """
        subtitle = Paragraph("Job Listings", self.styles['CustomSubtitle'])
        story.append(subtitle)
        story.append(Spacer(1, 0.1*inch))
        
        # Add each job
        for i, job in enumerate(jobs, 1):
            self._add_job_entry(story, job, i)
            
            # Add page break every 3 jobs for better readability
            if i % 3 == 0 and i < len(jobs):
                story.append(PageBreak())
    
    def _add_job_entry(self, story: List, job: Dict, index: int):
        """
        Add a single job entry.
        
        Args:
            story: PDF story list
            job: Job dictionary
            index: Job index number
        """
        # Get job data
        title = job.get('title', 'N/A')
        company = job.get('company', 'N/A')
        location = job.get('location', 'N/A')
        salary = job.get('salary', 'N/A')
        job_type = job.get('job_type', 'N/A')
        
        # Get score data
        score_data = job.get('score', {})
        if isinstance(score_data, dict):
            overall_score = score_data.get('overall_score', 0)
            highlight = score_data.get('highlight', 'white').lower()
        else:
            overall_score = 0
            highlight = 'white'
        
        # Determine background color
        if overall_score >= 85:
            bg_color = self.COLORS['green']
        elif highlight in self.COLORS:
            bg_color = self.COLORS[highlight]
        else:
            bg_color = self.COLORS['white']
        
        # Job title with score
        title_text = f"{index}. {title} - Match Score: {overall_score:.1f}%"
        job_title = Paragraph(title_text, self.styles['JobTitle'])
        story.append(job_title)
        
        # Job details table
        details_data = [
            ['Company:', company],
            ['Location:', location],
            ['Salary:', salary],
            ['Job Type:', job_type],
            ['Match Quality:', highlight.upper()]
        ]
        
        details_table = Table(details_data, colWidths=[1.5*inch, 5*inch])
        details_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), bg_color),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('PADDING', (0, 0), (-1, -1), 6),
            ('VALIGN', (0, 0), (-1, -1), 'TOP')
        ]))
        
        story.append(details_table)
        
        # Job description (truncated)
        description = job.get('description', 'N/A')
        if len(description) > 300:
            description = description[:300] + '...'
        
        desc_para = Paragraph(f"<b>Description:</b> {description}", self.styles['CustomBody'])
        story.append(desc_para)
        
        # Job link
        link = job.get('link', 'N/A')
        link_para = Paragraph(f"<b>Link:</b> <link href='{link}'>{link[:60]}...</link>", self.styles['CustomBody'])
        story.append(link_para)
        
        story.append(Spacer(1, 0.2*inch))
    
    def export_jobs_to_file(self, jobs: List[Dict], 
                           filename: str,
                           resume_tips: Optional[Dict] = None,
                           include_tips: bool = True):
        """
        Export jobs to a PDF file on disk.
        
        Args:
            jobs: List of job dictionaries
            filename: Output filename
            resume_tips: Optional resume tips
            include_tips: Whether to include tips
        """
        output = self.export_jobs(jobs, resume_tips, filename, include_tips)
        
        with open(filename, 'wb') as f:
            f.write(output.getvalue())
        
        logger.info(f"Exported jobs to file: {filename}")


# Convenience functions
def export_jobs_to_csv(jobs: List[Dict], 
                       include_scores: bool = True,
                       include_description: bool = True) -> BytesIO:
    """
    Convenience function to export jobs to CSV.
    
    Args:
        jobs: List of job dictionaries
        include_scores: Whether to include score columns
        include_description: Whether to include descriptions
        
    Returns:
        BytesIO object containing the CSV file
    """
    exporter = CSVExporter()
    return exporter.export_jobs(jobs, include_scores, include_description)


def export_jobs_to_pdf(jobs: List[Dict],
                       resume_tips: Optional[Dict] = None,
                       include_tips: bool = True) -> BytesIO:
    """
    Convenience function to export jobs to PDF.
    
    Args:
        jobs: List of job dictionaries
        resume_tips: Optional resume tips
        include_tips: Whether to include tips section
        
    Returns:
        BytesIO object containing the PDF file
    """
    exporter = PDFExporter()
    return exporter.export_jobs(jobs, resume_tips, include_tips=include_tips)


if __name__ == '__main__':
    # Example usage
    sample_jobs = [
        {
            'title': 'Senior Python Developer',
            'company': 'Tech Corp',
            'location': 'San Francisco, CA',
            'salary': '$120k-$150k',
            'job_type': 'Remote',
            'description': 'Looking for an experienced Python developer with strong backend skills...',
            'link': 'https://example.com/job1',
            'score': {
                'overall_score': 87,
                'highlight': 'green',
                'keyword_match_score': 85,
                'salary_match_score': 90,
                'location_match_score': 85
            }
        },
        {
            'title': 'Junior Developer',
            'company': 'Startup Inc',
            'location': 'New York, NY',
            'salary': '$60k-$80k',
            'job_type': 'Onsite',
            'description': 'Entry-level position for new graduates...',
            'link': 'https://example.com/job2',
            'score': {
                'overall_score': 45,
                'highlight': 'yellow',
                'keyword_match_score': 40,
                'salary_match_score': 50,
                'location_match_score': 45
            }
        }
    ]
    
    sample_tips = {
        'summary': 'Your resume shows good technical skills but needs improvement in quantifying achievements.',
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
        'optional_tips': []
    }
    
    print("Exporting sample jobs to CSV...")
    csv_exporter = CSVExporter()
    csv_exporter.export_jobs_to_file(sample_jobs, 'sample_jobs.csv', include_scores=True, include_description=True)
    print("CSV export complete! Check sample_jobs.csv")
    
    print("\nExporting sample jobs to PDF...")
    pdf_exporter = PDFExporter()
    pdf_exporter.export_jobs_to_file(sample_jobs, 'sample_jobs.pdf', sample_tips, include_tips=True)
    print("PDF export complete! Check sample_jobs.pdf")
