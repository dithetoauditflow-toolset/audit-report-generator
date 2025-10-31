import streamlit as st
from utils.report_generator import ReportGenerator
import os
import pandas as pd
from datetime import datetime, timedelta
import warnings
from config.copy_paste_text import (
    FINDINGS, COMPLIANCE, OVERALL_OUTCOMES, VERIFICATION_SCOPES, OBJECTIVES,
    MONTHLY_AMOUNTS, UI_TEXT,
    get_finding_text, get_compliance_text, get_overall_outcome_text,
    get_verification_scope_text, get_objective_text, get_monthly_amount_helper_text,
    substitute_template_variables
)

# Suppress deprecation warning originating from docxcompose/pkg_resources
# We don't use docxcompose directly; this avoids noisy logs in production.
warnings.filterwarnings(
    "ignore",
    message=r".*pkg_resources is deprecated as an API.*",
    category=UserWarning,
)
warnings.filterwarnings(
    "ignore",
    category=UserWarning,
    module=r"docxcompose\..*",
)

@st.cache_data(show_spinner=False)
def load_address_book():
    """Load the combined address book and return a lookup dictionary"""
    try:
        # Resolve path from ENV or common filename variants to survive case-sensitive prod
        env_path = os.environ.get("ADDRESS_BOOK_PATH")
        candidate_paths = []
        if env_path:
            candidate_paths.append(env_path)
        candidate_paths += [
            os.path.join("data", "combined_address_book.xlsx"),
            os.path.join("data", "Combined_Address_Book.xlsx"),
            os.path.join("data", "COMBINED_ADDRESS_BOOK.xlsx"),
        ]

        resolved_path = None
        for p in candidate_paths:
            if os.path.exists(p):
                resolved_path = p
                break

        if not resolved_path:
            st.sidebar.info("Address book not found. Continuing without address enrichment.")
            return {}

        df = pd.read_excel(resolved_path)

        # Normalize column names and support common aliases
        col_map = {str(c).strip().upper().replace(" ", "_"): c for c in df.columns}

        def pick(*aliases):
            for a in aliases:
                if a in col_map:
                    return col_map[a]
            return None

        uif_col = pick("UIFREFERENCENUMBER", "UIF_REFERENCE_NUMBER", "UIF_REF_NUMBER", "UIF_NUMBER", "UIFREF", "UIF_REF")
        addr_col = pick("ADDRESS", "ADDRESS_LINE", "ADDRESS1", "LOCATION", "ADDRESS_IN_FULL")
        prov_col = pick("PROVINCE", "PROV", "STATE")

        if not uif_col:
            st.sidebar.warning("Address book loaded but UIF reference column was not found. Skipping address enrichment.")
            return {}

        # Create lookup dictionary: UIF -> (ADDRESS, PROVINCE)
        address_lookup = {}
        for _, row in df.iterrows():
            uif_val = row[uif_col]
            if pd.isna(uif_val):
                continue
            key = str(uif_val).strip()
            # Tolerate Excel numeric-like strings such as '123.0'
            if key.endswith('.0'):
                try:
                    key = str(int(float(key)))
                except Exception:
                    pass

            addr_val = ""
            if addr_col and addr_col in df.columns and pd.notna(row.get(addr_col)):
                addr_val = str(row.get(addr_col)).strip()

            prov_val = ""
            if prov_col and prov_col in df.columns and pd.notna(row.get(prov_col)):
                prov_val = str(row.get(prov_col)).strip()

            if key:
                address_lookup[key] = (addr_val, prov_val)

        return address_lookup
    except Exception as e:
        st.sidebar.error(f"Error loading address book: {str(e)}")
        return {}

def get_address_from_uif(uif_ref_number, address_lookup):
    """Get address and province for a given UIF reference number"""
    if not uif_ref_number or not address_lookup:
        return "", ""

    uif_ref_clean = str(uif_ref_number).strip()
    if uif_ref_clean.endswith('.0'):
        try:
            uif_ref_clean = str(int(float(uif_ref_clean)))
        except Exception:
            pass
    return address_lookup.get(uif_ref_clean, ("", ""))

# Simple Streamlit app without custom CSS

# Initialize session state for button approach
if 'button_data' not in st.session_state:
    st.session_state.button_data = {
        "main_findings": "",
        "limitation_of_scope": "",
        "compliance_comments": "",
        "overall_outcomes": "",
        "payment_verification_scope": "",
        "employment_verification_scope": "",
        "claims_validity_scope": "",
        "objective_1_comment": "",
        "objective_2_comment": "",
        "objective_3_comment": "",
        "objective_4_comment": "",
        "objective_5_comment": ""
    }
    st.session_state.saved = {
        "main_findings": False,
        "limitation_of_scope": False,
        "compliance_comments": False,
        "overall_outcomes": False,
        "payment_verification_scope": False,
        "employment_verification_scope": False,
        "claims_validity_scope": False,
        "objective_1_comment": False,
        "objective_2_comment": False,
        "objective_3_comment": False,
        "objective_4_comment": False,
        "objective_5_comment": False
    }

# Initialize monthly payments saved status
if 'monthly_payments_saved' not in st.session_state:
    st.session_state.monthly_payments_saved = False

# Initialize other session state variables
if "form_data" not in st.session_state:
    st.session_state.form_data = {}
if 'widget_version' not in st.session_state:
    st.session_state.widget_version = 0
if "findings" not in st.session_state:
    st.session_state.findings = [
        {
            "description": "IRP5s, ID Copies and Employment contracts for the all the beneficiaries were not provided",
            "rating": "Critical",
            "page_ref": "TP.2"
        },
        {
            "description": "The employer did not provide all the required bank statements detailing the funds they received from UIF.",
            "rating": "Critical", 
            "page_ref": "TP.3"
        },
        {
            "description": "No payroll data or EMP501/201 documents were provided to confirm the employer's monthly UIF contributions/declarations.",
            "rating": "Critical",
            "page_ref": "TP.4"
        }
    ]
if "output_path" not in st.session_state:
    st.session_state.output_path = None
if "disabled_fields" not in st.session_state:
    st.session_state.disabled_fields = set()
if "validation_errors" not in st.session_state:
    st.session_state.validation_errors = []
if "file_processed" not in st.session_state:
    st.session_state.file_processed = False
if "current_file_name" not in st.session_state:
    st.session_state.current_file_name = None

# Comprehensive field initialization (from original app.py)
def initialize_session_state():
    """Initialize session state with nested structure for better organization"""
    if 'form_data' not in st.session_state:
        st.session_state.form_data = {
            'personal_info': {},
            'monthly_data': {},
            'findings': [],
            'completion_status': {}
        }
    
    # Initialize legacy structure for backward compatibility
    if 'form_data' not in st.session_state or not isinstance(st.session_state.form_data, dict):
        st.session_state.form_data = {}
    
    # Ensure nested structure exists even if form_data already exists
    if 'completion_status' not in st.session_state.form_data:
        st.session_state.form_data['completion_status'] = {}
    if 'personal_info' not in st.session_state.form_data:
        st.session_state.form_data['personal_info'] = {}
    if 'monthly_data' not in st.session_state.form_data:
        st.session_state.form_data['monthly_data'] = {}
    if 'findings' not in st.session_state.form_data:
        st.session_state.form_data['findings'] = []
    
    # Initialize new fields with default values
    if "Main_Findings" not in st.session_state.form_data:
        st.session_state.form_data["Main_Findings"] = ""
    if "Limitation_of_scope" not in st.session_state.form_data:
        st.session_state.form_data["Limitation_of_scope"] = ""
    if "Payment_Verification_Scope" not in st.session_state.form_data:
        st.session_state.form_data["Payment_Verification_Scope"] = ""
    if "Employment_Verification_Scope" not in st.session_state.form_data:
        st.session_state.form_data["Employment_Verification_Scope"] = ""
    if "Claims_Validity_Scope" not in st.session_state.form_data:
        st.session_state.form_data["Claims_Validity_Scope"] = ""
    if "Compliance_Comments" not in st.session_state.form_data:
        st.session_state.form_data["Compliance_Comments"] = ""
    if "Objective_1_Comment" not in st.session_state.form_data:
        st.session_state.form_data["Objective_1_Comment"] = ""
    if "Objective_2_Comment" not in st.session_state.form_data:
        st.session_state.form_data["Objective_2_Comment"] = ""
    if "Objective_3_Comment" not in st.session_state.form_data:
        st.session_state.form_data["Objective_3_Comment"] = ""
    if "Objective_4_Comment" not in st.session_state.form_data:
        st.session_state.form_data["Objective_4_Comment"] = ""
    if "Objective_5_Comment" not in st.session_state.form_data:
        st.session_state.form_data["Objective_5_Comment"] = ""
    if "Overall_Outcomes" not in st.session_state.form_data:
        st.session_state.form_data["Overall_Outcomes"] = ""
    if "Compliance" not in st.session_state.form_data:
        st.session_state.form_data["Compliance"] = "No"
    if "Compliance_with_UI_Act_Provide_comments" not in st.session_state.form_data:
        st.session_state.form_data["Compliance_with_UI_Act_Provide_comments"] = ""
    if "Compliance_Documents_List" not in st.session_state.form_data:
        st.session_state.form_data["Compliance_Documents_List"] = "N/A"
    if "Possible_Fraud_Fraud_Indicators_YesNo1" not in st.session_state.form_data:
        st.session_state.form_data["Possible_Fraud_Fraud_Indicators_YesNo1"] = "No"
    if "Overpayments_Identified_YesNo1" not in st.session_state.form_data:
        st.session_state.form_data["Overpayments_Identified_YesNo1"] = "No"
    if "Finding_1" not in st.session_state.form_data:
        st.session_state.form_data["Finding_1"] = ""
    if "Finding_1_Rating" not in st.session_state.form_data:
        st.session_state.form_data["Finding_1_Rating"] = ""
    if "Finding_1_Page" not in st.session_state.form_data:
        st.session_state.form_data["Finding_1_Page"] = ""
    
    # Initialize monthly claims fields
    monthly_claim_fields = [
        "April_2020_Indicate_NA_where_no_claim_", "May_2020", "June_2020", "July_2020", 
        "Aug_2020", "Sep_2020", "Oct_2020", "Nov_2020", "Dec_2020",
        "Jan_2021", "Feb_2021", "Mar_2021", "Apr_2021", "May_2021", "Jun_2021", "July_2021"
    ]
    
    for field in monthly_claim_fields:
        if field not in st.session_state.form_data:
            st.session_state.form_data[field] = "N/A"
    
    # Initialize monthly payment fields
    monthly_payment_fields = [
        "May_20201", "June_20201", "July_20201", "Aug_20201", "Sep_20201", "Oct_20201", 
        "Nov_20201", "Dec_20201", "Jan_20211", "Feb_20211", "Mar_20211", "Apr_20211", 
        "May_20211", "Jun_20211", "July_20211", "April_2020_Indicate_NA_where_no_paymen"
    ]
    
    for field in monthly_payment_fields:
        if field not in st.session_state.form_data:
            st.session_state.form_data[field] = "N/A"
    
    # Initialize other required fields
    required_fields = [
        "Name_of_Employer", "UIF_REG_Number", "Location_Type_address_in_full", 
        "Period_Claimed_For_Lockdown_Period", "Industry", "Number_of_Employees", 
        "Province", "Total_Amount_Verified", "Amount_Verified_as_Accurate", 
        "Affected_Employees", "Amount_not_Disbursed", "Verified_Percentage"
    ]
    
    for field in required_fields:
        if field not in st.session_state.form_data:
            st.session_state.form_data[field] = ""

# Initialize session state
initialize_session_state()

st.title("UIF TERS Report Generator - Button Approach")

# Debug section removed for cleaner interface

# Calculate completion status
# Enhanced completion status tracking
def get_section_completion(section_name, required_fields, optional_fields=None):
    """Calculate completion for a specific section with better accuracy"""
    filled_count = 0
    total_count = len(required_fields)
    
    # Count filled required fields
    for field in required_fields:
        field_value = st.session_state.form_data.get(field, "")
        if field_value and str(field_value).strip() and field_value != "N/A":
            filled_count += 1
    
    # Add optional fields if specified
    if optional_fields:
        total_count += len(optional_fields)
        for field in optional_fields:
            field_value = st.session_state.form_data.get(field, "")
            if field_value and str(field_value).strip() and field_value != "N/A":
                filled_count += 1
    
    percentage = (filled_count / total_count * 100) if total_count > 0 else 0
    return {
        'filled': filled_count,
        'total': total_count,
        'percentage': round(percentage, 1)
    }

def get_button_data_completion():
    """Calculate completion for button-based sections"""
    filled_count = 0
    total_count = len(st.session_state.button_data)
    
    for key, value in st.session_state.button_data.items():
        if value and str(value).strip():
            filled_count += 1
    
    percentage = (filled_count / total_count * 100) if total_count > 0 else 0
    return {
        'filled': filled_count,
        'total': total_count,
        'percentage': round(percentage, 1)
    }

def get_monthly_data_completion():
    """Calculate completion percentage for monthly data section"""
    if 'monthly_data' not in st.session_state.form_data:
        return {'filled': 0, 'total': 0, 'percentage': 0}
    
    monthly_data = st.session_state.form_data['monthly_data']
    filled_months = 0
    total_months = 0
    
    # Count months with both claim and payment data
    for month_key in monthly_data.keys():
        if month_key.endswith('_claim') or month_key.endswith('_payment'):
            month_base = month_key.replace('_claim', '').replace('_payment', '')
            if month_base not in [key.replace('_claim', '').replace('_payment', '') for key in monthly_data.keys() if key != month_key]:
                continue
            
            claim_key = f"{month_base}_claim"
            payment_key = f"{month_base}_payment"
            
            if claim_key in monthly_data and payment_key in monthly_data:
                total_months += 1
                if monthly_data[claim_key] and monthly_data[payment_key]:
                    filled_months += 1
    
    percentage = (filled_months / total_months * 100) if total_months > 0 else 0
    return {'filled': filled_months, 'total': total_months, 'percentage': percentage}

def count_filled_fields(section_data):
    """Count filled fields in a section"""
    if isinstance(section_data, dict):
        return sum(1 for value in section_data.values() if value and str(value).strip())
    return 0

def count_total_fields(section):
    """Count total fields in a section"""
    section_field_counts = {
        'personal_info': 8,  # Name, UIF, Location, Period, Industry, Employees, Province, etc.
        'monthly_data': 32,  # 16 months * 2 fields each (claim + payment)
        'findings': 5  # Main findings, limitations, compliance, objectives, outcomes
    }
    return section_field_counts.get(section, 0)

def update_completion_status():
    """Calculate completion percentage for each section with enhanced accuracy"""
    if 'completion_status' not in st.session_state.form_data:
        st.session_state.form_data['completion_status'] = {}
    
    # Company Details - core required fields
    company_fields = [
        "Name_of_Employer", "UIF_REG_Number", "Location_Type_address_in_full", 
        "Period_Claimed_For_Lockdown_Period", "Industry", "Number_of_Employees", "Province"
    ]
    
    # Financials - core required fields
    financial_fields = [
        "Total_Amount_Verified", "Amount_Verified_as_Accurate", "Affected_Employees"
    ]
    
    # Update completion status with enhanced calculations
    st.session_state.form_data['completion_status'] = {
        'company_details': get_section_completion('company_details', company_fields),
        'financials': get_section_completion('financials', financial_fields),
        'monthly_data': get_monthly_data_completion(),
        'findings': get_button_data_completion()
    }

# Update completion status
update_completion_status()

# Check for template
template_path = "templates/UIF_Template.docx"
if os.path.exists(template_path):
    st.sidebar.success("Template found: UIF_Template.docx")
else:
    st.sidebar.error("Template not found at templates/UIF_Template.docx. Please ensure it exists.")
    st.stop()

# Sidebar: Progress tracking
st.sidebar.header("📊 Form Completion Progress")

# Update completion status before displaying
update_completion_status()

# Get current progress data
completion_status = st.session_state.form_data.get('completion_status', {})

# Overall progress
total_sections = 4
completed_sections = sum(1 for section in completion_status.values() if section.get('percentage', 0) >= 100)
overall_percentage = (completed_sections / total_sections) * 100

# Display overall progress
st.sidebar.markdown("### 🎯 Overall Progress")
st.sidebar.progress(overall_percentage / 100)
st.sidebar.metric(
    label="Complete Sections", 
    value=f"{completed_sections}/{total_sections}",
    delta=f"{overall_percentage:.1f}% Complete"
)

st.sidebar.markdown("---")

# Display section progress with better formatting
st.sidebar.markdown("### 📋 Section Details")

# Company Details
company_progress = completion_status.get('company_details', {})
st.sidebar.markdown(f"**🏢 Company Details**")
st.sidebar.progress(company_progress.get('percentage', 0) / 100)
st.sidebar.caption(f"{company_progress.get('filled', 0)}/{company_progress.get('total', 0)} fields completed")

# Financials
financials_progress = completion_status.get('financials', {})
st.sidebar.markdown(f"**💰 Financials**")
st.sidebar.progress(financials_progress.get('percentage', 0) / 100)
st.sidebar.caption(f"{financials_progress.get('filled', 0)}/{financials_progress.get('total', 0)} fields completed")

# Monthly Data
monthly_progress = completion_status.get('monthly_data', {})
st.sidebar.markdown(f"**📅 Monthly Data**")
st.sidebar.progress(monthly_progress.get('percentage', 0) / 100)
st.sidebar.caption(f"{monthly_progress.get('filled', 0)}/{monthly_progress.get('total', 0)} months completed")

# Findings & Compliance
findings_progress = completion_status.get('findings', {})
st.sidebar.markdown(f"**🔍 Findings & Compliance**")
st.sidebar.progress(findings_progress.get('percentage', 0) / 100)
st.sidebar.caption(f"{findings_progress.get('filled', 0)}/{findings_progress.get('total', 0)} sections completed")

# Status indicators
st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Status Summary")

if overall_percentage == 100:
    st.sidebar.success("🎉 **Form Complete!** Ready to generate report.")
elif overall_percentage >= 75:
    st.sidebar.info("📝 **Almost Complete!** Just a few more fields needed.")
elif overall_percentage >= 50:
    st.sidebar.warning("⚠️ **Halfway There!** Keep going!")
else:
    st.sidebar.info("🚀 **Getting Started!** Begin with company details.")

# Sidebar: DataFile Upload
st.sidebar.header("Upload DataFile")
if "file_uploader_key" not in st.session_state:
    st.session_state.file_uploader_key = 0

uploaded_file = st.sidebar.file_uploader("Upload Excel DataFile", type=["xlsx"], key=f"file_uploader_{st.session_state.file_uploader_key}")

# Handle file upload/removal (comprehensive processing from original app.py)
if uploaded_file is not None:
    if st.session_state.current_file_name != uploaded_file.name:
        st.session_state.current_file_name = uploaded_file.name
        st.session_state.file_processed = False
    
    if not st.session_state.file_processed:
        try:
            df = pd.read_excel(uploaded_file)

            # Normalize headers and support common aliases
            df_cols = {str(c).strip().upper().replace(' ', '_'): c for c in df.columns}
            def pick_df(*aliases):
                for a in aliases:
                    if a in df_cols:
                        return df_cols[a]
                return None

            name_col = pick_df('TRADENAME', 'TRADE_NAME', 'EMPLOYER_NAME', 'NAME_OF_EMPLOYER', 'NAME', 'COMPANY', 'TRADING_NAME')
            uif_col = pick_df('UIFREFERENCENUMBER', 'UIF_REFERENCE_NUMBER', 'UIF_REF_NUMBER', 'UIF_NUMBER', 'UIFREF', 'UIF_REF', 'UIF_REG_NUMBER')
            industry_col = pick_df('INDUSTRYSECTOR', 'INDUSTRY_SECTOR', 'INDUSTRY', 'SECTOR')

            # Aggregate from DataFile using resolved columns
            name_of_employer = ''
            if name_col and name_col in df.columns and not df[name_col].dropna().empty:
                name_of_employer = str(df[name_col].dropna().iloc[0])
            st.sidebar.write(f"Info: Employer column detected = {name_col or 'None'}, value = '{name_of_employer}'")

            uif_reg_number = ''
            if uif_col and uif_col in df.columns and not df[uif_col].dropna().empty:
                uif_reg_number = str(df[uif_col].dropna().iloc[0]).strip()
                if uif_reg_number.endswith('.0'):
                    try:
                        uif_reg_number = str(int(float(uif_reg_number)))
                    except Exception:
                        pass
            st.sidebar.write(f"Info: UIF column detected = {uif_col or 'None'}, value = '{uif_reg_number}'")

            industry = ''
            if industry_col and industry_col in df.columns and not df[industry_col].dropna().empty:
                industry = str(df[industry_col].dropna().iloc[0])
            st.sidebar.write(f"Info: Industry column detected = {industry_col or 'None'}, value = '{industry}'")
            
            # Load address book and lookup address/province for this UIF reference number
            address_lookup = load_address_book()
            auto_address, auto_province = get_address_from_uif(uif_reg_number, address_lookup)
            
            # Show address lookup results in sidebar
            if auto_address or auto_province:
                st.sidebar.success(f"📍 Address found for UIF {uif_reg_number}")
                if auto_address:
                    st.sidebar.write(f"**Address:** {auto_address}")
                if auto_province:
                    st.sidebar.write(f"**Province:** {auto_province}")
            else:
                st.sidebar.info(f"ℹ️ No address found for UIF {uif_reg_number} in address book")
            
            # Count unique employees by ID number (assuming there's an ID column)
            id_column = None
            for col in df.columns:
                if 'ID' in col.upper() or 'EMPLOYEE' in col.upper():
                    id_column = col
                    break
            
            if id_column:
                number_of_employees = df[id_column].nunique()
            else:
                # Fallback to row count if no ID column found
                number_of_employees = len(df)
            
            affected_employees = number_of_employees  # Assume all affected
            
            # Convert dates (handle both serial numbers and pandas Timestamps)
            def serial_to_date(serial):
                if pd.isna(serial):
                    return None
                if isinstance(serial, (pd.Timestamp, datetime)):
                    return serial
                try:
                    # Try to convert to numeric for Excel serial dates
                    base = datetime(1899, 12, 30)
                    return base + timedelta(days=int(float(serial)))
                except (ValueError, TypeError):
                    # If conversion fails, try to parse as date string
                    try:
                        return pd.to_datetime(serial)
                    except:
                        return None
            
            # Get all shutdown periods and format them properly
            if 'SHUTDOWN_FROM' in df and 'SHUTDOWN_TILL' in df:
                # Get unique shutdown periods
                shutdown_periods = []
                st.sidebar.write(f"Debug: Processing {len(df)} rows for periods")
                
                for _, row in df.iterrows():
                    if pd.notna(row['SHUTDOWN_FROM']) and pd.notna(row['SHUTDOWN_TILL']):
                        from_date = serial_to_date(row['SHUTDOWN_FROM'])
                        till_date = serial_to_date(row['SHUTDOWN_TILL'])
                        if from_date and till_date:
                            # Format as "27 March 2020 to 30 April 2020"
                            from_formatted = from_date.strftime('%d %B %Y').lstrip('0') if from_date.day != 0 else from_date.strftime('%B %Y')
                            till_formatted = till_date.strftime('%d %B %Y').lstrip('0') if till_date.day != 0 else till_date.strftime('%B %Y')
                            period = f"{from_formatted} to {till_formatted}"
                            if period not in shutdown_periods:
                                shutdown_periods.append(period)
                                st.sidebar.write(f"Debug: Added period: {period}")
                
                st.sidebar.write(f"Debug: Total unique periods found: {len(shutdown_periods)}")
                if shutdown_periods:
                    period_claimed = ", ".join(shutdown_periods)
                else:
                    period_claimed = ""
            else:
                period_claimed = ""
            
            # Financial totals - Calculate total amount verified from bank pay amounts with specific criteria
            # Ensure expected numeric columns exist and are numeric
            for col in ['PAYMENT_ITR_1', 'PAYMENT_ITR_2', 'PAYMENT_ITR_3', 'BANK_PAY_AMOUNT']:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
                else:
                    df[col] = 0
            
            # Calculate total amount verified based on payment status and medium
            # Assuming columns exist for payment status and medium - adjust column names as needed
            payment_status_col = None
            payment_medium_col = None
            
            # Look for payment status and medium columns
            for col in df.columns:
                if 'STATUS' in col.upper() and 'PAYMENT' in col.upper():
                    payment_status_col = col
                elif 'MEDIUM' in col.upper() and 'PAYMENT' in col.upper():
                    payment_medium_col = col
            
            # Calculate total amount verified based on criteria
            try:
                if payment_status_col and payment_medium_col:
                    # Filter for payment status = 3 and payment medium = 1 or 2
                    mask = (df[payment_status_col] == 3) & (df[payment_medium_col].isin([1, 2]))
                    total_amount_verified = df.loc[mask, 'BANK_PAY_AMOUNT'].sum()
                else:
                    # Fallback: sum all bank pay amounts
                    total_amount_verified = df['BANK_PAY_AMOUNT'].sum()
            except Exception:
                total_amount_verified = 0
            
            # Round to 2 decimal places and format with R prefix
            total_amount_verified = round(total_amount_verified, 2)
            st.sidebar.write(f"Info: Total Amount Verified computed = R {total_amount_verified:.2f}")
            
            # Amount verified as accurate will be left blank for user input
            amount_verified_accurate = 0
            amount_not_disbursed = total_amount_verified - amount_verified_accurate
            verified_percentage = 0  # Will be calculated when user inputs amount verified as accurate
            
            # Monthly claims - determine based on shutdown dates
            monthly_claims = {
                "April_2020": "N/A",
                "May_2020": "N/A", 
                "June_2020": "N/A",
                "July_2020": "N/A",
                "Aug_2020": "N/A",
                "Sep_2020": "N/A",
                "Oct_2020": "N/A",
                "Nov_2020": "N/A",
                "Dec_2020": "N/A",
                "Jan_2021": "N/A",
                "Feb_2021": "N/A",
                "Mar_2021": "N/A",
                "Apr_2021": "N/A",
                "May_2021": "N/A",
                "Jun_2021": "N/A",
                "July_2021": "N/A"
            }
            
            # Calculate monthly claims based on shutdown dates
            if 'SHUTDOWN_TILL' in df:
                # First, let's debug what we're seeing
                st.sidebar.write(f"Debug: Found {len(df)} rows in datafile")
                st.sidebar.write(f"Debug: SHUTDOWN_TILL column values: {df['SHUTDOWN_TILL'].dropna().unique()}")
                
                # Group by SHUTDOWN_TILL to get unique periods and their amounts
                shutdown_groups = df.groupby('SHUTDOWN_TILL')['BANK_PAY_AMOUNT'].sum()
                st.sidebar.write(f"Debug: Found {len(shutdown_groups)} unique shutdown periods")
                
                for shutdown_till, total_amount in shutdown_groups.items():
                    if pd.notna(shutdown_till):
                        shutdown_date = serial_to_date(shutdown_till)
                        if shutdown_date:
                            # Determine which month this represents (shutdown till date indicates the month they claimed)
                            month_key = shutdown_date.strftime('%B_%Y')
                            st.sidebar.write(f"Debug: Processing shutdown date {shutdown_date} -> month_key: '{month_key}'")
                            
                            # Map full month names to abbreviated keys in monthly_claims
                            month_mapping = {
                                'January_2020': 'Jan_2020', 'February_2020': 'Feb_2020', 'March_2020': 'Mar_2020',
                                'April_2020': 'April_2020', 'May_2020': 'May_2020', 'June_2020': 'June_2020',
                                'July_2020': 'July_2020', 'August_2020': 'Aug_2020', 'September_2020': 'Sep_2020',
                                'October_2020': 'Oct_2020', 'November_2020': 'Nov_2020', 'December_2020': 'Dec_2020',
                                'January_2021': 'Jan_2021', 'February_2021': 'Feb_2021', 'March_2021': 'Mar_2021',
                                'April_2021': 'Apr_2021', 'May_2021': 'May_2021', 'June_2021': 'Jun_2021',
                                'July_2021': 'July_2021'
                            }
                            
                            # Try to find the correct key
                            if month_key in monthly_claims:
                                monthly_claims[month_key] = f"R {round(total_amount, 2)}"
                                st.sidebar.write(f"Debug: {month_key} -> R {round(total_amount, 2)}")
                            elif month_key in month_mapping:
                                mapped_key = month_mapping[month_key]
                                if mapped_key in monthly_claims:
                                    monthly_claims[mapped_key] = f"R {round(total_amount, 2)}"
                                    st.sidebar.write(f"Debug: Mapped {month_key} -> {mapped_key} -> R {round(total_amount, 2)}")
                                else:
                                    st.sidebar.write(f"Debug: Mapped key '{mapped_key}' not found in monthly_claims")
                            else:
                                st.sidebar.write(f"Debug: Month key '{month_key}' not found in monthly_claims or mapping")
                                st.sidebar.write(f"Debug: Available keys: {list(monthly_claims.keys())}")

                # Compute Iterations (employees paid per period) and Gaps flag
                try:
                    # Collect unique shutdown months as datetime (normalized to month)
                    unique_shutdowns = [serial_to_date(val) for val in df['SHUTDOWN_TILL'].dropna().unique()]
                    unique_shutdowns = [d for d in unique_shutdowns if d is not None]
                    unique_month_keys = sorted({datetime(d.year, d.month, 1) for d in unique_shutdowns})

                    # Helper: month difference
                    def months_diff(a, b):
                        return (b.year - a.year) * 12 + (b.month - a.month)

                    # Determine gaps: any non-consecutive month differences > 1
                    gaps_flag = "No"
                    for i in range(1, len(unique_month_keys)):
                        if months_diff(unique_month_keys[i-1], unique_month_keys[i]) > 1:
                            gaps_flag = "Yes"
                            break

                    # Determine employee identifier column
                    emp_col = None
                    for col in df.columns:
                        if 'ID' in col.upper() or 'EMPLOYEE' in col.upper():
                            emp_col = col
                            break

                    iteration_counts = []
                    if len(unique_month_keys) > 0:
                        for month_dt in unique_month_keys:
                            # Filter rows matching this month
                            mask = df['SHUTDOWN_TILL'].apply(lambda x: serial_to_date(x))
                            mask = mask.apply(lambda d: (d is not None) and (d.year == month_dt.year and d.month == month_dt.month))
                            period_df = df[mask]
                            # Only count paid entries (BANK_PAY_AMOUNT > 0) if available
                            if 'BANK_PAY_AMOUNT' in period_df.columns:
                                period_df = period_df[pd.to_numeric(period_df['BANK_PAY_AMOUNT'], errors='coerce').fillna(0) > 0]
                            # Count unique employees if column exists, else count rows
                            if emp_col and emp_col in period_df.columns:
                                count_val = period_df[emp_col].nunique()
                            else:
                                count_val = len(period_df)
                            iteration_counts.append(int(count_val))
                    # Persist to session
                    st.session_state['iteration_counts'] = iteration_counts
                    st.session_state['gaps_flag'] = gaps_flag
                    st.sidebar.write(f"Debug: Iteration counts = {iteration_counts}, Gaps = {gaps_flag}")
                except Exception as e:
                    st.sidebar.write(f"Debug: Failed to compute iterations/gaps: {e}")
            
            # Monthly payments - determine which months are editable based on claims
            monthly_payments = {
                "April_2020": {"value": "", "editable": monthly_claims["April_2020"] != "N/A"},
                "May_2020": {"value": "", "editable": monthly_claims["May_2020"] != "N/A"},
                "June_2020": {"value": "", "editable": monthly_claims["June_2020"] != "N/A"},
                "July_2020": {"value": "", "editable": monthly_claims["July_2020"] != "N/A"},
                "Aug_2020": {"value": "", "editable": monthly_claims["Aug_2020"] != "N/A"},
                "Sep_2020": {"value": "", "editable": monthly_claims["Sep_2020"] != "N/A"},
                "Oct_2020": {"value": "", "editable": monthly_claims["Oct_2020"] != "N/A"},
                "Nov_2020": {"value": "", "editable": monthly_claims["Nov_2020"] != "N/A"},
                "Dec_2020": {"value": "", "editable": monthly_claims["Dec_2020"] != "N/A"},
                "Jan_2021": {"value": "", "editable": monthly_claims["Jan_2021"] != "N/A"},
                "Feb_2021": {"value": "", "editable": monthly_claims["Feb_2021"] != "N/A"},
                "Mar_2021": {"value": "", "editable": monthly_claims["Mar_2021"] != "N/A"},
                "Apr_2021": {"value": "", "editable": monthly_claims["Apr_2021"] != "N/A"},
                "May_2021": {"value": "", "editable": monthly_claims["May_2021"] != "N/A"},
                "Jun_2021": {"value": "", "editable": monthly_claims["Jun_2021"] != "N/A"},
                "July_2021": {"value": "", "editable": monthly_claims["July_2021"] != "N/A"}
            }
            
            # Set default values for non-editable months
            for month, data in monthly_payments.items():
                if not data["editable"]:
                    data["value"] = "N/A"
            
            # Store monthly claims in form_data for progress tracking
            for month, claim_amount in monthly_claims.items():
                # Map month names to form field keys
                month_to_field_mapping = {
                    "April_2020": "April_2020_Indicate_NA_where_no_claim_",
                    "May_2020": "May_2020",
                    "June_2020": "June_2020", 
                    "July_2020": "July_2020",
                    "Aug_2020": "Aug_2020",
                    "Sep_2020": "Sep_2020",
                    "Oct_2020": "Oct_2020",
                    "Nov_2020": "Nov_2020",
                    "Dec_2020": "Dec_2020",
                    "Jan_2021": "Jan_2021",
                    "Feb_2021": "Feb_2021",
                    "Mar_2021": "Mar_2021",
                    "Apr_2021": "Apr_2021",
                    "May_2021": "May_2021",
                    "Jun_2021": "Jun_2021",
                    "July_2021": "July_2021"
                }
                
                if month in month_to_field_mapping:
                    field_key = month_to_field_mapping[month]
                    st.session_state.form_data[field_key] = claim_amount
            
            # Store monthly payments in form_data for progress tracking
            for month, payment_data in monthly_payments.items():
                # Map month names to payment field keys
                month_to_payment_field_mapping = {
                    "April_2020": "April_2020_Indicate_NA_where_no_paymen",
                    "May_2020": "May_20201",
                    "June_2020": "June_20201",
                    "July_2020": "July_20201",
                    "Aug_2020": "Aug_20201",
                    "Sep_2020": "Sep_20201",
                    "Oct_2020": "Oct_20201",
                    "Nov_2020": "Nov_20201",
                    "Dec_2020": "Dec_20201",
                    "Jan_2021": "Jan_20211",
                    "Feb_2021": "Feb_20211",
                    "Mar_2021": "Mar_20211",
                    "Apr_2021": "Apr_20211",
                    "May_2021": "May_20211",
                    "Jun_2021": "Jun_20211",
                    "July_2021": "July_20211"
                }
                
                if month in month_to_payment_field_mapping:
                    field_key = month_to_payment_field_mapping[month]
                    # Set payment value - if editable, use claim amount as default, otherwise use N/A
                    if payment_data["editable"]:
                        claim_amount = monthly_claims[month]
                        if claim_amount != "N/A":
                            # Extract amount from claim (remove "R " prefix)
                            claim_amount_clean = claim_amount.replace("R ", "").replace(",", "")
                            st.session_state.form_data[field_key] = f"R {claim_amount_clean}"
                        else:
                            st.session_state.form_data[field_key] = ""
                    else:
                        st.session_state.form_data[field_key] = "N/A"

            # Populate form_data with comprehensive data
            st.session_state.form_data.update({
                "Name_of_Employer": name_of_employer,
                "UIF_REG_Number": uif_reg_number,
                "Industry": industry,
                "Number_of_Employees": str(number_of_employees),
                "Period_Claimed_For_Lockdown_Period": period_claimed,
                "Location_Type_address_in_full": auto_address,  # Auto-populated from address book
                "Province": auto_province,  # Auto-populated from address book
                "Total_Amount_Verified": f"R {total_amount_verified:.2f}",
                "Amount_Verified_as_Accurate": "",  # Leave blank for user input
                "Amount_not_Disbursed": f"R {amount_not_disbursed:.2f}",
                "Verified_Percentage": "0.00%",  # Will be calculated when user inputs amount verified as accurate
                "Affected_Employees": "",  # Leave blank for user input
                
                # Amount Claimed fields (from monthly_claims)
                "April_2020_Indicate_NA_where_no_claim_": monthly_claims["April_2020"],
                "May_2020": monthly_claims["May_2020"],
                "June_2020": monthly_claims["June_2020"],
                "July_2020": monthly_claims["July_2020"],
                "Aug_2020": monthly_claims["Aug_2020"],
                "Sep_2020": monthly_claims["Sep_2020"],
                "Oct_2020": monthly_claims["Oct_2020"],
                "Nov_2020": monthly_claims["Nov_2020"],
                "Dec_2020": monthly_claims["Dec_2020"],
                "Jan_2021": monthly_claims["Jan_2021"],
                "Feb_2021": monthly_claims["Feb_2021"],
                "Mar_2021": monthly_claims["Mar_2021"],
                "Apr_2021": monthly_claims["Apr_2021"],
                "May_2021": monthly_claims["May_2021"],
                "Jun_2021": monthly_claims["Jun_2021"],
                "July_2021": monthly_claims["July_2021"],
                
                # Amount paid to beneficiaries fields (from monthly_payments)
                "April_2020_Indicate_NA_where_no_paymen": monthly_payments["April_2020"]["value"],
                "May_20201": monthly_payments["May_2020"]["value"],
                "June_20201": monthly_payments["June_2020"]["value"],
                "July_20201": monthly_payments["July_2020"]["value"],
                "Aug_20201": monthly_payments["Aug_2020"]["value"],
                "Sep_20201": monthly_payments["Sep_2020"]["value"],
                "Oct_20201": monthly_payments["Oct_2020"]["value"],
                "Nov_20201": monthly_payments["Nov_2020"]["value"],
                "Dec_20201": monthly_payments["Dec_2020"]["value"],
                "Jan_20211": monthly_payments["Jan_2021"]["value"],
                "Feb_20211": monthly_payments["Feb_2021"]["value"],
                "Mar_20211": monthly_payments["Mar_2021"]["value"],
                "Apr_20211": monthly_payments["Apr_2021"]["value"],
                "May_20211": monthly_payments["May_2021"]["value"],
                "Jun_20211": monthly_payments["Jun_2021"]["value"],
                "July_20211": monthly_payments["July_2021"]["value"]
            })
            
            st.session_state.file_processed = True
            # Bump widget version to force widget keys to refresh and take new defaults
            st.session_state.widget_version += 1
            st.rerun()
            st.session_state.monthly_payments_saved = False  # Reset monthly payments saved status
            # Update progress tracking after file upload
            update_completion_status()
            st.sidebar.success("DataFile uploaded and all fields populated successfully!")
            
        except Exception as e:
            st.sidebar.error(f"Error processing file: {str(e)}")
            st.session_state.file_processed = False

# Clear form button
if st.sidebar.button("Clear Form"):
    st.session_state.button_data = {
        "main_findings": "",
        "limitation_of_scope": "",
        "compliance_comments": "",
        "overall_outcomes": "",
        "payment_verification_scope": "",
        "employment_verification_scope": "",
        "claims_validity_scope": "",
        "objective_1_comment": "",
        "objective_2_comment": "",
        "objective_3_comment": "",
        "objective_4_comment": "",
        "objective_5_comment": ""
    }
    st.session_state.saved = {
        "main_findings": False,
        "limitation_of_scope": False,
        "compliance_comments": False,
        "overall_outcomes": False,
        "payment_verification_scope": False,
        "employment_verification_scope": False,
        "claims_validity_scope": False,
        "objective_1_comment": False,
        "objective_2_comment": False,
        "objective_3_comment": False,
        "objective_4_comment": False,
        "objective_5_comment": False
    }
    st.session_state.form_data = {}
    st.session_state.findings = [
        {
            "description": "IRP5s, ID Copies and Employment contracts for the all the beneficiaries were not provided",
            "rating": "Critical",
            "page_ref": "TP.2"
        },
        {
            "description": "The employer did not provide all the required bank statements detailing the funds they received from UIF.",
            "rating": "Critical", 
            "page_ref": "TP.3"
        },
        {
            "description": "No payroll data or EMP501/201 documents were provided to confirm the employer's monthly UIF contributions/declarations.",
            "rating": "Critical",
            "page_ref": "TP.4"
        }
    ]
    st.session_state.output_path = None
    st.session_state.validation_errors = []
    st.session_state.file_processed = False
    st.session_state.current_file_name = None
    st.session_state.file_uploader_key += 1
    # Update progress tracking after clearing form
    update_completion_status()
    st.rerun()

# Functions to append text to each form's input
def add_main_findings_positive():
    """Add positive finding (underpayments) - replaces existing content with single finding"""
    st.session_state.button_data["main_findings"] = get_finding_text("main_findings", "finding_1", st.session_state.form_data)
    # Sync widget state so text_area reflects programmatic change
    st.session_state["main_findings_input"] = st.session_state.button_data["main_findings"]
    st.rerun()

def add_main_findings_negative():
    """Add negative finding (ineligible employees) - replaces existing content with single finding"""
    st.session_state.button_data["main_findings"] = get_finding_text("main_findings", "finding_2", st.session_state.form_data)
    st.session_state["main_findings_input"] = st.session_state.button_data["main_findings"]
    st.rerun()

def add_limitation_1():
    st.session_state.button_data["limitation_of_scope"] += get_finding_text("limitations", "limitation_1") + "\n"
    st.session_state["limitation_input"] = st.session_state.button_data["limitation_of_scope"]
    st.rerun()

def add_limitation_2():
    st.session_state.button_data["limitation_of_scope"] += get_finding_text("limitations", "limitation_2") + "\n"
    st.session_state["limitation_input"] = st.session_state.button_data["limitation_of_scope"]
    st.rerun()

def add_limitation_3():
    st.session_state.button_data["limitation_of_scope"] += get_finding_text("limitations", "limitation_3") + "\n"
    st.session_state["limitation_input"] = st.session_state.button_data["limitation_of_scope"]
    st.rerun()

def add_limitation_4():
    st.session_state.button_data["limitation_of_scope"] += get_finding_text("limitations", "limitation_4") + "\n"
    st.session_state["limitation_input"] = st.session_state.button_data["limitation_of_scope"]
    st.rerun()

def add_compliance_yes():
    st.session_state.button_data["compliance_comments"] += get_compliance_text("ui_act_compliance", "yes") + "\n"
    # Update progress tracking
    update_completion_status()
    st.session_state["compliance_input"] = st.session_state.button_data["compliance_comments"]
    st.rerun()

def add_compliance_no():
    st.session_state.button_data["compliance_comments"] += get_compliance_text("ui_act_compliance", "no") + "\n"
    # Update progress tracking
    update_completion_status()
    st.session_state["compliance_input"] = st.session_state.button_data["compliance_comments"]
    st.rerun()

def add_overall_outcomes_positive():
    st.session_state.button_data["overall_outcomes"] += get_overall_outcome_text("positive", "payment_accuracy", st.session_state.form_data) + "\n"
    st.session_state.button_data["overall_outcomes"] += get_overall_outcome_text("positive", "employment_verification", st.session_state.form_data) + "\n"
    st.session_state.button_data["overall_outcomes"] += get_overall_outcome_text("positive", "documentation", st.session_state.form_data) + "\n"
    # Update progress tracking
    update_completion_status()
    st.session_state["overall_outcomes_input"] = st.session_state.button_data["overall_outcomes"]
    st.rerun()

def add_overall_outcomes_negative():
    st.session_state.button_data["overall_outcomes"] += get_overall_outcome_text("negative", "payment_accuracy", st.session_state.form_data) + "\n"
    st.session_state.button_data["overall_outcomes"] += get_overall_outcome_text("negative", "employment_verification", st.session_state.form_data) + "\n"
    st.session_state.button_data["overall_outcomes"] += get_overall_outcome_text("negative", "documentation", st.session_state.form_data) + "\n"
    # Update progress tracking
    update_completion_status()
    st.session_state["overall_outcomes_input"] = st.session_state.button_data["overall_outcomes"]
    st.rerun()

def refresh_overall_outcomes():
    """Refresh the overall outcomes text with current form data for template variable substitution"""
    current_text = st.session_state.button_data.get("overall_outcomes", "")
    if current_text:
        # Apply template substitution to existing text
        refreshed_text = substitute_template_variables(current_text, st.session_state.form_data)
        st.session_state.button_data["overall_outcomes"] = refreshed_text

def refresh_main_findings():
    """Refresh the main findings text with current form data for template variable substitution"""
    current_text = st.session_state.button_data.get("main_findings", "")
    if current_text:
        # Apply template substitution to existing text
        refreshed_text = substitute_template_variables(current_text, st.session_state.form_data)
        st.session_state.button_data["main_findings"] = refreshed_text



def add_claims_validity_yes():
    st.session_state.button_data["claims_validity_scope"] += get_verification_scope_text("claims_validity", "yes", form_data=st.session_state.form_data) + "\n"
    # Update progress tracking
    update_completion_status()
    st.session_state["claims_validity_input"] = st.session_state.button_data["claims_validity_scope"]
    st.rerun()

def add_claims_validity_no():
    st.session_state.button_data["claims_validity_scope"] += get_verification_scope_text("claims_validity", "no", form_data=st.session_state.form_data) + "\n"
    # Update progress tracking
    update_completion_status()
    st.session_state["claims_validity_input"] = st.session_state.button_data["claims_validity_scope"]
    st.rerun()

def add_objective_1_yes():
    st.session_state.button_data["objective_1_comment"] += get_objective_text("objective_1_employer_exists", "yes") + "\n"
    # Update progress tracking
    update_completion_status()
    st.session_state["objective_1_input"] = st.session_state.button_data["objective_1_comment"]
    st.rerun()

def add_objective_1_no():
    st.session_state.button_data["objective_1_comment"] += get_objective_text("objective_1_employer_exists", "no") + "\n"
    # Update progress tracking
    update_completion_status()
    st.session_state["objective_1_input"] = st.session_state.button_data["objective_1_comment"]
    st.rerun()

def add_objective_2_yes():
    st.session_state.button_data["objective_2_comment"] += get_objective_text("objective_2_employee_validity", "yes") + "\n"
    # Update progress tracking
    update_completion_status()
    st.session_state["objective_2_input"] = st.session_state.button_data["objective_2_comment"]
    st.rerun()

def add_objective_2_no():
    st.session_state.button_data["objective_2_comment"] += get_objective_text("objective_2_employee_validity", "no") + "\n"
    # Update progress tracking
    update_completion_status()
    st.session_state["objective_2_input"] = st.session_state.button_data["objective_2_comment"]
    st.rerun()

def add_objective_3_yes():
    st.session_state.button_data["objective_3_comment"] += get_objective_text("objective_3_payment_accuracy", "yes") + "\n"
    # Update progress tracking
    update_completion_status()
    st.session_state["objective_3_input"] = st.session_state.button_data["objective_3_comment"]
    st.rerun()

def add_objective_3_no():
    st.session_state.button_data["objective_3_comment"] += get_objective_text("objective_3_payment_accuracy", "no") + "\n"
    # Update progress tracking
    update_completion_status()
    st.session_state["objective_3_input"] = st.session_state.button_data["objective_3_comment"]
    st.rerun()

def add_objective_4_yes():
    st.session_state.button_data["objective_4_comment"] += get_objective_text("objective_4_funds_reached_beneficiaries", "yes") + "\n"
    # Update progress tracking
    update_completion_status()
    st.session_state["objective_4_input"] = st.session_state.button_data["objective_4_comment"]
    st.rerun()

def add_objective_4_no():
    st.session_state.button_data["objective_4_comment"] += get_objective_text("objective_4_funds_reached_beneficiaries", "no") + "\n"
    # Update progress tracking
    update_completion_status()
    st.session_state["objective_4_input"] = st.session_state.button_data["objective_4_comment"]
    st.rerun()

def add_objective_5_yes():
    st.session_state.button_data["objective_5_comment"] += get_objective_text("objective_5_information_validity", "yes") + "\n"
    # Update progress tracking
    update_completion_status()
    st.session_state["objective_5_input"] = st.session_state.button_data["objective_5_comment"]
    st.rerun()

def add_objective_5_no():
    st.session_state.button_data["objective_5_comment"] += get_objective_text("objective_5_information_validity", "no") + "\n"
    # Update progress tracking
    update_completion_status()
    st.session_state["objective_5_input"] = st.session_state.button_data["objective_5_comment"]
    st.rerun()

# Function to auto-calculate financial fields (from original app.py)
def auto_calculate_financials(amount_verified_accurate):
    try:
        if amount_verified_accurate and amount_verified_accurate != "":
            # Extract numeric value from amount verified as accurate
            if isinstance(amount_verified_accurate, str):
                # Remove "R " prefix and convert to float
                amount_str = amount_verified_accurate.replace("R ", "").replace(",", "")
                amount_verified_accurate_value = float(amount_str)
            else:
                amount_verified_accurate_value = float(amount_verified_accurate)
            
            # Get total amount verified from session state
            total_verified_str = st.session_state.form_data.get("Total_Amount_Verified", "R 0.00")
            total_verified_value = float(total_verified_str.replace("R ", "").replace(",", ""))
            
            # Calculate amount not disbursed
            amount_not_disbursed_value = total_verified_value - amount_verified_accurate_value
            
            # Calculate percentage
            if total_verified_value > 0:
                percentage_value = (amount_verified_accurate_value / total_verified_value) * 100
            else:
                percentage_value = 0
            
            # Update session state with calculated values
            st.session_state.form_data["Amount_not_Disbursed"] = f"R {amount_not_disbursed_value:.2f}"
            st.session_state.form_data["Verified_Percentage"] = f"{percentage_value:.2f}%"
            
            # Auto-set affected employees to 0 if percentage is 100%
            if abs(percentage_value - 100.0) < 0.01:
                st.session_state.form_data["Affected_Employees"] = "0"
            
            return True
    except (ValueError, TypeError):
        return False
    return False

# ============================================================================
# SECTION 1: COMPANY DETAILS
# ============================================================================
st.header("Company Details")
wv = st.session_state.get('widget_version', 0)
st.info("**Basic company information and details about the employer applying for TERS funds.**")

with st.form(key="form_company_details"):
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("📝 **Name of Employer** (requires input)")
        name_of_employer = st.text_input(
            "Name of Employer", 
            value=st.session_state.form_data.get("Name_of_Employer", ""),
            key=f"name_of_employer_input_{wv}"
        )
        
        st.markdown("📝 **UIF Registration Number** (requires input)")
        uif_reg_number = st.text_input(
            "UIF Registration Number", 
            value=st.session_state.form_data.get("UIF_REG_Number", ""),
            key=f"uif_reg_number_input_{wv}"
        )
        
        st.markdown("📝 **Period Claimed For / Lockdown Period** (requires input)")
        lockdown_period = st.text_input(
            "Period Claimed For / Lockdown Period", 
            value=st.session_state.form_data.get("Period_Claimed_For_Lockdown_Period", ""),
            key=f"lockdown_period_input_{wv}"
        )
        
        # Check if address was auto-populated
        current_address = st.session_state.form_data.get("Location_Type_address_in_full", "")
        address_auto_populated = bool(current_address and current_address.strip())
        
        if address_auto_populated:
            st.markdown("📍 **Location (Full Address)** (auto-populated from address book - editable)")
            st.info(f"✅ Auto-populated from address book for UIF {st.session_state.form_data.get('UIF_REG_Number', '')}")
        else:
            st.markdown("📝 **Location (Full Address)** (requires input)")
        
        location = st.text_input(
            "Location (Full Address)", 
            value=current_address,
            key=f"location_input_{wv}",
            help="This field is automatically populated from the address book when a data file is uploaded, but you can edit it if needed."
        )
    
    with col2:
        # Check if province was auto-populated
        current_province = st.session_state.form_data.get("Province", "")
        province_auto_populated = bool(current_province and current_province.strip())
        
        if province_auto_populated:
            st.markdown("📍 **Province** (auto-populated from address book - editable)")
            st.info(f"✅ Auto-populated from address book for UIF {st.session_state.form_data.get('UIF_REG_Number', '')}")
        else:
            st.markdown("📝 **Province** (requires input)")
        
        province_options = [
            "",
            "Eastern Cape",
            "Free State", 
            "Gauteng",
            "KwaZulu-Natal",
            "Limpopo",
            "Mpumalanga",
            "Northern Cape",
            "North West",
            "Western Cape"
        ]
        province = st.selectbox(
            "Province", 
            province_options, 
            index=province_options.index(current_province) if current_province in province_options else 0,
            key=f"province_input_{wv}",
            help="This field is automatically populated from the address book when a data file is uploaded, but you can edit it if needed."
        )
        
        st.markdown("📝 **Industry** (requires input)")
        industry = st.text_input(
            "Industry", 
            value=st.session_state.form_data.get("Industry", ""),
            key=f"industry_input_{wv}"
        )
        
        st.markdown("📝 **Number of Employees** (requires input)")
        number_of_employees = st.text_input(
            "Number of Employees", 
            value=st.session_state.form_data.get("Number_of_Employees", ""),
            key=f"number_of_employees_input_{wv}"
        )
    
    col_save_company, col_indicator_company = st.columns([3, 1])
    with col_save_company:
        if st.form_submit_button("Save Company Details"):
            st.session_state.form_data.update({
                "Name_of_Employer": name_of_employer,
                "UIF_REG_Number": uif_reg_number,
                "Period_Claimed_For_Lockdown_Period": lockdown_period,
                "Location_Type_address_in_full": location,
                "Province": province,
                "Industry": industry,
                "Number_of_Employees": number_of_employees
            })
            # Auto-refresh overall outcomes if they exist
            if st.session_state.button_data.get("overall_outcomes"):
                refresh_overall_outcomes()
            # Auto-refresh main findings if they exist
            if st.session_state.button_data.get("main_findings"):
                refresh_main_findings()
            # Update progress tracking
            update_completion_status()
            st.success("Company details saved!")
    with col_indicator_company:
        if all([
            st.session_state.form_data.get("Name_of_Employer", ""),
            st.session_state.form_data.get("UIF_REG_Number", ""),
            st.session_state.form_data.get("Location_Type_address_in_full", ""),
            st.session_state.form_data.get("Period_Claimed_For_Lockdown_Period", "")
        ]):
            st.success("(Saved)")

# ============================================================================
# SECTION 2: FINANCIALS
# ============================================================================
st.header("Financials")
st.info("**Financial verification details including amounts claimed, paid, and verification results.**")

with st.form(key="form_financials"):
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("📝 **Total Amount Verified** (requires input)")
        total_amount_verified = st.text_input(
            "Total Amount Verified (e.g., R 32236.05)", 
            value=st.session_state.form_data.get("Total_Amount_Verified", ""),
            key=f"total_amount_verified_input_{wv}"
        )
        
        st.markdown("📝 **Amount Verified as Accurate** (requires input)")
        amount_verified_accurate = st.text_input(
            "Amount Verified as Accurate (Sum of Monthly Amounts Paid)", 
            value=st.session_state.form_data.get("Amount_Verified_as_Accurate", ""),
            key=f"amount_verified_accurate_input_{wv}"
        )
        
        st.markdown("📝 **Affected Employees** (requires input)")
        affected_employees = st.text_input(
            "Affected Employees (for underpayments)", 
            value=st.session_state.form_data.get("Affected_Employees", ""),
            key=f"affected_employees_input_{wv}"
        )
    
    with col2:
        st.markdown("📋 **Amount Not Disbursed** (auto-calculated)")
        amount_not_disbursed = st.text_input(
            "Amount Not Disbursed", 
            value=st.session_state.form_data.get("Amount_not_Disbursed", ""),
            disabled=True,
            key=f"amount_not_disbursed_input_{wv}"
        )
        
        # Show calculation status
        if st.session_state.form_data.get("Amount_Verified_as_Accurate") and st.session_state.form_data.get("Total_Amount_Verified"):
            st.info("💡 Auto-calculated based on your inputs above")
        
        st.markdown("📋 **Verified Percentage** (auto-calculated)")
        verified_percentage = st.text_input(
            "Verified Percentage", 
            value=st.session_state.form_data.get("Verified_Percentage", ""),
            disabled=True,
            key=f"verified_percentage_input_{wv}"
        )
        
        # Show calculation status
        if st.session_state.form_data.get("Amount_Verified_as_Accurate") and st.session_state.form_data.get("Total_Amount_Verified"):
            st.info("💡 Auto-calculated based on your inputs above")
    
    # Show real-time calculation preview
    if total_amount_verified and amount_verified_accurate:
        try:
            # Extract numeric values for preview
            total_str = total_amount_verified.replace("R ", "").replace(",", "")
            accurate_str = amount_verified_accurate.replace("R ", "").replace(",", "")
            
            if total_str and accurate_str:
                total_val = float(total_str)
                accurate_val = float(accurate_str)
                
                if total_val > 0:
                    not_disbursed = total_val - accurate_val
                    percentage = (accurate_val / total_val) * 100
                    
                    st.info(f"📊 **Calculation Preview:** Amount Not Disbursed: R {not_disbursed:.2f}, Verified Percentage: {percentage:.2f}%")
        except (ValueError, TypeError):
            pass
    
    col_save_financials, col_indicator_financials = st.columns([3, 1])
    with col_save_financials:
        if st.form_submit_button("Save Financials"):
            # Update form data first
            st.session_state.form_data.update({
                "Total_Amount_Verified": total_amount_verified,
                "Amount_Verified_as_Accurate": amount_verified_accurate,
                "Affected_Employees": affected_employees
            })
            
            # Auto-calculate financial fields using the function
            if auto_calculate_financials(amount_verified_accurate):
                # Auto-refresh overall outcomes if they exist
                if st.session_state.button_data.get("overall_outcomes"):
                    refresh_overall_outcomes()
                # Auto-refresh main findings if they exist
                if st.session_state.button_data.get("main_findings"):
                    refresh_main_findings()
                # Update progress tracking
                update_completion_status()
                st.success("Financials saved and calculated!")
                # Force a rerun to update the auto-calculated fields
                st.rerun()
            else:
                st.warning("Could not calculate financial fields. Please ensure amounts are valid numbers.")
                # Update progress tracking even if calculation fails
                update_completion_status()
                st.success("Financials saved!")
    with col_indicator_financials:
        if all([
            st.session_state.form_data.get("Total_Amount_Verified", ""),
            st.session_state.form_data.get("Amount_Verified_as_Accurate", ""),
            st.session_state.form_data.get("Affected_Employees", "")
        ]):
            st.success("(Saved)")

# ============================================================================
# SECTION 3: MONTHLY CLAIMS & EMPLOYEE PAYMENTS
# ============================================================================
st.header("📊 Monthly Claims & Employee Payments")
st.info("**Monthly claims are automatically calculated from your uploaded datafile. The claimed amount (greyed out) shows what UIF paid, while the payment amount field is editable to show what the employer actually paid to employees.**")
st.info("📊 **Progress Note**: Monthly data progress only counts months with actual claims (not N/A). Progress starts at 0% and updates to 100% only after you click 'Save All Monthly Payments' below.")

# Get active months with claims
def get_active_months(session_state_data):
    """Group active months with claims for better UX organization"""
    active_months = []
    months = ['January', 'February', 'March', 'April', 'May', 'June', 
              'July', 'August', 'September', 'October', 'November', 'December']
    
    # Map month names to form field keys
    month_field_mapping = {
        'January': {'claim_key': 'Jan_2021', 'payment_key': 'Jan_20211'},
        'February': {'claim_key': 'Feb_2021', 'payment_key': 'Feb_20211'},
        'March': {'claim_key': 'Mar_2021', 'payment_key': 'Mar_20211'},
        'April': {'claim_key': 'April_2020_Indicate_NA_where_no_claim_', 'payment_key': 'April_2020_Indicate_NA_where_no_paymen'},
        'May': {'claim_key': 'May_2020', 'payment_key': 'May_20201'},
        'June': {'claim_key': 'June_2020', 'payment_key': 'June_20201'},
        'July': {'claim_key': 'July_2020', 'payment_key': 'July_20201'},
        'August': {'claim_key': 'Aug_2020', 'payment_key': 'Aug_20201'},
        'September': {'claim_key': 'Sep_2020', 'payment_key': 'Sep_20201'},
        'October': {'claim_key': 'Oct_2020', 'payment_key': 'Oct_20201'},
        'November': {'claim_key': 'Nov_2020', 'payment_key': 'Nov_20201'},
        'December': {'claim_key': 'Dec_2020', 'payment_key': 'Dec_20201'}
    }
    
    # Add 2021 months that aren't in the mapping
    month_field_mapping.update({
        'April_2021': {'claim_key': 'Apr_2021', 'payment_key': 'Apr_20211'},
        'May_2021': {'claim_key': 'May_2021', 'payment_key': 'May_20211'},
        'June_2021': {'claim_key': 'Jun_2021', 'payment_key': 'Jun_20211'},
        'July_2021': {'claim_key': 'July_2021', 'payment_key': 'July_20211'}
    })
    
    for month in months:
        # Handle both 2020 and 2021 months
        for year in ['2020', '2021']:
            if year == '2021' and month in ['January', 'February', 'March']:
                month_key = month
            elif year == '2020' and month in ['April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']:
                month_key = month
            elif year == '2021' and month in ['April', 'May', 'June', 'July']:
                month_key = f"{month}_{year}"
            else:
                continue
                
            if month_key in month_field_mapping:
                claim_key = month_field_mapping[month_key]['claim_key']
                payment_key = month_field_mapping[month_key]['payment_key']
                claim_amount = session_state_data.get(claim_key, "N/A")
                
                if claim_amount != "N/A" and claim_amount != "":
                    active_months.append({
                        'name': f"{month} {year}",
                        'claim_amount': claim_amount,
                        'claim_key': claim_key,
                        'payment_key': payment_key,
                        'month_key': month_key
                    })
    
    return active_months

# Get active months with claims
active_months = get_active_months(st.session_state.form_data)

if not active_months:
    st.warning("⚠️ No monthly claims found. Please upload a datafile with claim information.")
else:
    st.success(f"✅ Found {len(active_months)} month(s) with claims")
    st.info("💡 **Tip**: Payment amounts are auto-populated with claim amounts since employers typically pay employees what they received from UIF. You can adjust if needed.**")
    
    # Create a container for better organization
    with st.container():
        # Implementation pattern for monthly sections with perfect alignment
        for month_data in active_months:
            with st.expander(f"📅 {month_data['name']}", expanded=True):
                # Create a clean row layout with both values side by side
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    st.write("💰 **Amount Claimed from UIF:**")
                    # Show claimed amount as read-only (greyed out)
                    st.text_input(
                        "Claimed Amount",
                        value=month_data['claim_amount'],
                        disabled=True,
                        key=f"claimed_{month_data['claim_key']}",
                        label_visibility="collapsed"
                    )
                
                with col2:
                    st.write("💳 **Payment to Employees:**")
                    # Editable payment amount field
                    current_payment = st.session_state.form_data.get(month_data['payment_key'], "")
                    if not current_payment or current_payment == "":
                        # Auto-populate with claim amount if empty
                        claim_amount_clean = month_data['claim_amount'].replace("R ", "").replace(",", "")
                        st.session_state.form_data[month_data['payment_key']] = f"R {claim_amount_clean}"
                        current_payment = f"R {claim_amount_clean}"
                    
                    payment_amount = st.text_input(
                        "Payment Amount",
                        value=current_payment,
                        key=f"payment_{month_data['payment_key']}",
                        label_visibility="collapsed",
                        placeholder="Enter payment amount..."
                    )
                    # Store the payment amount
                    st.session_state.form_data[month_data['payment_key']] = payment_amount
    
    # Single save button for all monthly payments with improved styling
    if active_months:
        st.markdown("---")
        
        # Progress indicator
        if st.session_state.get('monthly_payments_saved', False):
            st.success("✅ Monthly payments have been saved - progress updated!")
        else:
            st.info("💡 **Click 'Save All Monthly Payments' below to update your form completion progress**")
        
        # Show current progress info
        total_monthly_fields = count_total_fields('monthly_data')
        if total_monthly_fields > 0:
            st.info(f"📊 **Progress Info**: {len(active_months)} month(s) with claims found. Progress will be calculated based on actual claim months only.")
        
        # Full width save button
        if st.button("💾 Save All Monthly Payments", key="save_all_monthly_payments", type="primary", use_container_width=True):
            # Save all payment amounts
            for month_data in active_months:
                payment_key = month_data['payment_key']
                payment_amount = st.session_state.form_data.get(payment_key, "")
                st.session_state.form_data[payment_key] = payment_amount
            
            # Mark monthly payments as saved and update progress
            st.session_state.monthly_payments_saved = True
            update_completion_status()
            
            st.success(f"✅ All {len(active_months)} monthly payments saved successfully!")
        
        # Status indicator
        all_saved = all(
            st.session_state.form_data.get(month_data['payment_key'], "") and 
            st.session_state.form_data.get(month_data['payment_key'], "") != ""
            for month_data in active_months
        )
        
        if all_saved:
            st.success("✅ All Monthly Payments Saved")
        else:
            st.warning("⚠️ Some payments not saved")

# ============================================================================
# SECTION 4: MAIN FINDINGS (Button Approach)
# ============================================================================
st.header("🔍 Main Findings")
st.info("**Documents the key findings and issues discovered during the verification process.**")

# Add refresh button for main findings
if st.button("🔄 Refresh Main Findings with Current Form Data", key="refresh_main_findings", use_container_width=True):
    refresh_main_findings()
    # Update progress tracking
    update_completion_status()
    st.success("Main findings refreshed with current form data!")
    st.rerun()

# Button row with consistent styling - full width and evenly distributed
col1, col2 = st.columns(2)
with col1:
    if st.button("💰 Underpayments", key="pos_finding", use_container_width=True):
        add_main_findings_positive()
        # Update progress tracking
        update_completion_status()
with col2:
    if st.button("👥 Ineligible Employee(s)", key="neg_finding", use_container_width=True):
        add_main_findings_negative()
        # Update progress tracking
        update_completion_status()

with st.form(key="form_main_findings"):
    st.session_state.button_data["main_findings"] = st.text_area(
        "Edit Main Findings", 
        value=st.session_state.button_data["main_findings"], 
        height=120, 
        key="main_findings_input",
        placeholder="Enter your main findings here..."
    )
    
    # Save button and status indicator
    col_save1, col_indicator1 = st.columns([3, 1])
    with col_save1:
        if st.form_submit_button("💾 Save Main Findings"):
            st.session_state.saved['main_findings'] = True
            # Update progress tracking
            update_completion_status()
            st.success("Main findings saved!")
    with col_indicator1:
        if st.session_state.saved["main_findings"]:
            st.success("✅ Saved")
        else:
            st.warning("⚠️ Unsaved")

# Live preview section removed for cleaner interface

# ============================================================================
# SECTION 5: LIMITATION OF SCOPE (Button Approach)
# ============================================================================
st.header("⚠️ Limitation of Scope")
st.info("**Documents any limitations or constraints that prevented complete verification of certain aspects.**")

# Button row with consistent styling - full width and evenly distributed
col3, col4, col5, col6 = st.columns(4)
with col3:
    if st.button("📋 No Bank Statements", key="lim1", use_container_width=True):
        add_limitation_1()
        # Update progress tracking
        update_completion_status()
with col4:
    if st.button("📋 No Contracts/IRP5s/IDs", key="lim2", use_container_width=True):
        add_limitation_2()
        # Update progress tracking
        update_completion_status()
with col5:
    if st.button("📋 No Payroll/Payslips", key="lim3", use_container_width=True):
        add_limitation_3()
        # Update progress tracking
        update_completion_status()
with col6:
    if st.button("📋 No EMP501/201", key="lim4", use_container_width=True):
        add_limitation_4()
        # Update progress tracking
        update_completion_status()

with st.form(key="form_limitation"):
    st.session_state.button_data["limitation_of_scope"] = st.text_area(
        "Edit Limitation of Scope", 
        value=st.session_state.button_data["limitation_of_scope"], 
        height=120, 
        key="limitation_input",
        placeholder="Enter limitations of scope here..."
    )
    
    # Save button and status indicator
    col_save2, col_indicator2 = st.columns([3, 1])
    with col_save2:
        if st.form_submit_button("💾 Save Limitation of Scope"):
            st.session_state.saved['limitation_of_scope'] = True
            # Update progress tracking
            update_completion_status()
            st.success("Limitation of scope saved!")
    with col_indicator2:
        if st.session_state.saved["limitation_of_scope"]:
            st.success("✅ Saved")
        else:
            st.warning("⚠️ Unsaved")

# ============================================================================
# SECTION 6: INDIVIDUAL FINDINGS
# ============================================================================
st.header("📋 Individual Findings")
st.info("**Document specific findings with ratings and page references for detailed reporting.**")

# Individual findings management - each finding has its own remove button

# Display findings with improved styling
for i, finding in enumerate(st.session_state.findings):
    # Define specific headings for the first 3 findings
    if i == 0:
        heading = "🔍 No IRP5s/IDs/Contracts"
    elif i == 1:
        heading = "🔍 No Bank Statements"
    elif i == 2:
        heading = "🔍 No EMP501/201"
    else:
        heading = f"🔍 Finding {i+1}"
    
    with st.expander(heading, expanded=True):
        with st.form(key=f"form_finding_{i}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("📝 **Description** *")
                finding["description"] = st.text_area(
                    f"Description {i+1}", 
                    value=finding["description"], 
                    key=f"desc_{i}",
                    height=120,
                    placeholder="Enter finding description here..."
                )
                
                st.write("📊 **Rating** *")
                finding["rating"] = st.selectbox(
                    f"Rating {i+1}", 
                    ["", "Critical", "Significant", "Minor", "Insignificant"], 
                    index=["", "Critical", "Significant", "Minor", "Insignificant"].index(finding["rating"]) if finding["rating"] else 0, 
                    key=f"rating_{i}"
                )
            
            with col2:
                st.write("📄 **Page Reference** *")
                finding["page_ref"] = st.text_input(
                    f"Page Reference {i+1}", 
                    value=finding["page_ref"], 
                    key=f"page_{i}",
                    placeholder="e.g., TP.1, Page 5"
                )
            
            # Save button and status indicator
            col_save_finding, col_indicator_finding = st.columns([3, 1])
            with col_save_finding:
                if st.form_submit_button(f"💾 Save Finding {i+1}"):
                    st.success(f"Finding {i+1} saved!")
            with col_indicator_finding:
                if finding["description"] and finding["rating"] and finding["page_ref"]:
                    st.success("✅ Saved")
                else:
                    st.warning("⚠️ Unsaved")
        
        # Remove button at the bottom outside the form
        col_remove_bottom = st.columns([3, 1])
        with col_remove_bottom[1]:
            # Remove button always visible
            if st.button(f"🗑️ Remove Finding {i+1}", key=f"remove_finding_{i}", use_container_width=True):
                st.session_state.findings.pop(i)
                st.success(f"Finding {i+1} removed!")
                st.rerun()

# Add new finding button at the bottom
st.markdown("---")  # Add a separator line
if st.button("➕ Add New Finding", key="add_new_finding", use_container_width=True):
    st.session_state.findings.append({"description": "", "rating": "", "page_ref": ""})
    st.rerun()

# ============================================================================
# SECTION 6: COMPLIANCE WITH UI ACT
# ============================================================================
st.header("⚖️ Compliance with UI Act")
st.info("**Tests whether the employer complied with UIF Act and Contributions Act requirements.**")

with st.form(key="form_compliance_ui_act"):
    st.write("📝 **Does the employer comply with UI Act and Contributions Act** *")
    
    compliance_with_ui_act = st.selectbox(
        "Select compliance status", 
        ["", "Yes", "No"], 
        index=["", "Yes", "No"].index(st.session_state.form_data.get("Compliance", "")) if st.session_state.form_data.get("Compliance", "") in ["", "Yes", "No"] else 0,
        key="compliance_ui_act_input"
    )
    
    # Auto-populate compliance comment based on selection
    if compliance_with_ui_act == "Yes":
        default_comment = "The necessary documents to confirm compliance with UI Act"
    elif compliance_with_ui_act == "No":
        default_comment = "The necessary documents to confirm compliance with UI Act were not provided"
    else:
        default_comment = st.session_state.form_data.get("Compliance_with_UI_Act_Provide_comments", "")
    
    st.write("📝 **Compliance Comment**")
    compliance_comment = st.text_area(
        "Provide detailed comment about compliance status",
        value=default_comment,
        key="compliance_comment_input",
        placeholder="Enter detailed compliance comment here...",
        height=100
    )
    
    st.write("📋 **Compliance Documents List**")
    
    compliance_documents_list = st.text_input(
        "Enter comma-separated list of compliance documents (e.g., IRP5s, payslips, contracts)",
        value=st.session_state.form_data.get("Compliance_Documents_List", "N/A"),
        key="compliance_documents_list_input",
        placeholder="N/A"
    )
    
    # Save button and status indicator
    col_save_compliance_ui, col_indicator_compliance_ui = st.columns([3, 1])
    with col_save_compliance_ui:
        if st.form_submit_button("💾 Save Compliance with UI Act"):
            st.session_state.form_data.update({
                "Compliance": compliance_with_ui_act,  # Template expects {{Compliance}}
                "Compliance_with_UI_Act_Provide_comments": compliance_comment,  # Template expects {{Compliance_with_UI_Act_Provide_comments}}
                "Compliance_Documents_List": compliance_documents_list,  # Template expects {{Compliance_Documents_List}}
            })
            # Update progress tracking
            update_completion_status()
            st.success("Compliance with UI Act saved!")
    with col_indicator_compliance_ui:
        if st.session_state.form_data.get("Compliance"):
            st.success("✅ Saved")
        else:
            st.warning("⚠️ Unsaved")

# ============================================================================
# SECTION 7: COMPLIANCE COMMENTS (Button Approach)
# ============================================================================
st.header("📝 Compliance Comments")
st.info("**Tests whether the employer complied with UIF Act and Contributions Act requirements.**")

# Button row with consistent styling - full width and evenly distributed
col6, col7 = st.columns(2)
with col6:
    if st.button("✅ Add Compliance YES", key="comp_yes", use_container_width=True):
        add_compliance_yes()
with col7:
    if st.button("❌ Add Compliance NO", key="comp_no", use_container_width=True):
        add_compliance_no()

with st.form(key="form_compliance"):
    st.session_state.button_data["compliance_comments"] = st.text_area(
        "Edit Compliance Comments", 
        value=st.session_state.button_data["compliance_comments"], 
        height=120, 
        key="compliance_input",
        placeholder="Enter compliance comments here..."
    )
    
    # Save button and status indicator
    col_save3, col_indicator3 = st.columns([3, 1])
    with col_save3:
        if st.form_submit_button("💾 Save Compliance Comments"):
            st.session_state.saved['compliance_comments'] = True
            # Update progress tracking
            update_completion_status()
            st.success("Compliance comments saved!")
    with col_indicator3:
        if st.session_state.saved["compliance_comments"]:
            st.success("✅ Saved")
        else:
            st.warning("⚠️ Unsaved")

# ============================================================================
# SECTION 8: FRAUD AND OVERPAYMENTS
# ============================================================================
st.header("🚨 Fraud and Overpayments")
st.info("**Identifies potential fraud indicators and overpayments in the TERS claims.**")

with st.form(key="form_fraud_overpayments"):
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("🚨 **Possible Fraud Indicators** *")
        possible_fraud = st.selectbox(
            "Select fraud indicator status", 
            ["", "Yes", "No"], 
            index=["", "Yes", "No"].index(st.session_state.form_data.get("Possible_Fraud_Fraud_Indicators_YesNo1", "")) if st.session_state.form_data.get("Possible_Fraud_Fraud_Indicators_YesNo1", "") in ["", "Yes", "No"] else 0,
            key="possible_fraud_input"
        )
    
    with col2:
        st.write("💰 **Overpayments Identified** *")
        overpayments_identified = st.selectbox(
            "Select overpayment status", 
            ["", "Yes", "No"], 
            index=["", "Yes", "No"].index(st.session_state.form_data.get("Overpayments_Identified_YesNo1", "")) if st.session_state.form_data.get("Overpayments_Identified_YesNo1", "") in ["", "Yes", "No"] else 0,
            key="overpayments_identified_input"
        )
    
    # Save button and status indicator
    col_save_fraud, col_indicator_fraud = st.columns([3, 1])
    with col_save_fraud:
        if st.form_submit_button("💾 Save Fraud and Overpayments"):
            st.session_state.form_data.update({
                "Possible_Fraud_Fraud_Indicators_YesNo1": possible_fraud,
                "Overpayments_Identified_YesNo1": overpayments_identified
            })
            # Update progress tracking
            update_completion_status()
            st.success("Fraud and overpayments saved!")
    with col_indicator_fraud:
        if st.session_state.form_data.get("Possible_Fraud_Fraud_Indicators_YesNo1") and st.session_state.form_data.get("Overpayments_Identified_YesNo1"):
            st.success("✅ Saved")
        else:
            st.warning("⚠️ Unsaved")



# ============================================================================
# SECTION 10: PAYMENT VERIFICATION SCOPE (Button Approach)
# ============================================================================
st.header("💳 Payment Verification Scope")
st.info("**Tests whether the employer received and disbursed the correct amounts from UIF to employees.**")

# Button layout - 2 rows with positive on left, negative on right
col10, col11 = st.columns(2)

with col10:
    st.write("**Positive Comments:**")
    if st.button("✅ Correctly Received", key="pay_ver_yes_1", use_container_width=True):
        st.session_state.button_data["payment_verification_scope"] += get_verification_scope_text("payment_verification", "yes", 0, st.session_state.form_data) + "\n"
        # Update progress tracking
        update_completion_status()
        st.session_state["payment_verification_input"] = st.session_state.button_data["payment_verification_scope"]
        st.rerun()
    if st.button("✅ Correctly Disbursed", key="pay_ver_yes_2", use_container_width=True):
        st.session_state.button_data["payment_verification_scope"] += get_verification_scope_text("payment_verification", "yes", 1, st.session_state.form_data) + "\n"
        # Update progress tracking
        update_completion_status()
        st.session_state["payment_verification_input"] = st.session_state.button_data["payment_verification_scope"]
        st.rerun()

with col11:
    st.write("**Negative Comments:**")
    if st.button("❌ Incorrectly Received", key="pay_ver_no_1", use_container_width=True):
        st.session_state.button_data["payment_verification_scope"] += get_verification_scope_text("payment_verification", "no", 0, st.session_state.form_data) + "\n"
        # Update progress tracking
        update_completion_status()
        st.session_state["payment_verification_input"] = st.session_state.button_data["payment_verification_scope"]
        st.rerun()
    if st.button("❌ Incorrectly Disbursed", key="pay_ver_no_2", use_container_width=True):
        st.session_state.button_data["payment_verification_scope"] += get_verification_scope_text("payment_verification", "no", 1, st.session_state.form_data) + "\n"
        # Update progress tracking
        update_completion_status()
        st.session_state["payment_verification_input"] = st.session_state.button_data["payment_verification_scope"]
        st.rerun()

with st.form(key="form_payment_verification"):
    st.session_state.button_data["payment_verification_scope"] = st.text_area(
        "Edit Payment Verification Scope", 
        value=st.session_state.button_data["payment_verification_scope"], 
        height=120, 
        key="payment_verification_input",
        placeholder="Enter payment verification scope here..."
    )
    
    # Save button and status indicator
    col_save5, col_indicator5 = st.columns([3, 1])
    with col_save5:
        if st.form_submit_button("💾 Save Payment Verification Scope"):
            st.session_state.saved['payment_verification_scope'] = True
            # Update progress tracking
            update_completion_status()
            st.success("Payment verification scope saved!")
    with col_indicator5:
        if st.session_state.saved["payment_verification_scope"]:
            st.success("✅ Saved")
        else:
            st.warning("⚠️ Unsaved")

# ============================================================================
# SECTION 11: EMPLOYMENT VERIFICATION SCOPE (Button Approach)
# ============================================================================
st.header("👥 Employment Verification Scope")
st.info("**Tests whether the employees claimed for were actually employed and eligible for TERS benefits.**")

# Button layout - 2 rows with positive on left, negative on right
col14, col15 = st.columns(2)

with col14:
    st.write("**Positive Comments:**")
    if st.button("✅ Employment Confirmed", key="emp_ver_yes_1", use_container_width=True):
        st.session_state.button_data["employment_verification_scope"] += get_verification_scope_text("employment_verification", "yes", 0, st.session_state.form_data) + "\n"
        # Update progress tracking
        update_completion_status()
        st.session_state["employment_verification_input"] = st.session_state.button_data["employment_verification_scope"]
        st.rerun()
    if st.button("✅ Pre-Lockdown Verified", key="emp_ver_yes_2", use_container_width=True):
        st.session_state.button_data["employment_verification_scope"] += get_verification_scope_text("employment_verification", "yes", 1, st.session_state.form_data) + "\n"
        # Update progress tracking
        update_completion_status()
        st.session_state["employment_verification_input"] = st.session_state.button_data["employment_verification_scope"]
        st.rerun()

with col15:
    st.write("**Negative Comments:**")
    if st.button("❌ Employment Not Confirmed", key="emp_ver_no_1", use_container_width=True):
        st.session_state.button_data["employment_verification_scope"] += get_verification_scope_text("employment_verification", "no", 0, st.session_state.form_data) + "\n"
        # Update progress tracking
        update_completion_status()
        st.session_state["employment_verification_input"] = st.session_state.button_data["employment_verification_scope"]
        st.rerun()
    if st.button("❌ Pre-Lockdown Not Verified", key="emp_ver_no_2", use_container_width=True):
        st.session_state.button_data["employment_verification_scope"] += get_verification_scope_text("employment_verification", "no", 1, st.session_state.form_data) + "\n"
        # Update progress tracking
        update_completion_status()
        st.session_state["employment_verification_input"] = st.session_state.button_data["employment_verification_scope"]
        st.rerun()

with st.form(key="form_employment_verification"):
    st.session_state.button_data["employment_verification_scope"] = st.text_area(
        "Edit Employment Verification Scope", 
        value=st.session_state.button_data["employment_verification_scope"], 
        height=120, 
        key="employment_verification_input",
        placeholder="Enter employment verification scope here..."
    )
    
    # Save button and status indicator
    col_save6, col_indicator6 = st.columns([3, 1])
    with col_save6:
        if st.form_submit_button("💾 Save Employment Verification Scope"):
            st.session_state.saved['employment_verification_scope'] = True
            # Update progress tracking
            update_completion_status()
            st.success("Employment verification scope saved!")
    with col_indicator6:
        if st.session_state.saved["employment_verification_scope"]:
            st.success("✅ Saved")
        else:
            st.warning("⚠️ Unsaved")

# ============================================================================
# SECTION 12: CLAIMS VALIDITY SCOPE (Button Approach)
# ============================================================================
st.header("📋 Claims Validity Scope")
st.info("**Tests whether the UIF claims submitted were accurate and valid according to fund guidelines.**")

# Button row with consistent styling - full width and evenly distributed
col14, col15 = st.columns(2)
with col14:
    if st.button("✅ Claims Valid", key="claims_yes", use_container_width=True):
        add_claims_validity_yes()
with col15:
    if st.button("❌ Claims Invalid", key="claims_no", use_container_width=True):
        add_claims_validity_no()

with st.form(key="form_claims_validity"):
    st.session_state.button_data["claims_validity_scope"] = st.text_area(
        "Edit Claims Validity Scope", 
        value=st.session_state.button_data["claims_validity_scope"], 
        height=120, 
        key="claims_validity_input",
        placeholder="Enter claims validity scope here..."
    )
    
    # Save button and status indicator
    col_save7, col_indicator7 = st.columns([3, 1])
    with col_save7:
        if st.form_submit_button("💾 Save Claims Validity Scope"):
            st.session_state.saved['claims_validity_scope'] = True
            # Update progress tracking
            update_completion_status()
            st.success("Claims validity scope saved!")
    with col_indicator7:
        if st.session_state.saved["claims_validity_scope"]:
            st.success("✅ Saved")
        else:
            st.warning("⚠️ Unsaved")

# ============================================================================
# SECTION 13: OBJECTIVE 1 - EMPLOYER EXISTS (Button Approach)
# ============================================================================
st.header("🎯 Objective 1 - Employer Exists")
st.info("**Tests whether the employer who applied for COVID19 TERS funds actually exists as a business entity.**")

# Button row with consistent styling - full width and evenly distributed
col16, col17 = st.columns(2)
with col16:
    if st.button("✅ Add Objective 1 YES", key="obj1_yes", use_container_width=True):
        add_objective_1_yes()
with col17:
    if st.button("❌ Add Objective 1 NO", key="obj1_no", use_container_width=True):
        add_objective_1_no()

with st.form(key="form_objective_1"):
    st.session_state.button_data["objective_1_comment"] = st.text_area(
        "Edit Objective 1 Comment", 
        value=st.session_state.button_data["objective_1_comment"], 
        height=120, 
        key="objective_1_input",
        placeholder="Enter Objective 1 comment here..."
    )
    
    # Save button and status indicator
    col_save8, col_indicator8 = st.columns([3, 1])
    with col_save8:
        if st.form_submit_button("💾 Save Objective 1"):
            st.session_state.saved['objective_1_comment'] = True
            # Update progress tracking
            update_completion_status()
            st.success("Objective 1 saved!")
    with col_indicator8:
        if st.session_state.saved["objective_1_comment"]:
            st.success("✅ Saved")
        else:
            st.warning("⚠️ Unsaved")

# ============================================================================
# SECTION 14: OBJECTIVE 2 - EMPLOYEE VALIDITY (Button Approach)
# ============================================================================
st.header("🎯 Objective 2 - Employee Validity")
st.info("**Tests whether the employment of the employees applied for was valid and legitimate.**")

# Button row with consistent styling - full width and evenly distributed
col18, col19 = st.columns(2)
with col18:
    if st.button("✅ Add Objective 2 YES", key="obj2_yes", use_container_width=True):
        add_objective_2_yes()
with col19:
    if st.button("❌ Add Objective 2 NO", key="obj2_no", use_container_width=True):
        add_objective_2_no()

with st.form(key="form_objective_2"):
    st.session_state.button_data["objective_2_comment"] = st.text_area(
        "Edit Objective 2 Comment", 
        value=st.session_state.button_data["objective_2_comment"], 
        height=120, 
        key="objective_2_input",
        placeholder="Enter Objective 2 comment here..."
    )
    
    # Save button and status indicator
    col_save9, col_indicator9 = st.columns([3, 1])
    with col_save9:
        if st.form_submit_button("💾 Save Objective 2"):
            st.session_state.saved['objective_2_comment'] = True
            # Update progress tracking
            update_completion_status()
            st.success("Objective 2 saved!")
    with col_indicator9:
        if st.session_state.saved["objective_2_comment"]:
            st.success("✅ Saved")
        else:
            st.warning("⚠️ Unsaved")

# ============================================================================
# SECTION 15: OBJECTIVE 3 - PAYMENT ACCURACY (Button Approach)
# ============================================================================
st.header("🎯 Objective 3 - Payment Accuracy")
st.info("**Tests whether the accuracy of the payments made by the fund to the employer were correct.**")

# Button row with consistent styling - full width and evenly distributed
col20, col21 = st.columns(2)
with col20:
    if st.button("✅ Add Objective 3 YES", key="obj3_yes", use_container_width=True):
        add_objective_3_yes()
with col21:
    if st.button("❌ Add Objective 3 NO", key="obj3_no", use_container_width=True):
        add_objective_3_no()

with st.form(key="form_objective_3"):
    st.session_state.button_data["objective_3_comment"] = st.text_area(
        "Edit Objective 3 Comment", 
        value=st.session_state.button_data["objective_3_comment"], 
        height=120, 
        key="objective_3_input",
        placeholder="Enter Objective 3 comment here..."
    )
    
    # Save button and status indicator
    col_save10, col_indicator10 = st.columns([3, 1])
    with col_save10:
        if st.form_submit_button("💾 Save Objective 3"):
            st.session_state.saved['objective_3_comment'] = True
            # Update progress tracking
            update_completion_status()
            st.success("Objective 3 saved!")
    with col_indicator10:
        if st.session_state.saved["objective_3_comment"]:
            st.success("✅ Saved")
        else:
            st.warning("⚠️ Unsaved")

# ============================================================================
# SECTION 16: OBJECTIVE 4 - FUNDS REACHED BENEFICIARIES (Button Approach)
# ============================================================================
st.header("🎯 Objective 4 - Funds Reached Beneficiaries")
st.info("**Tests whether the COVID19 TERS funds actually reached the intended employee beneficiaries.**")

# Button row with consistent styling - full width and evenly distributed
col22, col23 = st.columns(2)
with col22:
    if st.button("✅ Add Objective 4 YES", key="obj4_yes", use_container_width=True):
        add_objective_4_yes()
with col23:
    if st.button("❌ Add Objective 4 NO", key="obj4_no", use_container_width=True):
        add_objective_4_no()

with st.form(key="form_objective_4"):
    st.session_state.button_data["objective_4_comment"] = st.text_area(
        "Edit Objective 4 Comment", 
        value=st.session_state.button_data["objective_4_comment"], 
        height=120, 
        key="objective_4_input",
        placeholder="Enter Objective 4 comment here..."
    )
    
    # Save button and status indicator
    col_save11, col_indicator11 = st.columns([3, 1])
    with col_save11:
        if st.form_submit_button("💾 Save Objective 4"):
            st.session_state.saved['objective_4_comment'] = True
            # Update progress tracking
            update_completion_status()
            st.success("Objective 4 saved!")
    with col_indicator11:
        if st.session_state.saved["objective_4_comment"]:
            st.success("✅ Saved")
        else:
            st.warning("⚠️ Unsaved")

# ============================================================================
# SECTION 17: OBJECTIVE 5 - INFORMATION VALIDITY (Button Approach)
# ============================================================================
st.header("🎯 Objective 5 - Information Validity")
st.info("**Tests whether the information submitted to the fund was accurate and valid according to MOA guidelines.**")

# Button row with consistent styling - full width and evenly distributed
col24, col25 = st.columns(2)
with col24:
    if st.button("✅ Add Objective 5 YES", key="obj5_yes", use_container_width=True):
        add_objective_5_yes()
with col25:
    if st.button("❌ Add Objective 5 NO", key="obj5_no", use_container_width=True):
        add_objective_5_no()

with st.form(key="form_objective_5"):
    st.session_state.button_data["objective_5_comment"] = st.text_area(
        "Edit Objective 5 Comment", 
        value=st.session_state.button_data["objective_5_comment"], 
        height=120, 
        key="objective_5_input",
        placeholder="Enter Objective 5 comment here..."
    )
    
    # Save button and status indicator
    col_save12, col_indicator12 = st.columns([3, 1])
    with col_save12:
        if st.form_submit_button("💾 Save Objective 5"):
            st.session_state.saved['objective_5_comment'] = True
            # Update progress tracking
            update_completion_status()
            st.success("Objective 5 saved!")
    with col_indicator12:
        if st.session_state.saved["objective_5_comment"]:
            st.success("✅ Saved")
        else:
            st.warning("⚠️ Unsaved")

# ============================================================================
# SECTION 18: OVERALL OUTCOMES (Button Approach)
# ============================================================================
st.header("📊 Overall Outcomes")
st.info("**Summarizes the overall results of the verification process and whether the employer met all requirements.**")



# Add refresh button
if st.button("🔄 Refresh with Current Form Data", key="refresh_outcomes", use_container_width=True):
    refresh_overall_outcomes()
    # Update progress tracking
    update_completion_status()
    st.success("Overall outcomes refreshed with current form data!")
    st.rerun()

# Button grid layout - 3 positive buttons on left, 3 negative buttons on right
col8, col9 = st.columns(2)

with col8:
    st.write("**Positive Outcomes:**")
    if st.button("✅ Payment Accuracy - Positive", key="outcomes_payment_pos", use_container_width=True):
        st.session_state.button_data["overall_outcomes"] += get_overall_outcome_text("positive", "payment_accuracy", st.session_state.form_data) + "\n"
        # Update progress tracking
        update_completion_status()
        st.session_state["overall_outcomes_input"] = st.session_state.button_data["overall_outcomes"]
        st.rerun()
    
    if st.button("✅ Employment Verification - Positive", key="outcomes_employment_pos", use_container_width=True):
        st.session_state.button_data["overall_outcomes"] += get_overall_outcome_text("positive", "employment_verification", st.session_state.form_data) + "\n"
        # Update progress tracking
        update_completion_status()
        st.session_state["overall_outcomes_input"] = st.session_state.button_data["overall_outcomes"]
        st.rerun()
    
    if st.button("✅ Documentation - Positive", key="outcomes_documentation_pos", use_container_width=True):
        st.session_state.button_data["overall_outcomes"] += get_overall_outcome_text("positive", "documentation", st.session_state.form_data) + "\n"
        # Update progress tracking
        update_completion_status()
        st.session_state["overall_outcomes_input"] = st.session_state.button_data["overall_outcomes"]
        st.rerun()

with col9:
    st.write("**Negative Outcomes:**")
    if st.button("❌ Payment Accuracy - Negative", key="outcomes_payment_neg", use_container_width=True):
        st.session_state.button_data["overall_outcomes"] += get_overall_outcome_text("negative", "payment_accuracy", st.session_state.form_data) + "\n"
        # Update progress tracking
        update_completion_status()
        st.session_state["overall_outcomes_input"] = st.session_state.button_data["overall_outcomes"]
        st.rerun()
    
    if st.button("❌ Employment Verification - Negative", key="outcomes_employment_neg", use_container_width=True):
        st.session_state.button_data["overall_outcomes"] += get_overall_outcome_text("negative", "employment_verification", st.session_state.form_data) + "\n"
        # Update progress tracking
        update_completion_status()
        st.session_state["overall_outcomes_input"] = st.session_state.button_data["overall_outcomes"]
        st.rerun()
    
    if st.button("❌ Documentation - Negative", key="outcomes_documentation_neg", use_container_width=True):
        st.session_state.button_data["overall_outcomes"] += get_overall_outcome_text("negative", "documentation", st.session_state.form_data) + "\n"
        # Update progress tracking
        update_completion_status()
        st.session_state["overall_outcomes_input"] = st.session_state.button_data["overall_outcomes"]
        st.rerun()

with st.form(key="form_overall_outcomes"):
    st.session_state.button_data["overall_outcomes"] = st.text_area(
        "Edit Overall Outcomes", 
        value=st.session_state.button_data["overall_outcomes"], 
        height=120, 
        key="overall_outcomes_input",
        placeholder="Enter overall outcomes here..."
    )
    
    # Save button and status indicator
    col_save4, col_indicator4 = st.columns([3, 1])
    with col_save4:
        if st.form_submit_button("💾 Save Overall Outcomes"):
            st.session_state.saved['overall_outcomes'] = True
            # Update progress tracking
            update_completion_status()
            st.success("Overall outcomes saved!")
    with col_indicator4:
        if st.session_state.saved["overall_outcomes"]:
            st.success("✅ Saved")
        else:
            st.warning("⚠️ Unsaved")

# Preview section removed for cleaner interface

# Final submission to join all forms
if st.button("Final Submit"):
    # Combine all the button data into the form_data structure
    combined_data = {
        "Main_Findings": st.session_state.button_data["main_findings"],
        "Limitation_of_scope": st.session_state.button_data["limitation_of_scope"],
        "Compliance_Comments": st.session_state.button_data["compliance_comments"],
        "Overall_Outcomes": st.session_state.button_data["overall_outcomes"],
        "Payment_Verification_Scope": st.session_state.button_data["payment_verification_scope"],
        "Employment_Verification_Scope": st.session_state.button_data["employment_verification_scope"],
        "Claims_Validity_Scope": st.session_state.button_data["claims_validity_scope"],
        "Objective_1_Comment": st.session_state.button_data["objective_1_comment"],
        "Objective_2_Comment": st.session_state.button_data["objective_2_comment"],
        "Objective_3_Comment": st.session_state.button_data["objective_3_comment"],
        "Objective_4_Comment": st.session_state.button_data["objective_4_comment"],
        "Objective_5_Comment": st.session_state.button_data["objective_5_comment"]
    }
    
    # Update form_data with combined data
    st.session_state.form_data.update(combined_data)
    
    # Handle findings
    for i, finding in enumerate(st.session_state.findings, 1):
        st.session_state.form_data[f"Finding_{i}"] = finding["description"]
        st.session_state.form_data[f"Finding_{i}_Rating"] = finding["rating"]
        st.session_state.form_data[f"Finding_{i}_Page"] = finding["page_ref"] or f"TP.{i+1}"
    
    # Add all monthly data fields
    monthly_claim_fields = {
        "April_2020_Indicate_NA_where_no_claim_": st.session_state.form_data.get("April_2020_Indicate_NA_where_no_claim_", ""),
        "May_2020": st.session_state.form_data.get("May_2020", ""),
        "June_2020": st.session_state.form_data.get("June_2020", ""),
        "July_2020": st.session_state.form_data.get("July_2020", ""),
        "Aug_2020": st.session_state.form_data.get("Aug_2020", ""),
        "Sep_2020": st.session_state.form_data.get("Sep_2020", ""),
        "Oct_2020": st.session_state.form_data.get("Oct_2020", ""),
        "Nov_2020": st.session_state.form_data.get("Nov_2020", ""),
        "Dec_2020": st.session_state.form_data.get("Dec_2020", ""),
        "Jan_2021": st.session_state.form_data.get("Jan_2021", ""),
        "Feb_2021": st.session_state.form_data.get("Feb_2021", ""),
        "Mar_2021": st.session_state.form_data.get("Mar_2021", ""),
        "Apr_2021": st.session_state.form_data.get("Apr_2021", ""),
        "May_2021": st.session_state.form_data.get("May_2021", ""),
        "Jun_2021": st.session_state.form_data.get("Jun_2021", ""),
        "July_2021": st.session_state.form_data.get("July_2021", "")
    }
    
    monthly_payment_fields = {
        "April_2020_Indicate_NA_where_no_paymen": st.session_state.form_data.get("April_2020_Indicate_NA_where_no_paymen", ""),
        "May_20201": st.session_state.form_data.get("May_20201", ""),
        "June_20201": st.session_state.form_data.get("June_20201", ""),
        "July_20201": st.session_state.form_data.get("July_20201", ""),
        "Aug_20201": st.session_state.form_data.get("Aug_20201", ""),
        "Sep_20201": st.session_state.form_data.get("Sep_20201", ""),
        "Oct_20201": st.session_state.form_data.get("Oct_20201", ""),
        "Nov_20201": st.session_state.form_data.get("Nov_20201", ""),
        "Dec_20201": st.session_state.form_data.get("Dec_20201", ""),
        "Jan_20211": st.session_state.form_data.get("Jan_20211", ""),
        "Feb_20211": st.session_state.form_data.get("Feb_20211", ""),
        "Mar_20211": st.session_state.form_data.get("Mar_20211", ""),
        "Apr_20211": st.session_state.form_data.get("Apr_20211", ""),
        "May_20211": st.session_state.form_data.get("May_20211", ""),
        "Jun_20211": st.session_state.form_data.get("Jun_20211", ""),
        "July_20211": st.session_state.form_data.get("July_20211", "")
    }
    
    # Update form_data with monthly fields
    st.session_state.form_data.update(monthly_claim_fields)
    st.session_state.form_data.update(monthly_payment_fields)
    
    # Add default values for required fields if not present
    if "Name_of_Employer" not in st.session_state.form_data:
        st.session_state.form_data["Name_of_Employer"] = "Sample Employer"
    if "UIF_REG_Number" not in st.session_state.form_data:
        st.session_state.form_data["UIF_REG_Number"] = "123456789"
    if "Location_Type_address_in_full" not in st.session_state.form_data:
        st.session_state.form_data["Location_Type_address_in_full"] = "Sample Address"
    if "Period_Claimed_For_Lockdown_Period" not in st.session_state.form_data:
        st.session_state.form_data["Period_Claimed_For_Lockdown_Period"] = "March 2020 to April 2020"
    
    # Add compliance field for template compatibility
    if "Compliance_Comments" in st.session_state.form_data:
        st.session_state.form_data["Compliance"] = "Yes" if "accurate" in st.session_state.form_data["Compliance_Comments"].lower() else "No"
    
    # Populate Iteration_* fields, Iteration_total, and Gaps for template
    iteration_counts = st.session_state.get('iteration_counts', [])
    # Map iterations 1..16
    for idx in range(16):
        key = f"Iteration_{idx+1}"
        st.session_state.form_data[key] = str(iteration_counts[idx]) if idx < len(iteration_counts) else "0"
    st.session_state.form_data["Iteration_total"] = str(sum(iteration_counts)) if iteration_counts else "0"
    st.session_state.form_data["Gaps"] = st.session_state.get('gaps_flag', "No")

    # Ensure Finding_3 and Finding_3_Rating exist (template expects them)
    if "Finding_3" not in st.session_state.form_data:
        st.session_state.form_data["Finding_3"] = st.session_state.form_data.get("Finding_3", "")
    if "Finding_3_Rating" not in st.session_state.form_data:
        st.session_state.form_data["Finding_3_Rating"] = st.session_state.form_data.get("Finding_3_Rating", "")

    # Auto-calculate financial fields if amount verified as accurate is provided
    amount_verified_accurate = st.session_state.form_data.get("Amount_Verified_as_Accurate", "")
    if amount_verified_accurate and amount_verified_accurate != "":
        try:
            # Extract numeric value from amount verified as accurate
            if isinstance(amount_verified_accurate, str):
                amount_str = amount_verified_accurate.replace("R ", "").replace(",", "")
                amount_verified_accurate_value = float(amount_str)
            else:
                amount_verified_accurate_value = float(amount_verified_accurate)
            
            # Get total amount verified from session state
            total_verified_str = st.session_state.form_data.get("Total_Amount_Verified", "R 0.00")
            total_verified_value = float(total_verified_str.replace("R ", "").replace(",", ""))
            
            # Calculate amount not disbursed
            amount_not_disbursed_value = total_verified_value - amount_verified_accurate_value
            
            # Calculate percentage
            if total_verified_value > 0:
                percentage_value = (amount_verified_accurate_value / total_verified_value) * 100
            else:
                percentage_value = 0
            
            # Update form data with calculated values
            st.session_state.form_data["Amount_not_Disbursed"] = f"R {amount_not_disbursed_value:.2f}"
            st.session_state.form_data["Verified_Percentage"] = f"{percentage_value:.2f}%"
            
            # Auto-set affected employees to 0 if percentage is 100%
            if abs(percentage_value - 100.0) < 0.01:
                st.session_state.form_data["Affected_Employees"] = "0"
                st.info("Verified percentage is 100% - Affected Employees automatically set to 0")
                
        except (ValueError, TypeError):
            st.warning("Could not calculate financial fields. Please ensure amounts are valid numbers.")
    
    # Generate report
    try:
        st.subheader("Combined Data for Template")
        st.json(st.session_state.form_data)

        generator = ReportGenerator(template_path)
        output_path = generator.generate_report(st.session_state.form_data)
        st.session_state.output_path = output_path
        st.success(f"Report generated: {output_path}")
    except Exception as e:
        st.error(f"Error generating report: {str(e)}")
        st.session_state.output_path = None

# Download button
if st.session_state.output_path and os.path.exists(st.session_state.output_path):
    with open(st.session_state.output_path, "rb") as file:
        st.download_button(
            label="Download Report",
            data=file,
            file_name=f"{st.session_state.form_data.get('Name_of_Employer', 'report').replace(' ', '_')}_report.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

def add_objective_5_no():
    st.session_state.button_data["objective_5_comment"] += get_objective_text("objective_5_information_validity", "no") + "\n"
