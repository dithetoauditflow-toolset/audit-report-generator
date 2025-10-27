"""
Example Edits for UIF Report Generator Configuration

This file shows examples of common edits you might want to make to the copy_paste_text.py file.
Copy these examples and modify them as needed, then paste them into the appropriate sections
of config/copy_paste_text.py

IMPORTANT: This is just an example file. Make actual changes in copy_paste_text.py
"""

# =============================================================================
# EXAMPLE 1: Adding a New Finding
# =============================================================================

# In the FINDINGS section, add this to the "main_findings" dictionary:
"""
"finding_3": "• The employer failed to maintain proper records of employee payments during the lockdown period."
"""

# =============================================================================
# EXAMPLE 2: Modifying Existing Finding Text
# =============================================================================

# Replace the existing finding_1 text with this:
"""
"finding_1": "• The employer has under-paid {employee_count} employees over all claim periods. The total underpayments amounted to R{amount}."
"""

# =============================================================================
# EXAMPLE 3: Adding a New Limitation
# =============================================================================

# In the FINDINGS section, add this to the "limitations" dictionary:
"""
"limitation_4": "• We could not verify the accuracy of employee ID numbers as the employer did not provide original ID documents.",
"limitation_5": "• The employer's payroll system was offline during the verification period, limiting our ability to cross-reference payment data."
"""

# =============================================================================
# EXAMPLE 4: Customizing Compliance Text
# =============================================================================

# Replace the existing compliance text with more specific versions:
"""
"ui_act_compliance": {
    "yes": "• The employer provided us with the required documents that confirmed their UIF Contributions were accurate and not in arrears as of the verification date.",
    "no": "• The employer did not provide us with the required documents that confirmed their UIF Contributions were accurate and not in arrears. Outstanding contributions were identified.",
    "partial": "• The employer provided partial documentation for UIF Contributions, but some periods could not be verified due to missing records."
}
"""

# =============================================================================
# EXAMPLE 5: Adding Industry-Specific Text
# =============================================================================

# Add industry-specific findings to the FINDINGS section:
"""
"industry_specific": {
    "retail": "• The retail sector employer failed to maintain proper employee attendance records during the lockdown period.",
    "manufacturing": "• The manufacturing employer could not provide evidence of production shutdown during the claimed periods.",
    "services": "• The service sector employer did not maintain proper client billing records to support the claimed business impact."
}
"""

# =============================================================================
# EXAMPLE 6: Customizing Monthly Amount Helper Text
# =============================================================================

# Modify the monthly amounts helper text:
"""
MONTHLY_AMOUNTS = {
    "helper_text": "💡 **Amount to pay: {amount}** (click to copy)",
    "no_claim_text": "N/A",
    "partial_payment_text": "💡 **Partial payment: {amount}** (click to copy)",
    "overpayment_text": "⚠️ **Overpayment: {amount}** (click to copy)"
}
"""

# =============================================================================
# EXAMPLE 7: Adding New Verification Scope Options
# =============================================================================

# Add new verification scope options:
"""
"documentation_verification": {
    "yes": "• All required documentation was provided and verified as accurate and complete.",
    "no": "• Required documentation was missing or incomplete, preventing full verification.",
    "partial": "• Some required documentation was provided, but key documents were missing."
}
"""

# =============================================================================
# EXAMPLE 8: Customizing UI Text
# =============================================================================

# Modify UI text for different languages or contexts:
"""
UI_TEXT = {
    "sections": {
        "company_details": "Company Details",
        "financials": "Financial Information",
        "findings": "Audit Findings",
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
        "copyable": "💡 **{field_name}** (click to copy)",
        "warning": "⚠️ **{field_name}** (requires attention)"
    }
}
"""

# =============================================================================
# EXAMPLE 9: Adding Conditional Text Based on Amount
# =============================================================================

# Add a function to get conditional text based on amount:
"""
def get_conditional_finding_text(amount_verified, amount_accurate):
    if amount_verified == amount_accurate:
        return "• All verified amounts were accurately paid to employees."
    elif amount_accurate == 0:
        return "• No verified amounts were paid to employees."
    else:
        return f"• Only R{amount_accurate} of R{amount_verified} was paid to employees."
"""

# =============================================================================
# EXAMPLE 10: Adding Date-Specific Text
# =============================================================================

# Add date-specific text for different lockdown periods:
"""
LOCKDOWN_PERIODS = {
    "level_5": "• During Level 5 lockdown (27 March to 30 April 2020), the employer was required to cease all operations.",
    "level_4": "• During Level 4 lockdown (1 May to 31 May 2020), the employer was permitted limited operations.",
    "level_3": "• During Level 3 lockdown (1 June to 17 August 2020), the employer was permitted expanded operations."
}
"""

# =============================================================================
# HOW TO APPLY THESE EXAMPLES
# =============================================================================

"""
To apply any of these examples:

1. Open config/copy_paste_text.py in a text editor
2. Find the appropriate section (FINDINGS, COMPLIANCE, etc.)
3. Copy the example code you want to use
4. Paste it into the correct location in the file
5. Modify the text as needed for your specific use case
6. Save the file
7. Restart the UIF Report Generator application

Remember to:
- Maintain proper Python syntax
- Keep the dictionary structure intact
- Test your changes by restarting the application
- Make backups before making significant changes
"""
