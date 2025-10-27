# Audit Report Generator

## Overview

The **Audit Report Generator** is a Streamlit application that captures structured audit data through guided forms and generates professional UIF TERS audit reports using Word document templates (DocxTemplate). It provides section-by-section completion tracking, auto-lookup capabilities, and text helpers to streamline report creation.

## Purpose

Capture structured audit data and produce standardized, high-quality UIF TERS audit reports by guiding auditors through comprehensive forms and automatically populating Word document templates with collected information.

## Key Features

- **Guided Form Sections**: Multi-section forms covering company info, audit scope, findings, compliance, outcomes, and conclusions
- **Completion Tracking**: Real-time progress indicators showing section and overall completion percentage
- **Monthly Claims & Payments Capture**: Structured tables for capturing monthly TERS claims and payment data
- **Text Helpers**: Pre-defined templates and suggestions for findings, compliance statements, outcomes, and scope descriptions
- **Auto-Lookup Functionality**: Automatic address and province lookup from combined address book
- **Template-Based Generation**: Uses `templates/UIF_Template.docx` with DocxTemplate for professional formatting
- **Data Validation**: Built-in validation for required fields and data formats
- **Excel Integration**: Upload employer data files to pre-populate company information
- **Report Preview**: Review captured data before final generation
- **Export Capability**: Generate Word documents saved to `generated_reports/` directory

## Business Benefits

- **Consistent Quality**: Ensure all reports follow standardized structure and formatting
- **Time Savings**: Reduce report writing time from hours to minutes with guided forms and templates
- **Reduced Rework**: Minimize formatting errors and missing sections with completion tracking
- **Clear Progress Visibility**: Track completion status for each section and overall report
- **Audit Trail**: Maintain consistent documentation standards across all engagements
- **Professional Output**: Generate polished, client-ready reports automatically

## Tech Stack

- **Python**: 3.11+
- **Framework**: Streamlit
- **Data Processing**: Pandas, OpenPyXL
- **Document Generation**: DocxTemplate (python-docx-template)
- **Template Format**: Microsoft Word (.docx)

## Inputs

- **Excel DataFile**: Uploaded employer data file with company information
  - Required columns: UIF reference, company name, employee details, claims, payments
- **Combined Address Book** (Optional): `data/Combined_Address_Book.xlsx`
  - Used for automatic address and province lookup by UIF reference
- **Word Template**: `templates/UIF_Template.docx`
  - Pre-formatted Word document with placeholders for data population

## Outputs

- **Generated Reports**: Professional Word documents (.docx) in `generated_reports/` directory
  - Named by company and date (e.g., `ABC_Company_Audit_Report_2024-12-15.docx`)
- **Structured Data**: Captured audit information ready for template population

## How It Works

1. **Data Upload**: User uploads Excel DataFile via Streamlit interface
2. **Company Selection**: Application extracts company list from DataFile
3. **Section Navigation**: User navigates through guided form sections (Company Info, Scope, Findings, etc.)
4. **Data Capture**: User fills forms with audit details, using text helpers and pre-defined options
5. **Auto-Lookup**: System automatically looks up address and province from address book if available
6. **Monthly Data Entry**: User enters monthly claims and payments in structured tables
7. **Completion Tracking**: Progress bars update as sections are completed
8. **Data Validation**: Application validates required fields before allowing report generation
9. **Template Population**: Captured data is merged into Word template using DocxTemplate
10. **Report Generation**: Final report saved to `generated_reports/` directory and available for download

## Installation & Setup

### Prerequisites
- Python 3.11 or higher
- Microsoft Word (for viewing generated reports)
- Excel DataFile with employer information

### Installation Steps

1. **Navigate to Tool Directory**:
   ```bash
   cd audit_report_generator
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Prepare Template**:
   - Ensure `templates/` directory exists
   - Place `UIF_Template.docx` in `templates/` directory
   - Verify template has correct placeholders (e.g., `{{company_name}}`, `{{uif_reference}}`)

4. **Prepare Address Book** (Optional):
   - Create `data/` directory
   - Place `Combined_Address_Book.xlsx` in `data/` directory
   - Ensure columns include: UIF reference, address, province

5. **Run Application**:
   ```bash
   streamlit run app.py
   ```

## Configuration

### Word Template Structure (`templates/UIF_Template.docx`)
- **Placeholders**: Use Jinja2 syntax for data fields
  - Company info: `{{company_name}}`, `{{uif_reference}}`, `{{address}}`, `{{province}}`
  - Audit details: `{{audit_scope}}`, `{{audit_period}}`, `{{auditor_name}}`
  - Findings: `{{findings}}`, `{{compliance_status}}`, `{{recommendations}}`
  - Financial: `{{total_claims}}`, `{{total_payments}}`, `{{variance}}`
- **Formatting**: Pre-format headings, tables, and styles in template
- **Tables**: Use DocxTemplate table syntax for monthly claims/payments

### Address Book Structure (`data/Combined_Address_Book.xlsx`)
- **Required Columns**:
  - UIF reference (for matching)
  - Physical address
  - Province
- **Optional Columns**:
  - Postal address
  - City
  - Postal code

### Form Sections
1. **Company Information**: Name, UIF ref, address, contact details
2. **Audit Scope**: Objectives, period, methodology
3. **Findings**: Key observations, issues identified, evidence
4. **Compliance**: Regulatory compliance status, deviations
5. **Outcomes**: Conclusions, opinions, recommendations
6. **Monthly Data**: Claims and payments by month

## Directory Structure

```
audit_report_generator/
├── app.py                               # Main Streamlit application
├── requirements.txt                      # Python dependencies
├── README.md                            # This documentation
├── templates/                           # Word templates (gitignored)
│   └── UIF_Template.docx
├── data/                                # Input data (gitignored)
│   └── Combined_Address_Book.xlsx
├── generated_reports/                   # Output reports (gitignored)
├── utils/                               # Helper modules
│   ├── data_loader.py
│   ├── template_populator.py
│   └── validators.py
└── config/                              # Configuration files
    └── constants.py
```

## Usage Workflow

1. **Launch Application**: Run `streamlit run app.py`
2. **Upload DataFile**: Use file uploader to select employer Excel file
3. **Select Company**: Choose company from dropdown
4. **Complete Company Info**: Fill company details section (auto-lookup if address book available)
5. **Define Audit Scope**: Enter audit objectives, period, and methodology
6. **Document Findings**: Record key findings using text helpers
7. **Assess Compliance**: Document compliance status and deviations
8. **Enter Monthly Data**: Fill claims and payments tables
9. **Record Outcomes**: Document conclusions and recommendations
10. **Review Progress**: Check completion tracking to ensure all sections complete
11. **Generate Report**: Click "Generate Report" to create Word document
12. **Download Report**: Access generated report from `generated_reports/` or download link

## Troubleshooting

### Template Issues
- **Error**: "Template not found"
  - **Solution**: Verify `UIF_Template.docx` exists in `templates/` directory
- **Error**: "Invalid template format"
  - **Solution**: Ensure template is valid .docx file with correct placeholders
- **Error**: "Placeholder not found"
  - **Solution**: Check template placeholders match data field names

### Data Upload Issues
- **Error**: "Failed to read DataFile"
  - **Solution**: Ensure file is valid Excel format (.xlsx) and not corrupted
- **Error**: "No companies found"
  - **Solution**: Verify DataFile has company name or UIF reference column
- **Error**: "Address book not found"
  - **Solution**: Optional file; auto-lookup will be disabled if missing

### Generation Issues
- **Error**: "Report generation failed"
  - **Solution**: Check all required sections are completed
- **Error**: "File already exists"
  - **Solution**: Close existing report file or rename output
- **Error**: "Permission denied"
  - **Solution**: Ensure write permissions in `generated_reports/` directory

### Form Issues
- **Error**: "Validation failed"
  - **Solution**: Complete all required fields marked with asterisk (*)
- **Error**: "Invalid data format"
  - **Solution**: Check date formats, numeric fields, and text length limits

## Best Practices

- **Complete All Sections**: Ensure all form sections are filled before generating report
- **Use Text Helpers**: Leverage pre-defined templates for consistency
- **Review Before Generation**: Preview captured data before final report creation
- **Save Progress**: Streamlit maintains session state; complete report in one session
- **Template Maintenance**: Keep Word template updated with latest formatting standards
- **Address Book Updates**: Regularly update address book for accurate auto-lookup

## Version Information

- **Version**: 1.0
- **Last Updated**: December 2024
- **Maintained By**: UIF Audit Team
- **License**: Proprietary
