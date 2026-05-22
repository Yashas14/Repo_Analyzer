"""
Documentation Service - Handles documentation generation and export
"""

import os
import json
from typing import Dict, List, Any
from datetime import datetime
from app.config import settings
from app.services.ai_service import AIService

# Try to import PDF generation libraries
try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

try:
    import markdown
    MARKDOWN_AVAILABLE = True
except ImportError:
    MARKDOWN_AVAILABLE = False


class DocumentationService:
    """Service for generating documentation"""
    
    def __init__(self):
        self.ai_service = AIService()
        self.reports_dir = settings.REPORTS_DIR
    
    async def generate_documentation(
        self,
        repository_id: str,
        analysis: Dict,
        include_code_snippets: bool = True,
        include_diagrams: bool = True,
        format: str = "pdf"
    ) -> str:
        """Generate documentation in the specified format"""
        
        # Generate markdown content first
        markdown_content = await self.generate_markdown(analysis, include_code_snippets)
        
        # Create output directory
        output_dir = os.path.join(self.reports_dir, repository_id)
        os.makedirs(output_dir, exist_ok=True)
        
        if format == "markdown":
            output_path = os.path.join(output_dir, "documentation.md")
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            return output_path
        
        elif format == "html":
            output_path = os.path.join(output_dir, "documentation.html")
            html_content = await self._markdown_to_html(markdown_content, analysis)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            return output_path
        
        elif format == "pdf":
            output_path = os.path.join(output_dir, "documentation.pdf")
            await self._generate_pdf(output_path, analysis, include_code_snippets)
            return output_path
        
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    async def get_documentation_path(self, repository_id: str, format: str) -> str:
        """Get the path to generated documentation"""
        extensions = {"pdf": ".pdf", "markdown": ".md", "html": ".html"}
        ext = extensions.get(format, ".pdf")
        return os.path.join(self.reports_dir, repository_id, f"documentation{ext}")
    
    async def generate_preview(self, analysis: Dict) -> str:
        """Generate HTML preview of documentation"""
        markdown_content = await self.generate_markdown(analysis, include_code_snippets=False)
        return await self._markdown_to_html(markdown_content, analysis)
    
    async def generate_markdown(self, analysis: Dict, include_code_snippets: bool = True) -> str:
        """Generate markdown documentation"""
        repo_name = analysis.get("repository_name", "Unknown Project")
        
        md = f"""# {repo_name} - Documentation

Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

---

## Table of Contents

1. [Overview](#overview)
2. [Technology Stack](#technology-stack)
3. [Architecture](#architecture)
4. [Modules](#modules)
5. [Functionalities](#functionalities)
6. [Dependencies](#dependencies)
7. [File Structure](#file-structure)

---

## Overview

{analysis.get('summary', 'No summary available.')}

### Project Statistics

| Metric | Value |
|--------|-------|
| Total Files | {analysis.get('structure', {}).get('total_files', 'N/A')} |
| Total Lines of Code | {analysis.get('structure', {}).get('total_lines', 'N/A')} |
| Number of Modules | {len(analysis.get('modules', []))} |
| Number of Dependencies | {len(analysis.get('dependencies', []))} |

---

## Technology Stack

"""
        
        tech_stack = analysis.get("tech_stack", [])
        if tech_stack:
            for tech in tech_stack:
                md += f"- {tech}\n"
        else:
            md += "No technology stack detected.\n"
        
        md += f"""
---

## Architecture

{analysis.get('architecture', 'Architecture analysis not available.')}

---

## Modules

"""
        
        modules = analysis.get("modules", [])
        if modules:
            for module in modules:
                md += f"""### {module.get('name', 'Unknown')}

**Path:** `{module.get('path', 'N/A')}`

**Files:** {module.get('file_count', 0)} files

"""
                files = module.get('files', [])[:5]
                if files:
                    md += "**Key Files:**\n"
                    for f in files:
                        md += f"- `{f}`\n"
                md += "\n"
        else:
            md += "No modules identified.\n"
        
        md += """
---

## Functionalities

"""
        
        functionalities = analysis.get("functionalities", [])
        if functionalities:
            for i, func in enumerate(functionalities, 1):
                md += f"""### {i}. {func.get('name', 'Unknown')}

**Description:** {func.get('description', 'N/A')}

**Core Logic:** {func.get('core_logic', 'N/A')}

"""
                files = func.get('files', [])[:3]
                if files:
                    md += "**Related Files:**\n"
                    for f in files:
                        md += f"- `{f}`\n"
                md += "\n"
        else:
            md += "No functionalities identified.\n"
        
        md += """
---

## Dependencies

"""
        
        dependencies = analysis.get("dependencies", [])
        if dependencies:
            md += "| Package | Version | Type |\n"
            md += "|---------|---------|------|\n"
            for dep in dependencies[:30]:
                md += f"| {dep.get('name', 'N/A')} | {dep.get('version', 'N/A')} | {dep.get('type', 'N/A')} |\n"
            
            if len(dependencies) > 30:
                md += f"\n*... and {len(dependencies) - 30} more dependencies*\n"
        else:
            md += "No dependencies detected.\n"
        
        md += """
---

## File Structure

### Languages Used

"""
        
        languages = analysis.get("structure", {}).get("languages", {})
        if languages:
            md += "| Language | Files |\n"
            md += "|----------|-------|\n"
            for lang, count in sorted(languages.items(), key=lambda x: x[1], reverse=True):
                md += f"| {lang} | {count} |\n"
        else:
            md += "No language statistics available.\n"
        
        md += f"""
---

## Appendix

### About This Documentation

This documentation was automatically generated by the AI-Powered Repository Understanding & Documentation Tool.

**Repository ID:** {analysis.get('repository_id', 'N/A')}

**Analysis Date:** {analysis.get('analysis_date', 'N/A')}

---

*Generated with ❤️ by Repository Analyzer*
"""
        
        return md
    
    async def _markdown_to_html(self, markdown_content: str, analysis: Dict) -> str:
        """Convert markdown to HTML"""
        repo_name = analysis.get("repository_name", "Documentation")
        
        if MARKDOWN_AVAILABLE:
            html_body = markdown.markdown(
                markdown_content, 
                extensions=['tables', 'fenced_code', 'toc']
            )
        else:
            # Basic conversion without markdown library
            html_body = f"<pre>{markdown_content}</pre>"
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{repo_name} - Documentation</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 900px;
            margin: 0 auto;
            padding: 40px 20px;
            background: #f9fafb;
        }}
        h1 {{
            color: #1a1a2e;
            border-bottom: 3px solid #4f46e5;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }}
        h2 {{
            color: #1a1a2e;
            margin-top: 40px;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 1px solid #e5e7eb;
        }}
        h3 {{
            color: #374151;
            margin-top: 25px;
            margin-bottom: 15px;
        }}
        p {{
            margin-bottom: 15px;
        }}
        code {{
            background: #f3f4f6;
            padding: 2px 6px;
            border-radius: 4px;
            font-family: 'Fira Code', 'Consolas', monospace;
            font-size: 0.9em;
        }}
        pre {{
            background: #1f2937;
            color: #f9fafb;
            padding: 20px;
            border-radius: 8px;
            overflow-x: auto;
            margin: 20px 0;
        }}
        pre code {{
            background: none;
            color: inherit;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        th, td {{
            padding: 12px 15px;
            text-align: left;
            border-bottom: 1px solid #e5e7eb;
        }}
        th {{
            background: #4f46e5;
            color: white;
            font-weight: 600;
        }}
        tr:hover {{
            background: #f9fafb;
        }}
        ul, ol {{
            margin: 15px 0;
            padding-left: 30px;
        }}
        li {{
            margin-bottom: 8px;
        }}
        hr {{
            border: none;
            border-top: 1px solid #e5e7eb;
            margin: 30px 0;
        }}
        blockquote {{
            border-left: 4px solid #4f46e5;
            padding-left: 20px;
            margin: 20px 0;
            color: #6b7280;
            font-style: italic;
        }}
        .toc {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        @media print {{
            body {{
                background: white;
                max-width: none;
            }}
            h2 {{
                page-break-before: always;
            }}
        }}
    </style>
</head>
<body>
    {html_body}
</body>
</html>"""
        
        return html
    
    async def _generate_pdf(self, output_path: str, analysis: Dict, include_code_snippets: bool):
        """Generate PDF documentation"""
        if not REPORTLAB_AVAILABLE:
            # Fallback: save as markdown
            markdown_content = await self.generate_markdown(analysis, include_code_snippets)
            md_path = output_path.replace('.pdf', '.md')
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            # Also create a simple text-based PDF alternative
            with open(output_path.replace('.pdf', '.txt'), 'w', encoding='utf-8') as f:
                f.write(f"PDF generation requires reportlab library.\n")
                f.write(f"Install with: pip install reportlab\n\n")
                f.write(f"Documentation saved as: {md_path}\n")
            return
        
        # Create PDF with ReportLab
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        styles = getSampleStyleSheet()
        
        # Custom styles
        styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            textColor=colors.HexColor('#1a1a2e')
        ))
        
        styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            spaceBefore=20,
            spaceAfter=10,
            textColor=colors.HexColor('#374151')
        ))
        
        styles.add(ParagraphStyle(
            name='CustomBody',
            parent=styles['Normal'],
            fontSize=11,
            spaceAfter=12,
            leading=14
        ))
        
        # Build content
        content = []
        repo_name = analysis.get("repository_name", "Unknown Project")
        
        # Title
        content.append(Paragraph(f"{repo_name}", styles['CustomTitle']))
        content.append(Paragraph("Project Documentation", styles['Heading2']))
        content.append(Spacer(1, 12))
        content.append(Paragraph(
            f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            styles['CustomBody']
        ))
        content.append(Spacer(1, 30))
        
        # Overview
        content.append(Paragraph("Overview", styles['CustomHeading']))
        summary = analysis.get('summary', 'No summary available.')
        # Truncate long summaries for PDF
        if len(summary) > 2000:
            summary = summary[:2000] + "..."
        content.append(Paragraph(summary.replace('\n', '<br/>'), styles['CustomBody']))
        content.append(Spacer(1, 20))
        
        # Statistics Table
        content.append(Paragraph("Project Statistics", styles['CustomHeading']))
        stats_data = [
            ['Metric', 'Value'],
            ['Total Files', str(analysis.get('structure', {}).get('total_files', 'N/A'))],
            ['Total Lines', str(analysis.get('structure', {}).get('total_lines', 'N/A'))],
            ['Modules', str(len(analysis.get('modules', [])))],
            ['Dependencies', str(len(analysis.get('dependencies', [])))]
        ]
        
        stats_table = Table(stats_data, colWidths=[200, 200])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4f46e5')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb'))
        ]))
        content.append(stats_table)
        content.append(Spacer(1, 20))
        
        # Technology Stack
        content.append(PageBreak())
        content.append(Paragraph("Technology Stack", styles['CustomHeading']))
        tech_stack = analysis.get("tech_stack", [])
        if tech_stack:
            for tech in tech_stack:
                content.append(Paragraph(f"• {tech}", styles['CustomBody']))
        else:
            content.append(Paragraph("No technology stack detected.", styles['CustomBody']))
        content.append(Spacer(1, 20))
        
        # Architecture
        content.append(Paragraph("Architecture", styles['CustomHeading']))
        arch = analysis.get('architecture', 'Architecture analysis not available.')
        if len(arch) > 3000:
            arch = arch[:3000] + "..."
        content.append(Paragraph(arch.replace('\n', '<br/>'), styles['CustomBody']))
        content.append(Spacer(1, 20))
        
        # Modules
        content.append(PageBreak())
        content.append(Paragraph("Modules", styles['CustomHeading']))
        modules = analysis.get("modules", [])
        if modules:
            for module in modules[:15]:  # Limit modules in PDF
                content.append(Paragraph(
                    f"<b>{module.get('name', 'Unknown')}</b>",
                    styles['CustomBody']
                ))
                content.append(Paragraph(
                    f"Path: {module.get('path', 'N/A')} | Files: {module.get('file_count', 0)}",
                    styles['CustomBody']
                ))
                content.append(Spacer(1, 10))
        else:
            content.append(Paragraph("No modules identified.", styles['CustomBody']))
        
        # Functionalities
        content.append(PageBreak())
        content.append(Paragraph("Functionalities", styles['CustomHeading']))
        functionalities = analysis.get("functionalities", [])
        if functionalities:
            for i, func in enumerate(functionalities[:10], 1):  # Limit in PDF
                content.append(Paragraph(
                    f"<b>{i}. {func.get('name', 'Unknown')}</b>",
                    styles['CustomBody']
                ))
                content.append(Paragraph(
                    func.get('description', 'N/A'),
                    styles['CustomBody']
                ))
                content.append(Spacer(1, 10))
        else:
            content.append(Paragraph("No functionalities identified.", styles['CustomBody']))
        
        # Dependencies
        content.append(PageBreak())
        content.append(Paragraph("Dependencies", styles['CustomHeading']))
        dependencies = analysis.get("dependencies", [])
        if dependencies:
            dep_data = [['Package', 'Version', 'Type']]
            for dep in dependencies[:25]:  # Limit in PDF
                dep_data.append([
                    dep.get('name', 'N/A')[:30],
                    dep.get('version', 'N/A')[:15],
                    dep.get('type', 'N/A')
                ])
            
            dep_table = Table(dep_data, colWidths=[200, 100, 100])
            dep_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4f46e5')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb'))
            ]))
            content.append(dep_table)
            
            if len(dependencies) > 25:
                content.append(Paragraph(
                    f"... and {len(dependencies) - 25} more dependencies",
                    styles['CustomBody']
                ))
        else:
            content.append(Paragraph("No dependencies detected.", styles['CustomBody']))
        
        # Footer
        content.append(Spacer(1, 40))
        content.append(Paragraph(
            "Generated by AI-Powered Repository Understanding & Documentation Tool",
            styles['CustomBody']
        ))
        
        # Build PDF
        doc.build(content)
