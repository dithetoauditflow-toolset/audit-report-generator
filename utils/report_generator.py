from docxtpl import DocxTemplate
import os
from datetime import datetime
from html import escape

class ReportGenerator:
    def __init__(self, template_path):
        """Initialize with hardcoded template path."""
        if not os.path.exists(template_path):
            raise FileNotFoundError(f"Template not found at {template_path}")
        self.template = DocxTemplate(template_path)

    def _sanitize_for_xml(self, value):
        """Recursively escape XML-unsafe characters in strings within context.

        Handles nested dicts/lists used by the template context. Ensures None -> "".
        """
        if value is None:
            return ""
        if isinstance(value, str):
            # Escape &, <, >. Leave quotes as-is for readability in docs
            return escape(value, quote=False)
        if isinstance(value, list):
            return [self._sanitize_for_xml(item) for item in value]
        if isinstance(value, tuple):
            return tuple(self._sanitize_for_xml(item) for item in value)
        if isinstance(value, dict):
            return {key: self._sanitize_for_xml(val) for key, val in value.items()}
        # Numbers, booleans, etc. are safe
        return value

    def generate_report(self, context):
        """Generate report and return output path."""
        # Add date for report naming
        context["date"] = datetime.now().strftime("%Y-%m-%d")
        # Ensure monthly_amounts is in context for table rendering
        if "monthly_amounts" not in context:
            context["monthly_amounts"] = []
        # Filter out empty monthly amounts to avoid empty table rows
        context["monthly_amounts"] = [
            item for item in context["monthly_amounts"]
            if item["amount"] or item["payment"]
        ]
        # Sanitize context to prevent XML parsing errors from characters like & and <
        safe_context = self._sanitize_for_xml(context)
        # Render template
        self.template.render(safe_context)
        # Create output directory
        os.makedirs("generated_reports", exist_ok=True)
        # Generate unique output path
        employer_name = str(context.get("Name_of_Employer", "report")).replace(" ", "_")
        # Basic filesystem-safe name
        for ch in ['\\', '/', ':', '*', '?', '"', '<', '>', '|']:
            employer_name = employer_name.replace(ch, "")
        output_path = f"generated_reports/{employer_name}_{context['date']}.docx"
        self.template.save(output_path)
        return output_path