"""
UIF Report Generator - Copy-Paste Ready Text Configuration

This file contains all the predefined text templates that users can copy and paste
into the UIF report generator. The text is organized by sections for easy editing.

To edit any text, simply modify the corresponding string in this file.
The application will automatically load these changes when restarted.

Structure:
- FINDINGS: Text for main findings and limitations
- COMPLIANCE: Text for compliance-related comments
- OVERALL_OUTCOMES: Text for overall outcomes and summaries
- VERIFICATION_SCOPES: Text for various verification scopes
- OBJECTIVES: Text for the 5 main objectives
- MONTHLY_AMOUNTS: Helper text for monthly amounts
"""

# =============================================================================
# MAIN FINDINGS SECTION
# =============================================================================

FINDINGS = {
    "main_findings": {
        "finding_1": "• The employer has under-paid {{affected_employees}} employees over all claim periods. The total underpayments amounted to {{amount_not_disbursed}}.",
        "finding_2": "• The employer has claimed for {{affected_employees}} employees that were ineligible to be claimed for. {{affected_employees}} being the number employees affected and {{amount_not_disbursed}} being the amount not disbursed."
    },
    
    "limitations": {
        "limitation_1": "• We cannot verify the accuracy of the amounts received by the employer from the Fund as the employer did not submit the bank statements reflecting TERS funds received.",
        "limitation_2": "• We could not perform employment verification procedures as the employer did not submit employees' contract of employment/ IRP5s and ID copies for some/all employees.",
        "limitation_3": "• We could not verify that the employees claimed for where employed in the 3 months before the lockdown as the necessary payroll/payslip documents were not provided.",
        "limitation_4": "• We could not confirm that the UIF contributions of the employer are accurate and not in arrears as we did not receive EMP501/201 or payroll data detailing their monthly UIF contributions/declaration."
    }
}

# =============================================================================
# COMPLIANCE SECTION
# =============================================================================

COMPLIANCE = {
    "ui_act_compliance": {
        "yes": "The necessary documents to confirm compliance with UI Act were provided.",
        "no": "The necessary documents to confirm compliance with UI Act were not provided."
    }
}

# =============================================================================
# OVERALL OUTCOMES SECTION
# =============================================================================

OVERALL_OUTCOMES = {
    "positive": {
        "payment_accuracy": "• The employer paid all {{employee_count}} employees accurately across all claimed periods. The total amount paid out to employees was {{verified_amount}}.",
        "employment_verification": "• We verified the employment of all {{employee_count}} employees.",
        "documentation": "• The employer provided us with all required supporting documents."
    },
    
    "negative": {
        "payment_accuracy": "• The employer did not pay all {{employee_count}} employees accurately across all claimed periods. The total amount paid out to employees was {{verified_amount}}, with {{affected_employees}} being the number employees affected and {{verified_amount}} being the amount verified as accurate.",
        "employment_verification": "• We could not verify the employment of all {{employee_count}} employees.",
        "documentation": "• The employer did not provide us with all required supporting documents."
    }
}

# =============================================================================
# VERIFICATION SCOPES SECTION
# =============================================================================

VERIFICATION_SCOPES = {
    "payment_verification": {
        "yes": [
            "• During payments verification testing we could confirm that the funds detailed on the UIF payment schedule is the amount the employer received according to their bank statement(s).",
            "• During the review of bank statement, it was noted that {{verified_amount}} was accurately disbursed to the beneficiaries."
        ],
        "no": [
            "• During the payments verification testing, we noted that the fund sent {{total_verified}} and we could confirm that the employer received {{verified_amount}}.",
            "• All the necessary bank statements were not provided, leading us to conclude that {{amount_not_disbursed}} was not disbursed to the qualifying employees."
        ]
    },
    
    "employment_verification": {
        "yes": [
            "• We inspected the provided payroll data and we could confirm that all {{employee_count}} employees claimed for were employed 3 months prior to the lockdown.",
            "• During the review of IRP5s and employment contracts, we could confirm that all {{employee_count}} employees claimed for were employed before 27 March 2020."
        ],
        "no": [
            "• During employment verification testing, the required payroll data was not provided for us to confirm that all employees claimed for were employed 3 months prior to the lockdown.",
            "• The required IRP5s and employment contracts were not provided for us to confirm that all the employees claimed for were employed before 27 March 2020."
        ]
    },
    
    "claims_validity": {
        "yes": "• During claims validity testing we could confirm that all UIF claims submitted were accurate and valid according to the fund guidelines.",
        "no": "• During claims validity testing we could not confirm that all UIF claims submitted were accurate and valid according to the fund guidelines."
    }
}

# =============================================================================
# OBJECTIVES SECTION
# =============================================================================

OBJECTIVES = {
    "objective_1_employer_exists": {
        "yes": "• Based on the work performed the employer who applied for the COVID19TERS funds exists.",
        "no": "• Based on the work performed the employer who applied for the COVID19TERS funds does not exist."
    },
    
    "objective_2_employee_validity": {
        "yes": "• Based on the work performed the employment of the employees applied for was valid.",
        "no": "• Based on the work performed the employment of the employees applied for was not valid."
    },
    
    "objective_3_payment_accuracy": {
        "yes": "• Based on the work performed the accuracy of the payments made by the fund to the employer were accurate.",
        "no": "• Based on the work performed the accuracy of the payments made by the fund to the employer were not accurate."
    },
    
    "objective_4_funds_reached_beneficiaries": {
        "yes": "• Based on the work performed the COVID19TERS funds reached the intended beneficiaries.",
        "no": "• Based on the work performed the COVID19TERS funds did not reach the intended beneficiaries."
    },
    
    "objective_5_information_validity": {
        "yes": "• Based on the work performed the information submitted to the fund by the intended recipient as per the application process in accordance with the guidelines of the MOA was accurate and valid.",
        "no": "• Based on the work performed the information submitted to the fund by the intended recipient as per the application process in accordance with the guidelines of the MOA was not accurate and valid."
    }
}

# =============================================================================
# MONTHLY AMOUNTS HELPER TEXT
# =============================================================================

MONTHLY_AMOUNTS = {
    "helper_text": "💡 **Amount to pay: {amount}** (click to copy)",
    "no_claim_text": "N/A"
}

# =============================================================================
# UI TEXT AND LABELS
# =============================================================================

UI_TEXT = {
    "sections": {
        "company_details": "Company Details",
        "financials": "Financials",
        "findings": "Findings",
        "compliance": "Compliance and Objectives"
    },
    
    "descriptions": {
        "company_details": "**Basic company information and details about the employer applying for TERS funds.**",
        "financials": "**Financial verification details including amounts claimed, paid, and verification results.**",
        "findings": "**Documents all findings, limitations, and issues discovered during the verification process.**",
        "compliance": "**Tests whether the employer complied with UIF Act and Contributions Act requirements.**"
    },
    
    "visual_indicators": {
        "required_input": "📝 **{field_name}** (requires input)",
        "auto_populated": "📋 **{field_name}** (auto-populated)",
        "copyable": "💡 **{field_name}** (click to copy)"
    }
}

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def substitute_template_variables(text, form_data):
    """
    Substitute template variables in text with actual values from form data.
    
    Args:
        text (str): Text containing template variables like {{variable_name}}
        form_data (dict): Dictionary containing form data with actual values
    
    Returns:
        str: Text with template variables substituted
    """
    if not text or not form_data:
        return text
    
    # Define the template variable mappings
    template_mappings = {
        "{{employee_count}}": form_data.get("Number_of_Employees", "XX"),
        "{{total_amount}}": form_data.get("Amount_Verified_as_Accurate", "RXXXXX"),  # Backward compatibility
        "{{affected_employees}}": form_data.get("Affected_Employees", "XX"),
        "{{company_name}}": form_data.get("Name_of_Employer", "Company"),
        "{{uif_number}}": form_data.get("UIF_REG_Number", "XXXXX"),
        "{{period}}": form_data.get("Period_Claimed_For_Lockdown_Period", "period"),
        "{{industry}}": form_data.get("Industry", "industry"),
        "{{province}}": form_data.get("Province", "province"),
        "{{total_verified}}": form_data.get("Total_Amount_Verified", "RXXXXX"),
        "{{verified_amount}}": form_data.get("Amount_Verified_as_Accurate", "RXXXXX"),
        "{{amount_not_disbursed}}": form_data.get("Amount_not_Disbursed", "RXXXXX"),
        "{{verified_percentage}}": form_data.get("Verified_Percentage", "XX%"),
        "{{Compliance_Documents_List}}": form_data.get("Compliance_Documents_List", "N/A"),
        "{{compliance_documents_list}}": form_data.get("Compliance_Documents_List", "N/A"),  # Alternative format
        "{{Compliance}}": form_data.get("Compliance_with_UI_Act_Provide_comments", "N/A"),
        "{{compliance}}": form_data.get("Compliance_with_UI_Act_Provide_comments", "N/A")  # Alternative format
    }
    
    # Replace all template variables
    substituted_text = text
    for placeholder, value in template_mappings.items():
        substituted_text = substituted_text.replace(placeholder, str(value))
    
    return substituted_text

def get_finding_text(finding_type, option=None, form_data=None):
    """
    Get finding text by type and option.
    
    Args:
        finding_type (str): Type of finding ('main_findings', 'limitations')
        option (str): Specific option (e.g., 'finding_1', 'limitation_1')
        form_data (dict): Optional form data for template variable substitution
    
    Returns:
        str: The requested text with template variables substituted if form_data provided
    """
    if finding_type in FINDINGS:
        if option and option in FINDINGS[finding_type]:
            text = FINDINGS[finding_type][option]
            # Apply template substitution if form_data is provided
            if form_data:
                text = substitute_template_variables(text, form_data)
            return text
        return FINDINGS[finding_type]
    return ""

def get_compliance_text(compliance_type, option):
    """
    Get compliance text by type and option.
    
    Args:
        compliance_type (str): Type of compliance ('ui_act_compliance')
        option (str): Specific option ('yes' or 'no')
    
    Returns:
        str: The requested text
    """
    if compliance_type in COMPLIANCE:
        if option in COMPLIANCE[compliance_type]:
            return COMPLIANCE[compliance_type][option]
    return ""

def get_overall_outcome_text(outcome_type, option, form_data=None):
    """
    Get overall outcome text by type and option.
    
    Args:
        outcome_type (str): Type of outcome ('positive' or 'negative')
        option (str): Specific option (e.g., 'payment_accuracy')
        form_data (dict): Optional form data for template variable substitution
    
    Returns:
        str: The requested text with template variables substituted if form_data provided
    """
    if outcome_type in OVERALL_OUTCOMES:
        if option in OVERALL_OUTCOMES[outcome_type]:
            text = OVERALL_OUTCOMES[outcome_type][option]
            # Apply template substitution if form_data is provided
            if form_data:
                text = substitute_template_variables(text, form_data)
            return text
    return ""

def get_verification_scope_text(scope_type, option, index=0, form_data=None):
    """
    Get verification scope text by type and option.
    
    Args:
        scope_type (str): Type of scope ('payment_verification', 'employment_verification', 'claims_validity')
        option (str): Specific option ('yes' or 'no')
        index (int): Index for lists (default 0)
        form_data (dict): Optional form data for template variable substitution
    
    Returns:
        str: The requested text with template variables substituted if form_data provided
    """
    if scope_type in VERIFICATION_SCOPES:
        if option in VERIFICATION_SCOPES[scope_type]:
            text = VERIFICATION_SCOPES[scope_type][option]
            if isinstance(text, list):
                text = text[index] if index < len(text) else text[0]
            # Apply template substitution if form_data is provided
            if form_data:
                text = substitute_template_variables(text, form_data)
            return text
    return ""

def get_objective_text(objective_type, option):
    """
    Get objective text by type and option.
    
    Args:
        objective_type (str): Type of objective (e.g., 'objective_1_employer_exists')
        option (str): Specific option ('yes' or 'no')
    
    Returns:
        str: The requested text
    """
    if objective_type in OBJECTIVES:
        if option in OBJECTIVES[objective_type]:
            return OBJECTIVES[objective_type][option]
    return ""

def get_monthly_amount_helper_text(amount):
    """
    Get helper text for monthly amounts.
    
    Args:
        amount (str): The amount to display
    
    Returns:
        str: The formatted helper text
    """
    if amount and amount != MONTHLY_AMOUNTS["no_claim_text"]:
        return MONTHLY_AMOUNTS["helper_text"].format(amount=amount)
    return ""
