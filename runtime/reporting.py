"""
PEL Report Generation Module

Generates stakeholder-friendly reports from PEL simulation results in multiple formats:
- Markdown (.md)
- HTML (.html)
- PDF (.pdf)

This module enables non-technical audiences (CFOs, board members, investors) to 
understand model results without interpreting raw JSON.
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime


class ModelReport:
    """Generates reports from PEL simulation results."""
    
    def __init__(self, results: Dict[str, Any]):
        """
        Initialize report generator with simulation results.
        
        Args:
            results: PEL simulation results (from pel run output JSON)
        """
        self.results = results
        self.model_name = results.get("model", {}).get("name", "Unknown Model")
        self.status = results.get("status", "unknown")
        self.mode = results.get("mode", "unknown")
        self.seed = results.get("seed")
        self.runtime = results.get("runtime_ms", 0)
        
    def generate_markdown(self, output_path: Optional[Path] = None) -> str:
        """
        Generate Markdown report.
        
        Args:
            output_path: Optional path to write report file
            
        Returns:
            Markdown content as string
        """
        md = []
        
        # Header
        md.append(f"# PEL Model Report: {self.model_name}")
        md.append(f"\n**Generated:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}\n")
        
        # Executive Summary
        md.append("## Executive Summary\n")
        md.append(f"- **Status:** {self.status}")
        md.append(f"- **Mode:** {self.mode}")
        if self.seed is not None:
            md.append(f"- **Seed:** {self.seed}")
        md.append(f"- **Runtime:** {self.runtime:.2f}ms\n")
        
        # Key Metrics
        md.append("## Key Metrics\n")
        variables = self.results.get("variables", {})
        if variables:
            md.append("| Variable | Final Value |")
            md.append("|----------|-------------|")
            for var_name, values in variables.items():
                if isinstance(values, list) and values:
                    final_value = values[-1]
                    md.append(f"| {var_name} | {final_value} |")
                elif isinstance(values, (int, float)):
                    md.append(f"| {var_name} | {values} |")
        else:
            md.append("*No variables recorded*\n")
        
        # Constraints
        md.append("\n## Constraint Violations\n")
        violations = self.results.get("constraint_violations", [])
        if violations:
            for v in violations:
                md.append(f"- **{v.get('constraint')}** at timestep {v.get('timestep')}: {v.get('message')}")
        else:
            md.append("*No constraint violations* ✓\n")
        
        # Assumption Register
        md.append("\n## Assumption Register\n")
        assumptions = self.results.get("assumptions", [])
        if assumptions:
            md.append("| Parameter | Source | Method | Confidence |")
            md.append("|-----------|--------|--------|------------|")
            for a in assumptions:
                md.append(f"| {a['name']} | {a['source']} | {a['method']} | {a['confidence']} |")
        else:
            md.append("*No assumptions recorded*\n")
        
        md_content = "\n".join(md)
        
        if output_path:
            output_path.write_text(md_content)
            
        return md_content
    
    def generate_html(self, output_path: Optional[Path] = None, include_charts: bool = False) -> str:
        """
        Generate HTML report.
        
        Args:
            output_path: Optional path to write report file
            include_charts: Whether to embed charts (requires visualization module)
            
        Returns:
            HTML content as string
        """
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PEL Report: {self.model_name}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            line-height: 1.6;
            color: #333;
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #34495e;
            margin-top: 30px;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }}
        th {{
            background-color: #3498db;
            color: white;
        }}
        tr:nth-child(even) {{
            background-color: #f2f2f2;
        }}
        .summary {{
            background-color: #ecf0f1;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }}
        .status-success {{
            color: #27ae60;
            font-weight: bold;
        }}
        .status-failed {{
            color: #e74c3c;
            font-weight: bold;
        }}
    </style>
</head>
<body>
    <h1>PEL Model Report: {self.model_name}</h1>
    <p><strong>Generated:</strong> {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
    
    <h2>Executive Summary</h2>
    <div class="summary">
        <p><strong>Status:</strong> <span class="status-{self.status.lower()}">{self.status}</span></p>
        <p><strong>Mode:</strong> {self.mode}</p>
        {"<p><strong>Seed:</strong> " + str(self.seed) + "</p>" if self.seed else ""}
        <p><strong>Runtime:</strong> {self.runtime:.2f}ms</p>
    </div>
    
    <h2>Key Metrics</h2>
    <table>
        <tr><th>Variable</th><th>Final Value</th></tr>
"""
        
        variables = self.results.get("variables", {})
        for var_name, values in variables.items():
            if isinstance(values, list) and values:
                final_value = values[-1]
                html += f"        <tr><td>{var_name}</td><td>{final_value}</td></tr>\n"
            elif isinstance(values, (int, float)):
                html += f"        <tr><td>{var_name}</td><td>{values}</td></tr>\n"
        
        html += """    </table>
    
    <h2>Constraint Violations</h2>
"""
        
        violations = self.results.get("constraint_violations", [])
        if violations:
            html += "    <ul>\n"
            for v in violations:
                html += f"        <li><strong>{v.get('constraint')}</strong> at timestep {v.get('timestep')}: {v.get('message')}</li>\n"
            html += "    </ul>\n"
        else:
            html += "    <p><em>No constraint violations</em> ✓</p>\n"
        
        html += """</body>
</html>"""
        
        if output_path:
            output_path.write_text(html)
            
        return html


def generate_report(results_path: Path, format: str = "markdown", output_path: Optional[Path] = None) -> str:
    """
    Convenience function to generate a report from results file.
    
    Args:
        results_path: Path to PEL simulation results JSON
        format: Report format ('markdown', 'html', or 'pdf')
        output_path: Optional path to write report
        
    Returns:
        Report content as string
    """
    with open(results_path) as f:
        results = json.load(f)
    
    report = ModelReport(results)
    
    if format == "markdown" or format == "md":
        return report.generate_markdown(output_path)
    elif format == "html":
        return report.generate_html(output_path)
    elif format == "pdf":
        # PDF generation requires additional dependencies (weasyprint or reportlab)
        raise NotImplementedError("PDF generation coming soon - use HTML format for now")
    else:
        raise ValueError(f"Unknown format: {format}. Use 'markdown', 'html', or 'pdf'")


if __name__ == "__main__":
    # Simple CLI for testing
    import sys
    if len(sys.argv) < 2:
        print("Usage: python reporting.py <results.json> [format] [output_path]")
        sys.exit(1)
    
    results_path = Path(sys.argv[1])
    format = sys.argv[2] if len(sys.argv) > 2 else "markdown"
    output_path = Path(sys.argv[3]) if len(sys.argv) > 3 else None
    
    content = generate_report(results_path, format, output_path)
    
    if not output_path:
        print(content)
