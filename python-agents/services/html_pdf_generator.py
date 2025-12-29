"""
HTML to PDF Resume Generator
Uses xhtml2pdf for pure Python HTML to PDF conversion
Generates professional two-column resumes matching the design specification
"""
import os
from typing import Dict, Any
from datetime import datetime
from io import BytesIO
from jinja2 import Environment, BaseLoader
from xhtml2pdf import pisa


class HTMLPDFGenerator:
    """
    Generates professional PDF resumes using HTML templates and xhtml2pdf
    Layout: Header bar + Two columns (35% left / 65% right)
    """
    
    # HTML Template matching the provided design exactly
    RESUME_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{{ header.name }} - Resume</title>
    <style>
        @page {
            size: A4;
            margin: 0;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: Helvetica, Arial, sans-serif;
            font-size: 10pt;
            line-height: 1.4;
            color: #333333;
            background: white;
        }
        
        /* Header Bar - Teal Blue */
        .header {
            background-color: #2e6677;
            color: white;
            text-align: center;
            padding: 30px 20px;
            width: 100%;
        }
        
        .header h1 {
            font-size: 26pt;
            font-weight: normal;
            letter-spacing: 4px;
            margin-bottom: 8px;
            text-transform: uppercase;
            color: white;
        }
        
        .header h2 {
            font-size: 11pt;
            font-weight: normal;
            letter-spacing: 3px;
            text-transform: uppercase;
            color: #e0e0e0;
        }
        
        /* Main Container - Two Columns */
        .container {
            width: 100%;
        }
        
        .columns {
            width: 100%;
        }
        
        /* Left Column (35%) */
        .left-column {
            width: 35%;
            background-color: #f5f6f7;
            padding: 25px 20px;
            vertical-align: top;
        }
        
        /* Right Column (65%) */
        .right-column {
            width: 65%;
            padding: 25px 25px;
            background: white;
            vertical-align: top;
        }
        
        /* Section Headers */
        .section-title {
            font-size: 10pt;
            font-weight: bold;
            color: #2e6677;
            letter-spacing: 2px;
            text-transform: uppercase;
            margin-bottom: 12px;
            padding-bottom: 5px;
            border-bottom: 1.5px solid #2e6677;
        }
        
        .section {
            margin-bottom: 20px;
        }
        
        /* Contact Section */
        .contact-item {
            margin-bottom: 8px;
            font-size: 9pt;
        }
        
        .contact-label {
            color: #2e6677;
            font-weight: bold;
            display: inline-block;
            width: 55px;
        }
        
        .contact-value {
            color: #555555;
        }
        
        /* Summary */
        .summary-text {
            font-size: 9pt;
            color: #555555;
            font-style: italic;
            line-height: 1.5;
            text-align: justify;
        }
        
        /* Education */
        .education-item {
            margin-bottom: 15px;
        }
        
        .education-year {
            font-size: 9pt;
            color: #2e6677;
            font-style: italic;
            margin-bottom: 3px;
        }
        
        .education-degree {
            font-size: 10pt;
            font-weight: bold;
            color: #222222;
        }
        
        .education-honors {
            font-size: 9pt;
            color: #555555;
            font-style: italic;
        }
        
        .education-institution {
            font-size: 9pt;
            color: #666666;
        }
        
        /* Skills with Progress Bars */
        .skill-item {
            margin-bottom: 12px;
        }
        
        .skill-header {
            margin-bottom: 4px;
        }
        
        .skill-name {
            font-size: 9pt;
            color: #333333;
        }
        
        .skill-level {
            font-size: 9pt;
            color: #2e6677;
            font-weight: bold;
            float: right;
        }
        
        .skill-bar {
            background: #dddddd;
            height: 5px;
            width: 100%;
            clear: both;
        }
        
        .skill-fill {
            background: #2e6677;
            height: 5px;
        }
        
        /* Experience Section */
        .experience-item {
            margin-bottom: 18px;
        }
        
        .experience-duration {
            font-size: 9pt;
            color: #2e6677;
            font-weight: bold;
            margin-bottom: 2px;
        }
        
        .experience-role {
            font-size: 11pt;
            font-weight: bold;
            color: #222222;
            font-style: italic;
        }
        
        .experience-company {
            font-size: 9pt;
            color: #2e6677;
            margin-bottom: 6px;
        }
        
        .experience-points {
            margin-left: 15px;
            font-size: 9pt;
            color: #555555;
        }
        
        .experience-points li {
            margin-bottom: 4px;
            line-height: 1.4;
        }
        
        /* Projects Section */
        .project-item {
            margin-bottom: 15px;
        }
        
        .project-title {
            font-size: 10pt;
            font-weight: bold;
            color: #222222;
            margin-bottom: 3px;
        }
        
        .project-tech {
            font-size: 8pt;
            color: #2e6677;
            font-style: italic;
            margin-bottom: 5px;
        }
        
        .project-points {
            margin-left: 15px;
            font-size: 9pt;
            color: #555555;
        }
        
        .project-points li {
            margin-bottom: 3px;
            line-height: 1.4;
        }
    </style>
</head>
<body>
    <!-- Header -->
    <div class="header">
        <h1>{{ header.name | upper }}</h1>
        <h2>{{ header.title | upper }}</h2>
    </div>
    
    <!-- Main Content - Two Columns using Table -->
    <table class="columns" cellpadding="0" cellspacing="0">
        <tr>
            <!-- Left Column -->
            <td class="left-column">
                <!-- Contact -->
                <div class="section">
                    <div class="section-title">Contact</div>
                    {% if contact.phone %}
                    <div class="contact-item">
                        <span class="contact-label">phone</span>
                        <span class="contact-value">{{ contact.phone }}</span>
                    </div>
                    {% endif %}
                    {% if contact.email %}
                    <div class="contact-item">
                        <span class="contact-label">email</span>
                        <span class="contact-value">{{ contact.email }}</span>
                    </div>
                    {% endif %}
                    {% if contact.address %}
                    <div class="contact-item">
                        <span class="contact-label">address</span>
                        <span class="contact-value">{{ contact.address }}</span>
                    </div>
                    {% endif %}
                    {% if contact.website %}
                    <div class="contact-item">
                        <span class="contact-label">website</span>
                        <span class="contact-value">{{ contact.website }}</span>
                    </div>
                    {% endif %}
                    {% if contact.linkedin %}
                    <div class="contact-item">
                        <span class="contact-label">linkedin</span>
                        <span class="contact-value">{{ contact.linkedin }}</span>
                    </div>
                    {% endif %}
                </div>
                
                <!-- Summary -->
                {% if summary %}
                <div class="section">
                    <div class="section-title">Summary</div>
                    <p class="summary-text">{{ summary }}</p>
                </div>
                {% endif %}
                
                <!-- Education -->
                {% if education %}
                <div class="section">
                    <div class="section-title">Education</div>
                    {% for edu in education %}
                    <div class="education-item">
                        <div class="education-year">{{ edu.year }}</div>
                        <div class="education-degree">{{ edu.degree }}</div>
                        {% if edu.details %}
                        <div class="education-honors">{{ edu.details }}</div>
                        {% endif %}
                        <div class="education-institution">{{ edu.institution }}</div>
                    </div>
                    {% endfor %}
                </div>
                {% endif %}
                
                <!-- Skills -->
                {% if skills %}
                <div class="section">
                    <div class="section-title">Relevant Skills</div>
                    {% for skill in skills %}
                    <div class="skill-item">
                        <div class="skill-header">
                            <span class="skill-name">{{ skill.name }}</span>
                            <span class="skill-level">{{ skill.level }}%</span>
                        </div>
                        <div class="skill-bar">
                            <div class="skill-fill" style="width: {{ skill.level }}%;"></div>
                        </div>
                    </div>
                    {% endfor %}
                </div>
                {% endif %}
            </td>
            
            <!-- Right Column -->
            <td class="right-column">
                <!-- Professional Experience -->
                {% if experience %}
                <div class="section">
                    <div class="section-title">Professional Experience</div>
                    {% for exp in experience %}
                    <div class="experience-item">
                        <div class="experience-duration">{{ exp.duration }}</div>
                        <div class="experience-role">{{ exp.role }}</div>
                        <div class="experience-company">{{ exp.company }}{% if exp.location %}, {{ exp.location }}{% endif %}</div>
                        {% if exp.points %}
                        <ul class="experience-points">
                            {% for point in exp.points %}
                            <li>{{ point }}</li>
                            {% endfor %}
                        </ul>
                        {% endif %}
                    </div>
                    {% endfor %}
                </div>
                {% endif %}
                
                <!-- Projects -->
                {% if projects %}
                <div class="section">
                    <div class="section-title">Projects</div>
                    {% for project in projects %}
                    <div class="project-item">
                        <div class="project-title">{{ project.title }}</div>
                        {% if project.tech_stack %}
                        <div class="project-tech">{{ project.tech_stack | join(', ') }}</div>
                        {% endif %}
                        {% if project.points %}
                        <ul class="project-points">
                            {% for point in project.points %}
                            <li>{{ point }}</li>
                            {% endfor %}
                        </ul>
                        {% endif %}
                    </div>
                    {% endfor %}
                </div>
                {% endif %}
            </td>
        </tr>
    </table>
</body>
</html>
"""
    
    def __init__(self, output_dir: str = None):
        # Use absolute path relative to project root
        if output_dir is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            output_dir = os.path.join(base_dir, "resumes")
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Initialize Jinja2 environment
        self.jinja_env = Environment(loader=BaseLoader())
        self.template = self.jinja_env.from_string(self.RESUME_TEMPLATE)
    
    def generate_pdf(
        self,
        resume_data: Dict[str, Any],
        filename: str = None,
        user_id: int = None
    ) -> Dict[str, Any]:
        """
        Generate PDF from structured resume JSON using xhtml2pdf
        
        Args:
            resume_data: Structured resume JSON following the strict schema
            filename: Optional custom filename
            user_id: Optional user ID for file naming
        
        Returns:
            Dictionary with file path and status
        """
        try:
            # Generate filename if not provided
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                name_slug = resume_data.get('header', {}).get('name', 'resume').lower()
                name_slug = ''.join(c if c.isalnum() else '_' for c in name_slug)
                filename = f"{name_slug}_{timestamp}.pdf"
            
            # Ensure .pdf extension
            if not filename.endswith('.pdf'):
                filename += '.pdf'
            
            filepath = os.path.join(self.output_dir, filename)
            
            # Render HTML from template
            html_content = self.template.render(**resume_data)
            
            # Convert HTML to PDF using xhtml2pdf
            with open(filepath, "wb") as pdf_file:
                pisa_status = pisa.CreatePDF(
                    html_content,
                    dest=pdf_file,
                    encoding='utf-8'
                )
            
            if pisa_status.err:
                return {
                    "status": "error",
                    "message": f"PDF generation had errors: {pisa_status.err}",
                    "file_path": None
                }
            
            return {
                "status": "success",
                "file_path": filepath,
                "filename": filename,
                "message": "Resume PDF generated successfully"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to generate PDF: {str(e)}",
                "file_path": None
            }
    
    def generate_pdf_bytes(self, resume_data: Dict[str, Any]) -> bytes:
        """
        Generate PDF and return as bytes (for streaming download)
        
        Args:
            resume_data: Structured resume JSON
        
        Returns:
            PDF file as bytes
        """
        html_content = self.template.render(**resume_data)
        pdf_buffer = BytesIO()
        
        pisa.CreatePDF(html_content, dest=pdf_buffer, encoding='utf-8')
        
        pdf_buffer.seek(0)
        return pdf_buffer.getvalue()
    
    def validate_resume_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate resume data against the strict schema
        
        Args:
            data: Resume data to validate
        
        Returns:
            Validation result with any missing fields
        """
        required_structure = {
            "header": {"name": str, "title": str},
            "contact": {"phone": str, "email": str, "address": str, "website": str, "linkedin": str},
            "summary": str,
            "skills": list,
            "experience": list,
            "education": list
        }
        
        missing_fields = []
        
        # Check top-level fields
        for field, field_type in required_structure.items():
            if field not in data:
                missing_fields.append(field)
        
        return {
            "valid": len(missing_fields) == 0,
            "missing_fields": missing_fields,
            "message": "Valid resume data" if len(missing_fields) == 0 else f"Missing fields: {missing_fields}"
        }
    
    def generate_html_preview(self, resume_data: Dict[str, Any]) -> str:
        """
        Generate HTML preview of the resume
        
        Args:
            resume_data: Structured resume JSON
        
        Returns:
            HTML string for preview
        """
        return self.template.render(**resume_data)


# Create singleton instance
html_pdf_generator = HTMLPDFGenerator()
